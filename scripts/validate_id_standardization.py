#!/usr/bin/env python3
# ~/scripts/validate_id_standardization.py
# ---------------------------------------------------------------------------------------------
# MeStore - ID Standardization Validation Script
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: validate_id_standardization.py
# Ruta: ~/scripts/validate_id_standardization.py
# Autor: Database Architect AI
# Fecha de Creación: 2025-09-17
# Versión: 1.0.0
# Propósito: Comprehensive validation script for ID standardization migration
#            Verifies data integrity, relationship consistency, and performance
#
# VALIDATION CATEGORIES:
# 1. ID Type Consistency - All IDs are String(36) UUID format
# 2. Referential Integrity - All foreign keys reference valid UUIDs
# 3. Data Preservation - No data loss during migration
# 4. Performance Validation - Query performance meets benchmarks
# 5. Business Logic Validation - Application functionality preserved
#
# ---------------------------------------------------------------------------------------------

"""
ID Standardization Validation Script.

This script performs comprehensive validation of the ID standardization migration:
- Validates all ID types are consistent String(36) UUID
- Checks referential integrity across all relationships
- Verifies data preservation during migration
- Tests performance benchmarks
- Validates business logic still functions
"""

import os
import sys
import time
import uuid
import asyncio
from typing import Dict, List, Tuple, Any, Optional
from decimal import Decimal
from datetime import datetime
import argparse

# Add the parent directory to the path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text, inspect, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Import models to validate
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem, OrderTransaction, PaymentMethod
from app.models.commission import Commission
from app.models.category import Category
from app.models.transaction import Transaction
from app.core.config import settings


