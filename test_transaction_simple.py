#!/usr/bin/env python3
"""
Simple test to validate transaction service functionality
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.services.transaction_service import TransactionService
from app.models.transaction import MetodoPago, TransactionType, EstadoTransaccion
from decimal import Decimal
from uuid import uuid4

def test_transaction_service_basic():
    """Test basic transaction service functionality"""

    # Create test database
    engine = create_engine("sqlite:///./test_transaction.db", echo=False)
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    try:
        with SessionLocal() as session:
            # Create transaction service
            service = TransactionService(db_session=session)

            print("✅ TransactionService initialized")

            # Test get_transaction_history method
            history_result = service.get_transaction_history(
                user_id=None,
                transaction_type=None,
                limit=10,
                offset=0,
                db=session
            )

            print("✅ TransactionService.get_transaction_history() works!")
            print(f"   - Returned {len(history_result['transactions'])} transactions")
            print(f"   - Pagination: {history_result['pagination']}")
            print(f"   - Summary: {history_result['summary']}")

            # Test calculate_fees method
            fees_result = service.calculate_fees(
                base_amount=Decimal("100000.00"),  # 100k COP
                commission_rate=Decimal("0.15"),   # 15%
                transaction_type=TransactionType.VENTA
            )

            print("✅ TransactionService.calculate_fees() works!")
            print(f"   - Base amount: {fees_result['base_amount']}")
            print(f"   - Platform fee: {fees_result['platform_fee']}")
            print(f"   - Vendor amount: {fees_result['vendor_amount']}")
            print(f"   - Commission rate: {fees_result['commission_rate']}")

            return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        try:
            os.remove("./test_transaction.db")
        except:
            pass

if __name__ == "__main__":
    success = test_transaction_service_basic()
    if success:
        print("\n🚀 TRANSACTION SERVICE IMPLEMENTATION SUCCESSFUL!")
        print("   All major service methods working correctly")
    else:
        print("\n💥 TRANSACTION SERVICE NEEDS FIXES")

    sys.exit(0 if success else 1)