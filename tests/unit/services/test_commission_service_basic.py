# Basic Commission Service Test - Working Test
# Purpose: Verify commission service works without complex middleware

import pytest
import logging
from app.services.commission_service import CommissionService
from app.database import SessionLocal

logger = logging.getLogger(__name__)


class TestCommissionServiceBasic:
    """Basic working test for commission service"""

    def test_commission_service_list_commissions_empty_db(self):
        """Test that list_commissions works with empty database"""
        db = SessionLocal()
        try:
            service = CommissionService(db)

            # Test basic functionality
            result = service.list_commissions(limit=10, offset=0)

            # Verify return structure
            assert isinstance(result, dict)
            assert 'commissions' in result
            assert 'pagination' in result
            assert 'summary' in result
            assert 'filters_applied' in result

            # Verify empty db returns empty list
            assert len(result['commissions']) == 0
            assert result['pagination']['total_count'] == 0

            logger.info("✅ Commission service basic test PASSED")

        finally:
            db.close()

    def test_commission_service_initialization(self):
        """Test commission service can be initialized"""
        db = SessionLocal()
        try:
            service = CommissionService(db)
            assert service is not None
            assert hasattr(service, 'list_commissions')
            assert callable(service.list_commissions)

            logger.info("✅ Commission service initialization test PASSED")

        finally:
            db.close()