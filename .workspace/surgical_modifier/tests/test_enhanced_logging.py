"""
Comprehensive test suite for enhanced logging system
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_enhanced_logger_basic():
    """Test basic logging functions"""
    try:
        from utils.logger import logger

        # Test basic functions
        logger.info("Test info message")
        logger.success("Test success message")
        logger.warning("Test warning message")
        logger.error("Test error message")

        return True
    except Exception as e:
        print(f"Enhanced logger basic test failed: {e}")
        return False


def test_operation_tracking():
    """Test operation start/end tracking"""
    try:
        from utils.logger import logger

        logger.operation_start("test_operation", "Testing operation tracking")
        time.sleep(0.1)
        logger.operation_end("test_operation", success=True)

        return True
    except Exception as e:
        print(f"Operation tracking test failed: {e}")
        return False


def test_file_operations_logging():
    """Test file operations logging"""
    try:
        from utils.logger import logger

        logger.file_operation("create", "test_file.py", "Testing file creation logging")
        logger.file_operation("update", "test_file.py", "Testing file update logging")

        return True
    except Exception as e:
        print(f"File operations test failed: {e}")
        return False


def test_progress_manager():
    """Test progress manager functionality"""
    try:
        from utils.progress_manager import progress_manager

        # Test operation progress
        with progress_manager.operation_progress("test_progress", 3) as progress:
            for i in range(3):
                progress.step(f"Step {i+1}")
                time.sleep(0.05)

        return True
    except Exception as e:
        print(f"Progress manager test failed: {e}")
        return False


def test_diff_visualizer():
    """Test diff visualization system"""
    try:
        from utils.diff_visualizer import diff_visualizer

        before = "def hello():\n    print('old')"
        after = "def hello():\n    print('new')\n    print('enhanced')"

        # Test change summary
        diff_visualizer.show_change_summary(before, after, "test.py")

        # Test language detection
        lang = diff_visualizer.detect_language("test.py")
        assert lang == "python", f"Expected python, got {lang}"

        return True
    except Exception as e:
        print(f"Diff visualizer test failed: {e}")
        return False


def test_operation_summary():
    """Test operation summary functionality"""
    try:
        from utils.logger import logger

        # Generate some operations
        logger.info("Test info")
        logger.success("Test success")
        logger.warning("Test warning")

        # Show summary
        logger.show_operation_summary()

        return True
    except Exception as e:
        print(f"Operation summary test failed: {e}")
        return False


def test_rich_components():
    """Test that all Rich components work"""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.progress import Progress
        from rich.syntax import Syntax

        console = Console()
        console.print("✅ Rich components test passed")

        return True
    except Exception as e:
        print(f"Rich components test failed: {e}")
        return False


def test_backward_compatibility():
    """Test backward compatibility with old SurgicalLogger"""
    try:
        from utils.logger import SurgicalLogger

        # Test that old logger still works
        old_logger = SurgicalLogger()
        old_logger.info("Backward compatibility test")
        old_logger.success("Old interface works")

        return True
    except Exception as e:
        print(f"Backward compatibility test failed: {e}")
        return False


def run_all_logging_tests():
    """Run all logging tests and report results"""
    tests = [
        ("Enhanced Logger Basic", test_enhanced_logger_basic),
        ("Operation Tracking", test_operation_tracking),
        ("File Operations Logging", test_file_operations_logging),
        ("Progress Manager", test_progress_manager),
        ("Diff Visualizer", test_diff_visualizer),
        ("Operation Summary", test_operation_summary),
        ("Rich Components", test_rich_components),
        ("Backward Compatibility", test_backward_compatibility),
    ]

    passed = 0
    total = len(tests)

    print("🧪 RUNNING ENHANCED LOGGING TESTS")
    print("=" * 50)

    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")

    print("=" * 50)
    print(f"📊 RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL LOGGING TESTS PASSED! Enhanced logging system is ready.")
        return True
    else:
        print("⚠️ Some tests failed. Review implementation.")
        return False


if __name__ == "__main__":
    success = run_all_logging_tests()
    sys.exit(0 if success else 1)
