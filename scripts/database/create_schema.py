#!/usr/bin/env python3
"""
Script to create database schema directly using SQLAlchemy
"""
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app.models import user, product, inventory, order, payment, category
from app.models import commission, storage, transaction
from app.models import admin_activity_log, admin_permission
from app.models import commission_dispute, discrepancy_report
from app.models import incidente_inventario, incoming_product_queue
from app.models import inventory_audit, movement_tracker, movimiento_stock
from app.models import payout_history, payout_request
from app.models import product_image, system_setting
from app.models import vendor_audit, vendor_document, vendor_note

def create_schema():
    """Create all tables in the database"""
    print("🔧 Creating database schema...")
    print(f"📂 Database: {engine.url}")

    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Schema created successfully!")

        # List created tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"\n📊 Total tables created: {len(tables)}")
        print("📋 Tables:", ", ".join(sorted(tables)))

        return True
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_schema()
    sys.exit(0 if success else 1)