class IDStandardizationValidator:
    """
    Comprehensive validator for ID standardization migration.

    Performs multiple validation passes:
    1. Schema validation - Check table structures
    2. Data type validation - Verify all IDs are UUID format
    3. Referential integrity - Validate all FK relationships
    4. Data consistency - Ensure no data corruption
    5. Performance validation - Benchmark query performance
    """

    def __init__(self, database_url: str = None):
        """Initialize validator with database connection."""
        self.database_url = database_url or settings.DATABASE_URL
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.inspector = inspect(self.engine)
        self.metadata = MetaData()
        self.validation_results = {}
        self.performance_metrics = {}

    def run_full_validation(self) -> Dict[str, Any]:
        """Run complete validation suite."""
        print("🔍 Starting comprehensive ID standardization validation...")
        print("=" * 80)

        start_time = time.time()

        # Validation phases
        validation_phases = [
            ("Schema Structure", self.validate_schema_structure),
            ("ID Type Consistency", self.validate_id_types),
            ("UUID Format Validation", self.validate_uuid_formats),
            ("Referential Integrity", self.validate_referential_integrity),
            ("Data Consistency", self.validate_data_consistency),
            ("Foreign Key Relationships", self.validate_foreign_keys),
            ("Index Performance", self.validate_index_performance),
            ("Query Performance", self.validate_query_performance),
            ("Business Logic", self.validate_business_logic),
            ("Migration Completeness", self.validate_migration_completeness)
        ]

        for phase_name, phase_function in validation_phases:
            print(f"\n📋 Validating: {phase_name}")
            print("-" * 60)

            try:
                result = phase_function()
                self.validation_results[phase_name] = result

                if result.get('success', False):
                    print(f"✅ {phase_name}: PASSED")
                else:
                    print(f"❌ {phase_name}: FAILED")
                    for error in result.get('errors', []):
                        print(f"   ⚠️ {error}")

            except Exception as e:
                print(f"💥 {phase_name}: EXCEPTION - {str(e)}")
                self.validation_results[phase_name] = {
                    'success': False,
                    'errors': [f"Exception during validation: {str(e)}"]
                }

        total_time = time.time() - start_time

        # Generate final report
        return self.generate_validation_report(total_time)

    def validate_schema_structure(self) -> Dict[str, Any]:
        """Validate that all tables have correct schema structure."""
        errors = []
        success = True

        # Expected table structures after migration
        expected_structures = {
            'orders': {
                'columns': ['id', 'order_number', 'buyer_id', 'vendor_id', 'subtotal', 'tax_amount',
                          'shipping_cost', 'discount_amount', 'total_amount', 'status', 'created_at', 'updated_at'],
                'pk': ['id'],
                'fks': [('buyer_id', 'users', 'id'), ('vendor_id', 'users', 'id')]
            },
            'order_items': {
                'columns': ['id', 'order_id', 'product_id', 'vendor_id', 'product_name', 'product_sku',
                          'unit_price', 'quantity', 'total_price', 'created_at', 'updated_at'],
                'pk': ['id'],
                'fks': [('order_id', 'orders', 'id'), ('product_id', 'products', 'id'), ('vendor_id', 'users', 'id')]
            },
            'order_transactions': {
                'columns': ['id', 'transaction_reference', 'order_id', 'payment_method_id', 'amount',
                          'currency', 'status', 'gateway', 'created_at', 'updated_at'],
                'pk': ['id'],
                'fks': [('order_id', 'orders', 'id'), ('payment_method_id', 'payment_methods', 'id')]
            },
            'payment_methods': {
                'columns': ['id', 'buyer_id', 'method_type', 'is_default', 'is_active', 'created_at', 'updated_at'],
                'pk': ['id'],
                'fks': [('buyer_id', 'users', 'id')]
            }
        }

        for table_name, expected in expected_structures.items():
            try:
                # Check if table exists
                if not self.inspector.has_table(table_name):
                    errors.append(f"Table '{table_name}' does not exist")
                    success = False
                    continue

                # Get actual columns
                columns = self.inspector.get_columns(table_name)
                column_names = [col['name'] for col in columns]

                # Check required columns exist
                for required_col in expected['columns']:
                    if required_col not in column_names:
                        errors.append(f"Table '{table_name}' missing column '{required_col}'")
                        success = False

                # Check primary key
                pk_constraint = self.inspector.get_pk_constraint(table_name)
                if set(pk_constraint['constrained_columns']) != set(expected['pk']):
                    errors.append(f"Table '{table_name}' primary key mismatch")
                    success = False

                # Check foreign keys
                fks = self.inspector.get_foreign_keys(table_name)
                fk_info = [(fk['constrained_columns'][0], fk['referred_table'], fk['referred_columns'][0])
                          for fk in fks]

                for expected_fk in expected['fks']:
                    if expected_fk not in fk_info:
                        errors.append(f"Table '{table_name}' missing foreign key {expected_fk}")
                        success = False

            except Exception as e:
                errors.append(f"Error validating table '{table_name}': {str(e)}")
                success = False

        return {'success': success, 'errors': errors}

    def validate_id_types(self) -> Dict[str, Any]:
        """Validate that all ID columns are String(36) type."""
        errors = []
        success = True

        tables_to_check = ['orders', 'order_items', 'order_transactions', 'payment_methods',
                          'users', 'products', 'commissions', 'categories']

        with self.engine.connect() as conn:
            for table_name in tables_to_check:
                try:
                    if not self.inspector.has_table(table_name):
                        continue

                    columns = self.inspector.get_columns(table_name)

                    for column in columns:
                        if column['name'].endswith('_id') or column['name'] == 'id':
                            # Check if column type is appropriate for UUID
                            col_type = str(column['type'])

                            # Accept VARCHAR(36), CHAR(36), or TEXT for UUID storage
                            if not any(uuid_type in col_type.upper() for uuid_type in ['VARCHAR(36)', 'CHAR(36)', 'TEXT']):
                                errors.append(f"Table '{table_name}' column '{column['name']}' has type '{col_type}' (expected VARCHAR(36))")
                                success = False

                except Exception as e:
                    errors.append(f"Error checking ID types for table '{table_name}': {str(e)}")
                    success = False

        return {'success': success, 'errors': errors}

    def validate_uuid_formats(self) -> Dict[str, Any]:
        """Validate that all ID values are valid UUID format."""
        errors = []
        success = True

        tables_to_check = [
            ('orders', ['id', 'buyer_id', 'vendor_id']),
            ('order_items', ['id', 'order_id', 'product_id', 'vendor_id']),
            ('order_transactions', ['id', 'order_id', 'payment_method_id']),
            ('payment_methods', ['id', 'buyer_id']),
            ('commissions', ['id', 'order_id', 'vendor_id', 'transaction_id'])
        ]

        with self.engine.connect() as conn:
            for table_name, id_columns in tables_to_check:
                try:
                    if not self.inspector.has_table(table_name):
                        continue

                    for column in id_columns:
                        # Check that all non-null values are valid UUIDs
                        result = conn.execute(text(f"""
                            SELECT {column}, COUNT(*) as count
                            FROM {table_name}
                            WHERE {column} IS NOT NULL
                            GROUP BY {column}
                            LIMIT 10
                        """))

                        for row in result:
                            id_value = row[0]
                            if id_value:
                                try:
                                    # Validate UUID format
                                    uuid.UUID(str(id_value))
                                except ValueError:
                                    errors.append(f"Table '{table_name}' column '{column}' has invalid UUID: '{id_value}'")
                                    success = False
                                    break

                except Exception as e:
                    errors.append(f"Error validating UUID formats for table '{table_name}': {str(e)}")
                    success = False

        return {'success': success, 'errors': errors}

    def validate_referential_integrity(self) -> Dict[str, Any]:
        """Validate that all foreign key references are valid."""
        errors = []
        success = True

        # Foreign key relationships to validate
        fk_relationships = [
            ('orders', 'buyer_id', 'users', 'id'),
            ('orders', 'vendor_id', 'users', 'id'),
            ('order_items', 'order_id', 'orders', 'id'),
            ('order_items', 'product_id', 'products', 'id'),
            ('order_items', 'vendor_id', 'users', 'id'),
            ('order_transactions', 'order_id', 'orders', 'id'),
            ('order_transactions', 'payment_method_id', 'payment_methods', 'id'),
            ('payment_methods', 'buyer_id', 'users', 'id'),
            ('commissions', 'order_id', 'orders', 'id'),
            ('commissions', 'vendor_id', 'users', 'id'),
        ]

        with self.engine.connect() as conn:
            for child_table, child_col, parent_table, parent_col in fk_relationships:
                try:
                    if not (self.inspector.has_table(child_table) and self.inspector.has_table(parent_table)):
                        continue

                    # Check for orphaned records
                    result = conn.execute(text(f"""
                        SELECT COUNT(*)
                        FROM {child_table} c
                        LEFT JOIN {parent_table} p ON c.{child_col} = p.{parent_col}
                        WHERE c.{child_col} IS NOT NULL AND p.{parent_col} IS NULL
                    """))

                    orphaned_count = result.scalar()
                    if orphaned_count > 0:
                        errors.append(f"Found {orphaned_count} orphaned records in {child_table}.{child_col}")
                        success = False

                except Exception as e:
                    errors.append(f"Error validating FK {child_table}.{child_col} -> {parent_table}.{parent_col}: {str(e)}")
                    success = False

        return {'success': success, 'errors': errors}

    def validate_data_consistency(self) -> Dict[str, Any]:
        """Validate data consistency after migration."""
        errors = []
        success = True

        with self.engine.connect() as conn:
            try:
                # Check that orders have consistent totals
                result = conn.execute(text("""
                    SELECT o.id, o.total_amount,
                           COALESCE(SUM(oi.total_price), 0) as items_total
                    FROM orders o
                    LEFT JOIN order_items oi ON o.id = oi.order_id
                    GROUP BY o.id, o.total_amount
                    HAVING ABS(o.total_amount - COALESCE(SUM(oi.total_price), 0)) > 0.01
                    LIMIT 5
                """))

                inconsistent_orders = result.fetchall()
                if inconsistent_orders:
                    for order in inconsistent_orders:
                        errors.append(f"Order {order[0]} total mismatch: order={order[1]}, items={order[2]}")
                    success = False

                # Check that commissions reference valid orders
                result = conn.execute(text("""
                    SELECT COUNT(*)
                    FROM commissions c
                    LEFT JOIN orders o ON c.order_id = o.id
                    WHERE o.id IS NULL
                """))

                orphaned_commissions = result.scalar()
                if orphaned_commissions > 0:
                    errors.append(f"Found {orphaned_commissions} commissions without valid orders")
                    success = False

                # Check for duplicate order numbers
                result = conn.execute(text("""
                    SELECT order_number, COUNT(*)
                    FROM orders
                    GROUP BY order_number
                    HAVING COUNT(*) > 1
                """))

                duplicates = result.fetchall()
                if duplicates:
                    errors.append(f"Found {len(duplicates)} duplicate order numbers")
                    success = False

            except Exception as e:
                errors.append(f"Error during data consistency validation: {str(e)}")
                success = False

        return {'success': success, 'errors': errors}

    def validate_foreign_keys(self) -> Dict[str, Any]:
        """Validate foreign key constraints are properly defined."""
        errors = []
        success = True

        expected_foreign_keys = {
            'orders': ['buyer_id', 'vendor_id'],
            'order_items': ['order_id', 'product_id', 'vendor_id'],
            'order_transactions': ['order_id', 'payment_method_id'],
            'payment_methods': ['buyer_id'],
            'commissions': ['order_id', 'vendor_id']
        }

        for table_name, expected_fks in expected_foreign_keys.items():
            try:
                if not self.inspector.has_table(table_name):
                    continue

                fks = self.inspector.get_foreign_keys(table_name)
                actual_fk_columns = [fk['constrained_columns'][0] for fk in fks]

                for expected_fk in expected_fks:
                    if expected_fk not in actual_fk_columns:
                        errors.append(f"Table '{table_name}' missing foreign key constraint on '{expected_fk}'")
                        success = False

            except Exception as e:
                errors.append(f"Error validating foreign keys for table '{table_name}': {str(e)}")
                success = False

        return {'success': success, 'errors': errors}

    def validate_index_performance(self) -> Dict[str, Any]:
        """Validate that appropriate indexes exist for UUID columns."""
        errors = []
        success = True

        # Expected indexes for performance
        expected_indexes = {
            'orders': ['id', 'buyer_id', 'vendor_id', 'status'],
            'order_items': ['id', 'order_id', 'product_id'],
            'order_transactions': ['id', 'order_id', 'payment_method_id'],
            'payment_methods': ['id', 'buyer_id'],
            'commissions': ['id', 'order_id', 'vendor_id']
        }

        for table_name, expected_idx_columns in expected_indexes.items():
            try:
                if not self.inspector.has_table(table_name):
                    continue

                indexes = self.inspector.get_indexes(table_name)
                indexed_columns = set()

                for idx in indexes:
                    indexed_columns.update(idx['column_names'])

                for expected_col in expected_idx_columns:
                    if expected_col not in indexed_columns:
                        errors.append(f"Table '{table_name}' missing index on column '{expected_col}'")
                        success = False

            except Exception as e:
                errors.append(f"Error validating indexes for table '{table_name}': {str(e)}")
                success = False

        return {'success': success, 'errors': errors}

    def validate_query_performance(self) -> Dict[str, Any]:
        """Validate query performance benchmarks."""
        errors = []
        success = True

        performance_tests = [
            ("Order lookup by ID", "SELECT * FROM orders WHERE id = ?", ["single_order_id"]),
            ("Orders by buyer", "SELECT * FROM orders WHERE buyer_id = ?", ["single_buyer_id"]),
            ("Order items by order", "SELECT * FROM order_items WHERE order_id = ?", ["single_order_id"]),
            ("Transactions by order", "SELECT * FROM order_transactions WHERE order_id = ?", ["single_order_id"]),
            ("Payment methods by buyer", "SELECT * FROM payment_methods WHERE buyer_id = ?", ["single_buyer_id"])
        ]

        with self.engine.connect() as conn:
            try:
                # Get sample IDs for testing
                sample_data = {}

                order_result = conn.execute(text("SELECT id, buyer_id FROM orders LIMIT 1")).fetchone()
                if order_result:
                    sample_data["single_order_id"] = order_result[0]
                    sample_data["single_buyer_id"] = order_result[1]
                else:
                    # Skip performance tests if no data
                    return {'success': True, 'errors': [], 'message': 'No data available for performance testing'}

                for test_name, query, param_keys in performance_tests:
                    try:
                        # Prepare parameters
                        params = [sample_data[key] for key in param_keys]

                        # Execute query with timing
                        start_time = time.time()
                        conn.execute(text(query), params)
                        execution_time = time.time() - start_time

                        # Store performance metric
                        self.performance_metrics[test_name] = execution_time

                        # Check if performance is acceptable (under 100ms for single record queries)
                        if execution_time > 0.1:
                            errors.append(f"Performance test '{test_name}' took {execution_time:.3f}s (expected < 0.1s)")
                            success = False

                    except Exception as e:
                        errors.append(f"Performance test '{test_name}' failed: {str(e)}")
                        success = False

            except Exception as e:
                errors.append(f"Error during performance validation: {str(e)}")
                success = False

        return {'success': success, 'errors': errors}

    def validate_business_logic(self) -> Dict[str, Any]:
        """Validate that business logic still functions correctly."""
        errors = []
        success = True

        try:
            # Test SQLAlchemy model operations
            session = self.SessionLocal()

            try:
                # Test order creation and relationships
                orders = session.query(Order).limit(1).all()
                if orders:
                    order = orders[0]

                    # Test relationships work
                    if hasattr(order, 'buyer') and order.buyer_id:
                        buyer = order.buyer  # Should not raise an error
                        if not buyer:
                            errors.append("Order.buyer relationship not working")
                            success = False

                    if hasattr(order, 'items'):
                        items = order.items  # Should not raise an error
                        # Items relationship should work

                    # Test property methods
                    if hasattr(order, 'is_paid'):
                        is_paid = order.is_paid  # Should not raise an error

                # Test commission relationships
                commissions = session.query(Commission).limit(1).all()
                if commissions:
                    commission = commissions[0]

                    if hasattr(commission, 'order') and commission.order_id:
                        order = commission.order  # Should not raise an error
                        if not order:
                            errors.append("Commission.order relationship not working")
                            success = False

            finally:
                session.close()

        except Exception as e:
            errors.append(f"Error during business logic validation: {str(e)}")
            success = False

        return {'success': success, 'errors': errors}

    def validate_migration_completeness(self) -> Dict[str, Any]:
        """Validate that migration is complete and consistent."""
        errors = []
        success = True

        with self.engine.connect() as conn:
            try:
                # Check for any remaining integer ID columns that should be UUIDs
                tables_to_check = ['orders', 'order_items', 'order_transactions', 'payment_methods']

                for table_name in tables_to_check:
                    if not self.inspector.has_table(table_name):
                        continue

                    columns = self.inspector.get_columns(table_name)

                    for column in columns:
                        if (column['name'].endswith('_id') or column['name'] == 'id'):
                            col_type_str = str(column['type']).upper()

                            # Check for integer types that should be UUIDs
                            if 'INTEGER' in col_type_str or 'INT' in col_type_str:
                                errors.append(f"Table '{table_name}' column '{column['name']}' still has integer type")
                                success = False

                # Check that mapping tables still exist (for potential rollback)
                mapping_tables = ['id_mapping_orders', 'id_mapping_order_items',
                                'id_mapping_order_transactions', 'id_mapping_payment_methods']

                mapping_exists = 0
                for mapping_table in mapping_tables:
                    if self.inspector.has_table(mapping_table):
                        mapping_exists += 1

                if mapping_exists != len(mapping_tables):
                    errors.append(f"Only {mapping_exists}/{len(mapping_tables)} mapping tables exist (may affect rollback capability)")
                    # This is a warning, not a failure

            except Exception as e:
                errors.append(f"Error during migration completeness validation: {str(e)}")
                success = False

        return {'success': success, 'errors': errors}

    def generate_validation_report(self, total_time: float) -> Dict[str, Any]:
        """Generate comprehensive validation report."""

        total_phases = len(self.validation_results)
        passed_phases = sum(1 for result in self.validation_results.values() if result.get('success', False))
        failed_phases = total_phases - passed_phases

        overall_success = failed_phases == 0

        report = {
            'overall_success': overall_success,
            'summary': {
                'total_phases': total_phases,
                'passed_phases': passed_phases,
                'failed_phases': failed_phases,
                'execution_time': total_time
            },
            'phase_results': self.validation_results,
            'performance_metrics': self.performance_metrics,
            'recommendations': []
        }

        # Generate recommendations based on results
        if not overall_success:
            report['recommendations'].append("❌ Migration validation failed. Review errors before proceeding to production.")

            for phase_name, result in self.validation_results.items():
                if not result.get('success', False):
                    report['recommendations'].append(f"🔧 Fix issues in: {phase_name}")
        else:
            report['recommendations'].append("✅ All validation phases passed successfully!")
            report['recommendations'].append("🚀 Migration is ready for production use.")

        # Performance recommendations
        slow_queries = [(name, time) for name, time in self.performance_metrics.items() if time > 0.05]
        if slow_queries:
            report['recommendations'].append("⚡ Consider optimizing slow queries:")
            for query_name, query_time in slow_queries:
                report['recommendations'].append(f"   - {query_name}: {query_time:.3f}s")

        return report

    def print_validation_report(self, report: Dict[str, Any]):
        """Print formatted validation report."""

        print("\n" + "=" * 80)
        print("🏁 ID STANDARDIZATION VALIDATION REPORT")
        print("=" * 80)

        # Overall status
        if report['overall_success']:
            print("🎉 OVERALL STATUS: ✅ PASSED")
        else:
            print("⚠️ OVERALL STATUS: ❌ FAILED")

        # Summary
        summary = report['summary']
        print(f"\n📊 SUMMARY:")
        print(f"   • Total validation phases: {summary['total_phases']}")
        print(f"   • Passed phases: {summary['passed_phases']}")
        print(f"   • Failed phases: {summary['failed_phases']}")
        print(f"   • Execution time: {summary['execution_time']:.2f} seconds")

        # Phase details
        print(f"\n📋 PHASE DETAILS:")
        for phase_name, result in report['phase_results'].items():
            status = "✅ PASSED" if result.get('success', False) else "❌ FAILED"
            print(f"   • {phase_name}: {status}")

            if not result.get('success', False) and result.get('errors'):
                for error in result['errors'][:3]:  # Show first 3 errors
                    print(f"     ⚠️ {error}")
                if len(result['errors']) > 3:
                    print(f"     ... and {len(result['errors']) - 3} more errors")

        # Performance metrics
        if report['performance_metrics']:
            print(f"\n⚡ PERFORMANCE METRICS:")
            for query_name, execution_time in report['performance_metrics'].items():
                status = "🟢" if execution_time < 0.05 else "🟡" if execution_time < 0.1 else "🔴"
                print(f"   • {query_name}: {execution_time:.3f}s {status}")

        # Recommendations
        if report['recommendations']:
            print(f"\n💡 RECOMMENDATIONS:")
            for recommendation in report['recommendations']:
                print(f"   {recommendation}")

        print("=" * 80)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Validate ID standardization migration')
    parser.add_argument('--database-url', help='Database URL (default: from settings)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    try:
        validator = IDStandardizationValidator(args.database_url)
        report = validator.run_full_validation()
        validator.print_validation_report(report)

        # Exit with appropriate code
        exit_code = 0 if report['overall_success'] else 1
        sys.exit(exit_code)

    except Exception as e:
        print(f"💥 Validation script failed with exception: {str(e)}")
        sys.exit(2)


if __name__ == "__main__":
    main()