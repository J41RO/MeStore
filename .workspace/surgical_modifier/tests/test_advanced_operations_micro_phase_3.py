"""
Test suite for MICRO-FASE 3: AFTER + BEFORE Advanced Operations
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_after_operation_basic():
    """Test basic AFTER operation functionality"""
    try:
        from core.operations.basic.after import insert_after, insert_after_v53
        
        # Create test file with content
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "after_test.py"
            
            # Create initial content
            initial_content = "def function_one():\n    return 1\n\ndef function_two():\n    return 2"
            with open(test_file, 'w') as f:
                f.write(initial_content)
            
            # Insert content after function_one
            result = insert_after(str(test_file), "def function_one():", "    print('After function_one')")
            
            # Verify result
            assert result.success == True, f"AFTER should succeed: {result.message}"
            assert result.operation_name == "after", "Should have operation name"
            assert result.details['insertions_made'] == 1, "Should insert one occurrence"
            
            # Verify file content
            with open(test_file, 'r') as f:
                new_content = f.read()
            
            assert "def function_one():" in new_content, "Should contain original function"
            assert "print('After function_one')" in new_content, "Should contain inserted content"
            lines = new_content.split('\n')
            func_one_line = None
            for i, line in enumerate(lines):
                if "def function_one():" in line:
                    func_one_line = i
                    break
            
            assert func_one_line is not None, "Should find function_one line"
            assert "After function_one" in lines[func_one_line + 1], "Should have inserted content after"
            assert "return 1" in lines[func_one_line + 2], "Should have original return after inserted content"
            print("✅ Basic AFTER operation working")
        
        return True
    except Exception as e:
        print(f"Basic AFTER test failed: {e}")
        return False

def test_after_operation_regex():
    """Test AFTER operation with regex support"""
    try:
        from core.operations.basic.after import insert_after_regex
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "regex_after_test.py"
            
            # Create content with pattern to match
            initial_content = "import os\nimport sys\nimport json\n\ndef main():\n    pass"
            with open(test_file, 'w') as f:
                f.write(initial_content)
            
            # Use regex to insert after any import statement
            result = insert_after_regex(str(test_file), r"^import\s+\w+", "import datetime")
            
            # Verify result
            assert result.success == True, f"Regex AFTER should succeed: {result.message}"
            assert result.details['insertions_made'] == 1, "Should insert after first match only"
            
            # Verify content
            with open(test_file, 'r') as f:
                new_content = f.read()
            
            assert "import datetime" in new_content, "Should contain inserted import"
            lines = new_content.split('\n')
            assert "import os" in lines[0], "Should have original import"
            assert "import datetime" in lines[1], "Should have inserted import after first"
            print("✅ Regex AFTER operation working")
        
        return True
    except Exception as e:
        print(f"Regex AFTER test failed: {e}")
        return False

def test_before_operation_basic():
    """Test basic BEFORE operation functionality"""
    try:
        from core.operations.basic.before import insert_before, insert_before_v53
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "before_test.py"
            
            # Create initial content
            initial_content = "def main():\n    print('start')\n    return 0"
            with open(test_file, 'w') as f:
                f.write(initial_content)
            
            # Insert content before return statement
            result = insert_before(str(test_file), "return 0", "    print('before return')")
            
            # Verify result
            assert result.success == True, f"BEFORE should succeed: {result.message}"
            assert result.operation_name == "before", "Should have operation name"
            assert result.details['insertions_made'] == 1, "Should insert one occurrence"
            
            # Verify file content
            with open(test_file, 'r') as f:
                new_content = f.read()
            
            assert "return 0" in new_content, "Should contain original return"
            assert "print('before return')" in new_content, "Should contain inserted content"
            lines = new_content.split('\n')
            return_line = None
            for i, line in enumerate(lines):
                if "return 0" in line:
                    return_line = i
                    break
            
            assert return_line is not None, "Should find return line"
            # BEFORE inserts content before the matching line, so the return line moves down
            assert "before return" in lines[return_line], "Should have inserted content before return"
            assert "return 0" in lines[return_line + 1], "Should have original return after inserted content"
            print("✅ Basic BEFORE operation working")
        
        return True
    except Exception as e:
        print(f"Basic BEFORE test failed: {e}")
        return False

def test_before_operation_regex():
    """Test BEFORE operation with regex support"""
    try:
        from core.operations.basic.before import insert_before_regex
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "regex_before_test.py"
            
            # Create content with pattern to match
            initial_content = "class MyClass:\n    def __init__(self):\n        pass\n\n    def method(self):\n        return True"
            with open(test_file, 'w') as f:
                f.write(initial_content)
            
            # Use regex to insert before any method definition
            result = insert_before_regex(str(test_file), r"def method", "    # Method implementation")
            
            # Verify result
            assert result.success == True, f"Regex BEFORE should succeed: {result.message}"
            assert result.details['insertions_made'] == 1, "Should insert before first match"
            
            # Verify content
            with open(test_file, 'r') as f:
                new_content = f.read()
            
            assert "# Method implementation" in new_content, "Should contain inserted comment"
            assert "def method(self):" in new_content, "Should contain original method"
            print("✅ Regex BEFORE operation working")
        
        return True
    except Exception as e:
        print(f"Regex BEFORE test failed: {e}")
        return False

def test_indentation_preservation():
    """Test indentation preservation in AFTER and BEFORE operations"""
    try:
        from core.operations.basic.after import insert_after
        from core.operations.basic.before import insert_before
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "indentation_test.py"
            
            # Create content with indentation
            initial_content = "class MyClass:\n    def method(self):\n        if True:\n            return 'test'\n        return None"
            with open(test_file, 'w') as f:
                f.write(initial_content)
            
            # Test AFTER with indentation preservation
            result = insert_after(str(test_file), "if True:", "print('inside if')")
            
            assert result.success == True, f"AFTER with indentation should succeed: {result.message}"
            
            # Verify indentation
            with open(test_file, 'r') as f:
                content_after = f.read()
            
            lines = content_after.split('\n')
            if_line = None
            for i, line in enumerate(lines):
                if "if True:" in line:
                    if_line = i
                    break
            
            assert if_line is not None, "Should find if statement"
            inserted_line = lines[if_line + 1]
            assert inserted_line.startswith("        "), "Should preserve indentation"
            assert "print('inside if')" in inserted_line, "Should contain inserted content"
            
            print("✅ Indentation preservation working")
        
        return True
    except Exception as e:
        print(f"Indentation preservation test failed: {e}")
        return False

def test_v53_compatibility():
    """Test v5.3 compatibility for AFTER and BEFORE"""
    try:
        from core.operations.basic.after import insert_after_v53
        from core.operations.basic.before import insert_before_v53
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test AFTER v5.3
            after_file = temp_path / "v53_after_test.py"
            with open(after_file, 'w') as f:
                f.write("print('start')\nprint('end')")
            
            result = insert_after_v53(str(after_file), "print('start')", "print('middle')")
            
            assert result.success == True, f"v5.3 AFTER should succeed: {result.message}"
            assert result.arguments_used is not None, "Should have arguments_used for v5.3"
            
            # Test BEFORE v5.3
            before_file = temp_path / "v53_before_test.py"
            with open(before_file, 'w') as f:
                f.write("print('start')\nprint('end')")
            
            result = insert_before_v53(str(before_file), "print('end')", "print('middle')")
            
            assert result.success == True, f"v5.3 BEFORE should succeed: {result.message}"
            assert result.arguments_used is not None, "Should have arguments_used for v5.3"
            
            print("✅ v5.3 compatibility working")
        
        return True
    except Exception as e:
        print(f"v5.3 compatibility test failed: {e}")
        return False

def test_rollback_functionality():
    """Test rollback functionality for AFTER and BEFORE"""
    try:
        from core.operations.basic.after import after_operation
        from core.operations.basic.before import before_operation
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test AFTER rollback
            after_file = temp_path / "after_rollback_test.py"
            original_content = "def test(): pass"
            with open(after_file, 'w') as f:
                f.write(original_content)
            
            # Perform after insertion and rollback
            context = after_operation.prepare_context(
                str(after_file), "print('inserted')", 
                position_marker="def test():"
            )
            result = after_operation.execute_with_logging(context)
            
            if result.success:
                # Test rollback
                rollback_success = after_operation.rollback_after(after_file)
                if rollback_success:
                    with open(after_file, 'r') as f:
                        restored_content = f.read()
                    assert restored_content == original_content, "AFTER rollback should restore original content"
                    print("✅ AFTER rollback working")
            
            # Test BEFORE rollback
            before_file = temp_path / "before_rollback_test.py"
            original_content = "def test(): pass"
            with open(before_file, 'w') as f:
                f.write(original_content)
            
            # Perform before insertion and rollback
            context = before_operation.prepare_context(
                str(before_file), "# Comment", 
                position_marker="def test():"
            )
            result = before_operation.execute_with_logging(context)
            
            if result.success:
                # Test rollback
                rollback_success = before_operation.rollback_before(before_file)
                if rollback_success:
                    with open(before_file, 'r') as f:
                        restored_content = f.read()
                    assert restored_content == original_content, "BEFORE rollback should restore original content"
                    print("✅ BEFORE rollback working")
        
        return True
    except Exception as e:
        print(f"Rollback test failed: {e}")
        return False

def run_advanced_operations_tests():
    """Run all ADVANCED OPERATIONS tests"""
    tests = [
        ("AFTER Basic Operation", test_after_operation_basic),
        ("AFTER Regex Support", test_after_operation_regex),
        ("BEFORE Basic Operation", test_before_operation_basic),
        ("BEFORE Regex Support", test_before_operation_regex),
        ("Indentation Preservation", test_indentation_preservation),
        ("v5.3 Compatibility", test_v53_compatibility),
        ("Rollback Functionality", test_rollback_functionality),
    ]
    
    passed = 0
    total = len(tests)
    
    print("🧪 RUNNING ADVANCED OPERATIONS TESTS (MICRO-FASE 3)")
    print("=" * 60)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("=" * 60)
    print(f"📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ADVANCED OPERATIONS TESTS PASSED! AFTER + BEFORE fully functional.")
        return True
    else:
        print("⚠️ Some tests failed. Review implementation.")
        return False

if __name__ == "__main__":
    success = run_advanced_operations_tests()
    sys.exit(0 if success else 1)
