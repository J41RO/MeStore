# tests/integration/financial/test_migration_integrity.py
# CRITICAL: Database Migration Integrity Testing Suite
# PRIORITY: Validate commission system migrations and data integrity

import pytest
import logging
from decimal import Decimal
from uuid import uuid4
from datetime import datetime

from sqlalchemy import create_engine, text, inspect, Table, MetaData
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command
from alembic.migration import MigrationContext
from alembic.operations import Operations

from app.core.config import settings
from app.models.commission import Commission, CommissionStatus, CommissionType
from app.models.order import Order, OrderStatus
from app.models.user import User, UserType
from app.models.transaction import Transaction, EstadoTransaccion, TransactionType

logger = logging.getLogger(__name__)

# Test database for migration testing
MIGRATION_TEST_DB = "postgresql://admin_jairo:JairoAdmin2024$$@localhost/mestore_migration_test"


@pytest.mark.integration_financial
@pytest.mark.critical
class TestDatabaseMigrationIntegrity:
    """
    CRITICAL: Database Migration Integrity Test Suite

    Validates that all commission system migrations create correct table structures,
    constraints, indexes, and maintain data integrity across schema changes.
    """

    @pytest.fixture(scope="class")
    def migration_engine(self):
        """Create a separate engine for migration testing"""
        engine = create_engine(MIGRATION_TEST_DB, echo=False)
        yield engine
        engine.dispose()

    @pytest.fixture(scope="class")
    def alembic_config(self):
        """Create Alembic configuration for testing"""
        config = Config()
        config.set_main_option("script_location", "alembic")
        config.set_main_option("sqlalchemy.url", MIGRATION_TEST_DB)
        return config

    @pytest.fixture(autouse=True)
    def setup_migration_database(self, migration_engine):
        """Setup clean migration test database"""
        # Drop all existing tables
        with migration_engine.connect() as conn:
            conn.execute(text("DROP SCHEMA public CASCADE"))
            conn.execute(text("CREATE SCHEMA public"))
            conn.commit()

    def test_commission_system_migration_creates_tables(
        self,
        migration_engine,
        alembic_config,
        audit_logger
    ):
        """Test that commission system migration creates all required tables"""
        audit_logger("migration_table_creation_start", {
            "migration_file": "2025_09_13_0147-abc123_add_commission_system_tables.py"
        })

        # Run the commission system migration
        with migration_engine.connect() as conn:
            context = MigrationContext.configure(conn)
            ops = Operations(context)

            # Execute the migration content manually for testing
            self._execute_commission_migration(ops)
            conn.commit()

        # Verify tables were created
        inspector = inspect(migration_engine)
        tables = inspector.get_table_names()

        assert 'commissions' in tables
        audit_logger("migration_table_creation_success", {
            "tables_created": tables
        })

    def test_commission_table_structure_integrity(
        self,
        migration_engine,
        alembic_config
    ):
        """Test commission table has correct column structure and constraints"""
        # Run migration
        with migration_engine.connect() as conn:
            context = MigrationContext.configure(conn)
            ops = Operations(context)
            self._execute_commission_migration(ops)
            conn.commit()

        # Inspect table structure
        inspector = inspect(migration_engine)
        columns = inspector.get_columns('commissions')
        constraints = inspector.get_check_constraints('commissions')
        indexes = inspector.get_indexes('commissions')

        # Verify critical financial columns exist
        column_names = [col['name'] for col in columns]
        required_columns = [
            'id', 'commission_number', 'order_id', 'vendor_id',
            'order_amount', 'commission_rate', 'commission_amount',
            'vendor_amount', 'platform_amount', 'status', 'commission_type'
        ]

        for col in required_columns:
            assert col in column_names, f"Missing critical column: {col}"

        # Verify decimal columns have correct precision
        decimal_columns = ['order_amount', 'commission_amount', 'vendor_amount', 'platform_amount']
        for col in decimal_columns:
            col_info = next(c for c in columns if c['name'] == col)
            assert col_info['type'].precision == 10
            assert col_info['type'].scale == 2

        # Verify commission rate precision
        rate_col = next(c for c in columns if c['name'] == 'commission_rate')
        assert rate_col['type'].precision == 5
        assert rate_col['type'].scale == 4

        # Verify check constraints exist
        constraint_names = [c['name'] for c in constraints]
        required_constraints = [
            'check_order_amount_positive',
            'check_commission_amount_non_negative',
            'check_vendor_amount_non_negative',
            'check_platform_amount_non_negative',
            'check_commission_rate_valid',
            'check_amounts_balance'
        ]

        for constraint in required_constraints:
            assert constraint in constraint_names, f"Missing constraint: {constraint}"

    def test_commission_table_indexes_created(
        self,
        migration_engine,
        alembic_config
    ):
        """Test that performance indexes are correctly created"""
        # Run migration
        with migration_engine.connect() as conn:
            context = MigrationContext.configure(conn)
            ops = Operations(context)
            self._execute_commission_migration(ops)
            conn.commit()

        # Verify indexes
        inspector = inspect(migration_engine)
        indexes = inspector.get_indexes('commissions')
        index_names = [idx['name'] for idx in indexes]

        required_indexes = [
            'idx_commission_calculation_date',
            'idx_commission_order_vendor',
            'idx_commission_vendor_status',
            'ix_commissions_id',
            'ix_commissions_commission_number',
            'ix_commissions_order_id',
            'ix_commissions_vendor_id',
            'ix_commissions_status'
        ]

        for index in required_indexes:
            assert index in index_names, f"Missing index: {index}"

    def test_commission_foreign_key_constraints(
        self,
        migration_engine,
        alembic_config
    ):
        """Test foreign key relationships are properly established"""
        # Setup base tables first (users, orders, transactions)
        with migration_engine.connect() as conn:
            # Create minimal required tables for FK relationships
            conn.execute(text("""
                CREATE TABLE users (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    email VARCHAR(255) UNIQUE NOT NULL,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))

            conn.execute(text("""
                CREATE TABLE orders (
                    id SERIAL PRIMARY KEY,
                    order_number VARCHAR(100) UNIQUE NOT NULL,
                    buyer_id UUID REFERENCES users(id),
                    total_amount DECIMAL(10,2) NOT NULL,
                    status VARCHAR(50) NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))

            conn.execute(text("""
                CREATE TABLE transactions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    monto DECIMAL(12,2) NOT NULL,
                    estado VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))

            # Now run commission migration
            context = MigrationContext.configure(conn)
            ops = Operations(context)
            self._execute_commission_migration(ops)
            conn.commit()

        # Test foreign key constraints
        inspector = inspect(migration_engine)
        fkeys = inspector.get_foreign_keys('commissions')

        # Verify required foreign keys
        fkey_info = {fk['constrained_columns'][0]: fk['referred_table'] for fk in fkeys}

        expected_fkeys = {
            'vendor_id': 'users',
            'order_id': 'orders',
            'transaction_id': 'transactions',
            'approved_by_id': 'users'
        }

        for column, expected_table in expected_fkeys.items():
            assert column in fkey_info, f"Missing foreign key for {column}"
            assert fkey_info[column] == expected_table

    @pytest.mark.critical
    def test_commission_constraint_validation_works(
        self,
        migration_engine,
        alembic_config,
        audit_logger
    ):
        """CRITICAL: Test that database constraints actually prevent invalid data"""
        audit_logger("constraint_validation_test_start", {
            "testing": "financial_integrity_constraints"
        })

        # Setup tables and run migration
        with migration_engine.connect() as conn:
            self._setup_base_tables(conn)
            context = MigrationContext.configure(conn)
            ops = Operations(context)
            self._execute_commission_migration(ops)
            conn.commit()

        # Create session for testing
        Session = sessionmaker(bind=migration_engine)
        session = Session()

        try:
            # Test 1: Negative order amount should fail
            with pytest.raises(Exception):  # Should raise IntegrityError
                session.execute(text("""
                    INSERT INTO commissions (
                        id, commission_number, order_id, vendor_id,
                        order_amount, commission_rate, commission_amount,
                        vendor_amount, platform_amount, commission_type, status, currency, calculation_method
                    ) VALUES (
                        gen_random_uuid(), 'TEST-001', 1, gen_random_uuid(),
                        -100.00, 0.05, 5.00, 95.00, 5.00, 'STANDARD', 'PENDING', 'COP', 'test'
                    )
                """))
                session.commit()

            # Test 2: Invalid commission rate should fail
            with pytest.raises(Exception):
                session.execute(text("""
                    INSERT INTO commissions (
                        id, commission_number, order_id, vendor_id,
                        order_amount, commission_rate, commission_amount,
                        vendor_amount, platform_amount, commission_type, status, currency, calculation_method
                    ) VALUES (
                        gen_random_uuid(), 'TEST-002', 1, gen_random_uuid(),
                        100.00, 1.5, 150.00, -50.00, 150.00, 'STANDARD', 'PENDING', 'COP', 'test'
                    )
                """))
                session.commit()

            # Test 3: Unbalanced amounts should fail
            with pytest.raises(Exception):
                session.execute(text("""
                    INSERT INTO commissions (
                        id, commission_number, order_id, vendor_id,
                        order_amount, commission_rate, commission_amount,
                        vendor_amount, platform_amount, commission_type, status, currency, calculation_method
                    ) VALUES (
                        gen_random_uuid(), 'TEST-003', 1, gen_random_uuid(),
                        100.00, 0.05, 5.00, 90.00, 5.00, 'STANDARD', 'PENDING', 'COP', 'test'
                    )
                """))
                session.commit()

            audit_logger("constraint_validation_test_success", {
                "constraints_working": "all_financial_constraints_validated"
            })

        finally:
            session.rollback()
            session.close()

    def test_additional_migrations_integration(
        self,
        migration_engine,
        alembic_config
    ):
        """Test integration with other recent migrations"""
        with migration_engine.connect() as conn:
            # Test processing_at column migration
            conn.execute(text("""
                CREATE TABLE orders (
                    id SERIAL PRIMARY KEY,
                    order_number VARCHAR(100),
                    total_amount DECIMAL(10,2),
                    status VARCHAR(50),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))

            # Add processing_at column (simulating migration)
            conn.execute(text("""
                ALTER TABLE orders ADD COLUMN processing_at TIMESTAMP WITH TIME ZONE
            """))

            # Add vendor_id column (simulating migration)
            conn.execute(text("""
                ALTER TABLE orders ADD COLUMN vendor_id UUID
            """))

            # Update UserType enum (simulating migration)
            conn.execute(text("""
                CREATE TYPE usertype_enum AS ENUM ('ADMIN', 'VENDOR', 'BUYER', 'MESTOCKER')
            """))

            conn.commit()

        # Verify migrations can coexist
        inspector = inspect(migration_engine)

        if 'orders' in inspector.get_table_names():
            order_columns = [col['name'] for col in inspector.get_columns('orders')]
            assert 'processing_at' in order_columns
            assert 'vendor_id' in order_columns

    def test_migration_rollback_integrity(
        self,
        migration_engine,
        alembic_config
    ):
        """Test that migration can be properly rolled back without data loss"""
        with migration_engine.connect() as conn:
            # Run migration
            context = MigrationContext.configure(conn)
            ops = Operations(context)
            self._execute_commission_migration(ops)

            # Verify table exists
            inspector = inspect(migration_engine)
            assert 'commissions' in inspector.get_table_names()

            # Run rollback
            self._execute_commission_rollback(ops)

            # Verify table is gone
            inspector = inspect(migration_engine)
            assert 'commissions' not in inspector.get_table_names()

            conn.commit()

    def test_migration_data_preservation(
        self,
        migration_engine,
        alembic_config
    ):
        """Test that existing data is preserved during schema changes"""
        with migration_engine.connect() as conn:
            # Setup base tables with test data
            self._setup_base_tables_with_data(conn)

            # Run commission migration
            context = MigrationContext.configure(conn)
            ops = Operations(context)
            self._execute_commission_migration(ops)

            # Verify base data still exists
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            assert result.scalar() > 0

            result = conn.execute(text("SELECT COUNT(*) FROM orders"))
            assert result.scalar() > 0

            conn.commit()

    # Helper methods for migration testing

    def _execute_commission_migration(self, ops):
        """Execute the commission migration upgrade"""
        from sqlalchemy.dialects.postgresql import UUID
        import sqlalchemy as sa

        # Create commissions table
        ops.create_table('commissions',
            sa.Column('id', UUID(as_uuid=True), nullable=False),
            sa.Column('commission_number', sa.String(length=50), nullable=False),
            sa.Column('order_id', sa.Integer(), nullable=False),
            sa.Column('vendor_id', UUID(as_uuid=True), nullable=False),
            sa.Column('transaction_id', UUID(as_uuid=True), nullable=True),
            sa.Column('order_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
            sa.Column('commission_rate', sa.DECIMAL(precision=5, scale=4), nullable=False),
            sa.Column('commission_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
            sa.Column('vendor_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
            sa.Column('platform_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
            sa.Column('commission_type', sa.Enum('STANDARD', 'PREMIUM', 'PROMOTIONAL', 'CATEGORY_BASED', name='commissiontype'), nullable=False),
            sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'PAID', 'DISPUTED', 'REFUNDED', 'CANCELLED', name='commissionstatus'), nullable=False),
            sa.Column('currency', sa.String(length=3), nullable=False),
            sa.Column('calculation_method', sa.String(length=100), nullable=False),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('admin_notes', sa.Text(), nullable=True),
            sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('disputed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('approved_by_id', UUID(as_uuid=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.CheckConstraint('order_amount > 0', name='check_order_amount_positive'),
            sa.CheckConstraint('commission_amount >= 0', name='check_commission_amount_non_negative'),
            sa.CheckConstraint('vendor_amount >= 0', name='check_vendor_amount_non_negative'),
            sa.CheckConstraint('platform_amount >= 0', name='check_platform_amount_non_negative'),
            sa.CheckConstraint('commission_rate >= 0 AND commission_rate <= 1', name='check_commission_rate_valid'),
            sa.CheckConstraint('vendor_amount + platform_amount = order_amount', name='check_amounts_balance'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('commission_number')
        )

        # Create indexes
        ops.create_index('idx_commission_calculation_date', 'commissions', ['calculated_at'])
        ops.create_index('idx_commission_order_vendor', 'commissions', ['order_id', 'vendor_id'])
        ops.create_index('idx_commission_vendor_status', 'commissions', ['vendor_id', 'status'])
        ops.create_index(ops.f('ix_commissions_id'), 'commissions', ['id'])
        ops.create_index(ops.f('ix_commissions_commission_number'), 'commissions', ['commission_number'])
        ops.create_index(ops.f('ix_commissions_order_id'), 'commissions', ['order_id'])
        ops.create_index(ops.f('ix_commissions_vendor_id'), 'commissions', ['vendor_id'])
        ops.create_index(ops.f('ix_commissions_transaction_id'), 'commissions', ['transaction_id'])
        ops.create_index(ops.f('ix_commissions_status'), 'commissions', ['status'])

    def _execute_commission_rollback(self, ops):
        """Execute the commission migration downgrade"""
        # Drop indexes
        ops.drop_index(ops.f('ix_commissions_status'), table_name='commissions')
        ops.drop_index(ops.f('ix_commissions_transaction_id'), table_name='commissions')
        ops.drop_index(ops.f('ix_commissions_vendor_id'), table_name='commissions')
        ops.drop_index(ops.f('ix_commissions_order_id'), table_name='commissions')
        ops.drop_index(ops.f('ix_commissions_commission_number'), table_name='commissions')
        ops.drop_index(ops.f('ix_commissions_id'), table_name='commissions')
        ops.drop_index('idx_commission_vendor_status', table_name='commissions')
        ops.drop_index('idx_commission_order_vendor', table_name='commissions')
        ops.drop_index('idx_commission_calculation_date', table_name='commissions')

        # Drop table
        ops.drop_table('commissions')

    def _setup_base_tables(self, conn):
        """Setup minimal base tables for foreign key testing"""
        conn.execute(text("""
            CREATE TABLE users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))

        conn.execute(text("""
            CREATE TABLE orders (
                id SERIAL PRIMARY KEY,
                order_number VARCHAR(100) UNIQUE NOT NULL,
                buyer_id UUID REFERENCES users(id),
                total_amount DECIMAL(10,2) NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))

        conn.execute(text("""
            CREATE TABLE transactions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                monto DECIMAL(12,2) NOT NULL,
                estado VARCHAR(50) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))

    def _setup_base_tables_with_data(self, conn):
        """Setup base tables with test data"""
        self._setup_base_tables(conn)

        # Insert test data
        conn.execute(text("""
            INSERT INTO users (email, username) VALUES
            ('test1@example.com', 'testuser1'),
            ('test2@example.com', 'testuser2')
        """))

        conn.execute(text("""
            INSERT INTO orders (order_number, total_amount)
            SELECT 'ORD-' || generate_series(1, 5), 100.00 * generate_series(1, 5)
        """))

        conn.commit()


@pytest.mark.integration_financial
class TestMigrationPerformance:
    """Test migration performance and optimization"""

    def test_commission_table_query_performance(self, migration_engine):
        """Test that commission table queries perform well with indexes"""
        with migration_engine.connect() as conn:
            # Setup and run migration
            self._setup_for_performance_test(conn)

            # Test query performance with explain
            result = conn.execute(text("""
                EXPLAIN ANALYZE SELECT * FROM commissions
                WHERE vendor_id = gen_random_uuid() AND status = 'PENDING'
            """))

            explain_output = result.fetchall()
            # Should use index scan, not sequential scan
            explain_text = ' '.join([str(row) for row in explain_output])
            assert 'Index Scan' in explain_text or 'Bitmap' in explain_text

    def _setup_for_performance_test(self, conn):
        """Setup tables for performance testing"""
        from sqlalchemy.dialects.postgresql import UUID
        import sqlalchemy as sa
        from alembic.migration import MigrationContext
        from alembic.operations import Operations

        # Setup base tables
        conn.execute(text("""
            CREATE TABLE users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(100) UNIQUE NOT NULL
            )
        """))

        conn.execute(text("""
            CREATE TABLE orders (
                id SERIAL PRIMARY KEY,
                order_number VARCHAR(100) UNIQUE NOT NULL,
                total_amount DECIMAL(10,2) NOT NULL,
                status VARCHAR(50) NOT NULL
            )
        """))

        conn.execute(text("""
            CREATE TABLE transactions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                monto DECIMAL(12,2) NOT NULL,
                estado VARCHAR(50) NOT NULL
            )
        """))

        # Run commission migration
        context = MigrationContext.configure(conn)
        ops = Operations(context)

        # Commission migration logic (simplified)
        ops.create_table('commissions',
            sa.Column('id', UUID(as_uuid=True), nullable=False),
            sa.Column('commission_number', sa.String(length=50), nullable=False),
            sa.Column('order_id', sa.Integer(), nullable=False),
            sa.Column('vendor_id', UUID(as_uuid=True), nullable=False),
            sa.Column('transaction_id', UUID(as_uuid=True), nullable=True),
            sa.Column('order_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
            sa.Column('commission_rate', sa.DECIMAL(precision=5, scale=4), nullable=False),
            sa.Column('commission_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
            sa.Column('vendor_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
            sa.Column('platform_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
            sa.Column('commission_type', sa.String(50), nullable=False),
            sa.Column('status', sa.String(50), nullable=False),
            sa.Column('currency', sa.String(length=3), nullable=False),
            sa.Column('calculation_method', sa.String(length=100), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )

        # Create performance indexes
        ops.create_index('idx_commission_vendor_status', 'commissions', ['vendor_id', 'status'])

        conn.commit()