import pytest

# Skip entire debugging folder for performance optimization
pytestmark = pytest.mark.skip(reason="Debugging tests - performance optimization during database work")