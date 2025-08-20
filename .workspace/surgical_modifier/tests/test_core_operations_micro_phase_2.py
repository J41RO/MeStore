"""
Test suite for MICRO-FASE 2: REPLACE + APPEND Core Operations
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_replace_operation_basic():
    """Test basic REPLACE operation functionality"""
    try:
        from core.operations.basic.replace import replace_content, replace_content_v53
        
        # Create test file with content to replace
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "replace_test.py"
            
            # Create initial content
            initial_content = "def old_function():\n    return 'old value'\n\nprint('test')"
            with open(test_file, 'w') as f:
                f.write(initial_content)
            
            # Perform replacement
            result = replace_content(str(test_file), "old_function", "new_function")
            
            # Verify result
            assert result.success == True, f"REPLACE should succeed: {result.message}"
            assert result.operation_name == "replace", "Should have operation name"
            assert result.details['replacements_made'] == 1, "Should replace one occurrence"
            
            # Verify file content
            with open(test_file, 'r') as f:
                new_content = f.read()
            
            assert "new_function" in new_content, "Should contain new function name"
            assert "old_function" not in new_content, "Should not contain old function name"
            print("✅ Basic REPLACE operation working")
        
        return True
    except Exception as e:
        print(f"Basic REPLACE test failed: {e}")
        return False

def test_replace_operation_regex():
    """Test REPLACE operation with regex support"""
    try:
        from core.operations.basic.replace import replace_content_regex
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "regex_test.py"
            
            # Create content with pattern to match
            initial_content = "def calculate_old(x):\n    return x * 2\n\ndef process_old(y):\n    return y + 1"
            with open(test_file, 'w') as f:
                f.write(initial_content)
            
            # Use regex to replace function names ending with _old
            result = replace_content_regex(str(test_file), r"def (\w+)_old", r"def \1_new")
            
            # Verify result
            assert result.success == True, f"Regex REPLACE should succeed: {result.message}"
            assert result.details['replacements_made'] == 2, "Should replace two occurrences"
            
            # Verify content
            with open(test_file, 'r') as f:
                new_content = f.read()
            
            assert "calculate_new" in new_content, "Should contain calculate_new"
            assert "process_new" in new_content, "Should contain process_new"
            assert "_old" not in new_content, "Should not contain _old"
            print("✅ Regex REPLACE operation working")
        
        return True
    except Exception as e:
        print(f"Regex REPLACE test failed: {e}")
        return False

def test_replace_v53_compatibility():
    """Test REPLACE operation v5.3 compatibility"""
    try:
        from core.operations.basic.replace import replace_content_v53
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "v53_replace_test.py"
            
            # Create test content
            initial_content = "VERSION = '1.0'\nDEBUG = False"
            with open(test_file, 'w') as f:
                f.write(initial_content)
            
            # Use v5.3 interface
            result = replace_content_v53(str(test_file), "DEBUG = False", "DEBUG = True")
            
            # Verify v5.3 compatibility
            assert result.success == True, f"v5.3 REPLACE should succeed: {result.message}"
            assert result.arguments_used is not None, "Should have arguments_used for v5.3"
            
            # Verify content
            with open(test_file, 'r') as f:
                new_content = f.read()
            
            assert "DEBUG = True" in new_content, "Should contain DEBUG = True"
            print("✅ v5.3 REPLACE compatibility working")
        
        return True
    except Exception as e:
        print(f"v5.3 REPLACE test failed: {e}")
        return False

def test_append_operation_basic():
    """Test basic APPEND operation functionality"""
    try:
        from core.operations.basic.append import append_content, append_content_v53
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "append_test.py"
            
            # Create initial content
            initial_content = "def existing_function():\n    return 'existing'"
            with open(test_file, 'w') as f:
                f.write(initial_content)
            
            # Append new content
            new_content = "\n\ndef new_function():\n    return 'new'"
            result = append_content(str(test_file), new_content)
            
            # Verify result
            assert result.success == True, f"APPEND should succeed: {result.message}"
            assert result.operation_name == "append", "Should have operation name"
            assert result.details['appended_length'] > 0, "Should have appended content"
            
            # Verify file content
            with open(test_file, 'r') as f:
                final_content = f.read()
            
            assert "existing_function" in final_content, "Should contain existing content"
            assert "new_function" in final_content, "Should contain appended content"
            print("✅ Basic APPEND operation working")
        
        return True
    except Exception as e:
        print(f"Basic APPEND test failed: {e}")
        return False

def test_append_with_separator():
    """Test APPEND operation with separator"""
    try:
        from core.operations.basic.append import append_with_separator
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "separator_test.py"
            
            # Create initial content (without ending newline)
            initial_content = "# Existing code"
            with open(test_file, 'w') as f:
                f.write(initial_content)
            
            # Append with separator
            result = append_with_separator(str(test_file), "# New section", "\n\n")
            
            # Verify result
            assert result.success == True, f"APPEND with separator should succeed: {result.message}"
            
            # Verify content
            with open(test_file, 'r') as f:
                final_content = f.read()
            
            assert "# Existing code" in final_content, "Should contain existing content"
            assert "# New section" in final_content, "Should contain appended content"
            assert "\n\n" in final_content, "Should contain separator"
            print("✅ APPEND with separator working")
        
        return True
    except Exception as e:
        print(f"APPEND with separator test failed: {e}")
        return False

def test_append_v53_compatibility():
    """Test APPEND operation v5.3 compatibility"""
    try:
        from core.operations.basic.append import append_content_v53
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "v53_append_test.py"
            
            # Create test content
            initial_content = "print('start')"
            with open(test_file, 'w') as f:
                f.write(initial_content)
            
            # Use v5.3 interface
            result = append_content_v53(str(test_file), "\nprint('end')")
            
            # Verify v5.3 compatibility
            assert result.success == True, f"v5.3 APPEND should succeed: {result.message}"
            assert result.arguments_used is not None, "Should have arguments_used for v5.3"
            
            # Verify content
            with open(test_file, 'r') as f:
                final_content = f.read()
            
            assert "print('start')" in final_content, "Should contain initial content"
            assert "print('end')" in final_content, "Should contain appended content"
            print("✅ v5.3 APPEND compatibility working")
        
        return True
    except Exception as e:
        print(f"v5.3 APPEND test failed: {e}")
        return False

def test_rollback_functionality():
    """Test rollback functionality for REPLACE and APPEND"""
    try:
        from core.operations.basic.replace import replace_operation
        from core.operations.basic.append import append_operation
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test REPLACE rollback
            replace_file = temp_path / "replace_rollback_test.py"
            original_content = "def original(): pass"
            with open(replace_file, 'w') as f:
                f.write(original_content)
            
            # Perform replace and rollback
            context = replace_operation.prepare_context(
                str(replace_file), "new_content", 
                position_marker="original"
            )
            result = replace_operation.execute_with_logging(context)
            
            if result.success:
                # Test rollback
                rollback_success = replace_operation.rollback_replace(replace_file)
                if rollback_success:
                    with open(replace_file, 'r') as f:
                        restored_content = f.read()
                    assert restored_content == original_content, "REPLACE rollback should restore original content"
                    print("✅ REPLACE rollback working")
            
            # Test APPEND rollback
            append_file = temp_path / "append_rollback_test.py"
            original_content = "def original(): pass"
            with open(append_file, 'w') as f:
                f.write(original_content)
            
            # Perform append and rollback
            context = append_operation.prepare_context(str(append_file), "\ndef appended(): pass")
            result = append_operation.execute_with_logging(context)
            
            if result.success:
                # Test rollback
                rollback_success = append_operation.rollback_append(append_file)
                if rollback_success:
                    with open(append_file, 'r') as f:
                        restored_content = f.read()
                    assert restored_content == original_content, "APPEND rollback should restore original content"
                    print("✅ APPEND rollback working")
        
        return True
    except Exception as e:
        print(f"Rollback test failed: {e}")
        return False

def run_core_operations_tests():
    """Run all CORE OPERATIONS tests"""
    tests = [
        ("REPLACE Basic Operation", test_replace_operation_basic),
        ("REPLACE Regex Support", test_replace_operation_regex),
        ("REPLACE v5.3 Compatibility", test_replace_v53_compatibility),
        ("APPEND Basic Operation", test_append_operation_basic),
        ("APPEND with Separator", test_append_with_separator),
        ("APPEND v5.3 Compatibility", test_append_v53_compatibility),
        ("Rollback Functionality", test_rollback_functionality),
    ]
    
    passed = 0
    total = len(tests)
    
    print("🧪 RUNNING CORE OPERATIONS TESTS (MICRO-FASE 2)")
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
        print("🎉 CORE OPERATIONS TESTS PASSED! REPLACE + APPEND fully functional.")
        return True
    else:
        print("⚠️ Some tests failed. Review implementation.")
        return False

if __name__ == "__main__":
    success = run_core_operations_tests()
    sys.exit(0 if success else 1)
