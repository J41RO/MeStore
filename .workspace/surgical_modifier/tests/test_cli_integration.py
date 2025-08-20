"""
Test suite for CLI integration and functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_main_entry_point():
    """Test that __main__.py works correctly"""
    try:
        import subprocess
        result = subprocess.run([sys.executable, '__main__.py', '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0 and 'Surgical Modifier v6.0' in result.stdout
    except Exception as e:
        print(f"Entry point test failed: {e}")
        return False

def test_cli_help_system():
    """Test CLI help system"""
    try:
        from cli import main
        from click.testing import CliRunner
        
        runner = CliRunner()
        result = runner.invoke(main, ['--help'])
        return result.exit_code == 0 and 'SURGICAL MODIFIER' in result.output
    except Exception as e:
        print(f"CLI help test failed: {e}")
        return False

def test_operations_registry():
    """Test operations registry system"""
    try:
        from core.operations_registry import operations_registry
        count = operations_registry.discover_operations()
        return True  # Should work even with 0 operations
    except Exception as e:
        print(f"Operations registry test failed: {e}")
        return False

def test_argument_parser():
    """Test argument parser system"""
    try:
        from core.argument_parser import argument_parser
        specs = argument_parser.operation_specs
        return len(specs) > 0  # Should have at least common specs
    except Exception as e:
        print(f"Argument parser test failed: {e}")
        return False

def test_list_operations():
    """Test list operations functionality"""
    try:
        from cli import main
        from click.testing import CliRunner
        
        runner = CliRunner()
        result = runner.invoke(main, ['--list-operations'])
        return result.exit_code == 0
    except Exception as e:
        print(f"List operations test failed: {e}")
        return False

def test_version_command():
    """Test version command functionality"""
    try:
        from cli import main
        from click.testing import CliRunner
        
        runner = CliRunner()
        result = runner.invoke(main, ['--version'])
        return result.exit_code == 0 and 'v6.0.0' in result.output
    except Exception as e:
        print(f"Version command test failed: {e}")
        return False

def test_core_imports():
    """Test core module imports"""
    try:
        from core import operations_registry, argument_parser
        return operations_registry is not None and argument_parser is not None
    except Exception as e:
        print(f"Core imports test failed: {e}")
        return False

def test_register_operations():
    """Test operations registration"""
    try:
        from cli import register_operations
        register_operations()  # Should not raise exception
        return True
    except Exception as e:
        print(f"Register operations test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    tests = [
        ("Entry Point", test_main_entry_point),
        ("CLI Help", test_cli_help_system),
        ("Operations Registry", test_operations_registry),
        ("Argument Parser", test_argument_parser),
        ("List Operations", test_list_operations),
        ("Version Command", test_version_command),
        ("Core Imports", test_core_imports),
        ("Register Operations", test_register_operations),
    ]
    
    passed = 0
    total = len(tests)
    
    print("🧪 RUNNING CLI INTEGRATION TESTS")
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
        print("🎉 ALL TESTS PASSED! CLI system is ready.")
        return True
    else:
        print("⚠️ Some tests failed. Review implementation.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
