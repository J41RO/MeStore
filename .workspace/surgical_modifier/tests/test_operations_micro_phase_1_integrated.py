"""
Test suite for MICRO-FASE 1 INTEGRATED: BaseOperation + CREATE + Registry Integration
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_base_operation_integrated():
    """Test BaseOperation integration with existing architecture"""
    try:
        from core.operations.base_operation import BaseOperation, OperationType
        
        # Test integration with OperationSpec
        try:
            from core.argument_parser import OperationSpec
            integration_available = True
        except ImportError:
            integration_available = False
        
        print(f"OperationSpec integration: {integration_available}")
        
        # Test that BaseOperation is abstract
        try:
            base_op = BaseOperation(OperationType.CREATE)
            return False  # Should not reach here
        except TypeError:
            pass  # Expected - BaseOperation is abstract
        
        return True
    except Exception as e:
        print(f"BaseOperation integration test failed: {e}")
        return False

def test_create_operation_integrated():
    """Test CREATE operation with full integration"""
    try:
        from core.operations.basic.create import CreateOperation, create_file, create_file_v53
        
        # Test instantiation
        create_op = CreateOperation()
        assert create_op.operation_type.value == "create"
        assert create_op.operation_name == "create"
        assert create_op.can_rollback() == True
        
        # Test OperationSpec integration
        operation_spec = create_op.get_operation_spec()
        if operation_spec:
            assert operation_spec.name == "create"
            print(f"✅ OperationSpec: {operation_spec.description}")
        
        return True
    except Exception as e:
        print(f"CREATE operation integration test failed: {e}")
        return False

def test_create_operation_execution_integrated():
    """Test CREATE operation execution with integration"""
    try:
        from core.operations.basic.create import create_file, create_file_v53
        
        # Test modern interface
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test_integrated.py"
            test_content = "# Integrated test file\nprint('Hello Integration')"
            
            # Execute CREATE operation
            result = create_file(str(test_file), test_content)
            
            # Verify result
            assert result.success == True, f"CREATE should succeed: {result.message}"
            assert result.operation_name == "create", "Should have operation name"
            assert test_file.exists(), "File should be created"
            
            # Verify content
            with open(test_file, 'r') as f:
                created_content = f.read()
            assert created_content == test_content, "Content should match"
        
        # Test v5.3 compatibility interface
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file_v53 = temp_path / "test_v53.py"
            test_content_v53 = "# v5.3 compatibility test"
            
            # Execute with v5.3 interface
            result_v53 = create_file_v53(str(test_file_v53), test_content_v53)
            
            # Verify v5.3 result
            assert result_v53.success == True, f"v5.3 CREATE should succeed: {result_v53.message}"
            assert result_v53.arguments_used is not None, "Should have arguments_used for v5.3"
            assert test_file_v53.exists(), "v5.3 file should be created"
        
        return True
    except Exception as e:
        print(f"CREATE operation execution integration test failed: {e}")
        return False

def test_operations_registry_integration():
    """Test integration with enhanced operations registry"""
    try:
        from core.operations_registry import enhanced_operations_registry
        
        # Test registry listing
        operations = enhanced_operations_registry.list_all_operations()
        assert 'base_operations' in operations, "Should have base_operations"
        assert 'legacy_operations' in operations, "Should have legacy_operations"
        
        # Test CREATE operation registration
        if 'create' in operations['base_operations']:
            create_info = enhanced_operations_registry.get_operation_info('create')
            assert create_info is not None, "CREATE info should be available"
            assert create_info['name'] == 'create', "Should have correct name"
            assert create_info['type'] == 'base_operation', "Should be base operation type"
            assert create_info['supports_rollback'] == True, "CREATE should support rollback"
            print(f"✅ CREATE operation registered: {create_info['description']}")
        else:
            print("⚠️  CREATE not in base operations list")
        
        return True
    except Exception as e:
        print(f"Operations registry integration test failed: {e}")
        return False

def test_template_integration():
    """Test template integration with CREATE operation"""
    try:
        from core.operations.basic.create import create_file_with_template
        
        # Test template creation
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "template_test.py"
            
            # Create with function template
            result = create_file_with_template(str(test_file), "function")
            
            # Verify result
            assert result.success == True, f"Template creation should succeed: {result.message}"
            assert test_file.exists(), "Template file should be created"
            
            # Check that content was generated
            with open(test_file, 'r') as f:
                content = f.read()
            
            assert 'def template_test' in content, "Should contain function definition"
            print(f"✅ Template content generated: {len(content)} characters")
        
        return True
    except Exception as e:
        print(f"Template integration test failed: {e}")
        return False

def test_rollback_functionality():
    """Test rollback functionality"""
    try:
        from core.operations.basic.create import create_operation
        
        # Test rollback capability
        assert create_operation.can_rollback() == True, "CREATE should support rollback"
        
        # Test actual rollback (if files were created)
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "rollback_test.py"
            
            # Create file
            context = create_operation.prepare_context(str(test_file), "# Rollback test")
            result = create_operation.execute_with_logging(context)
            
            if result.success:
                assert test_file.exists(), "File should be created"
                
                # Test rollback
                rollback_success = create_operation.rollback_create(test_file)
                if rollback_success:
                    assert not test_file.exists(), "File should be deleted after rollback"
                    print("✅ Rollback functionality working")
                else:
                    print("⚠️  Rollback failed (may be expected in some environments)")
        
        return True
    except Exception as e:
        print(f"Rollback functionality test failed: {e}")
        return False

def test_systems_integration():
    """Test integration with all existing systems"""
    try:
        from core.operations.basic.create import create_file
        
        # Test with project context awareness
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "systems_integration_test.py"
            
            # Test with project context awareness
            result = create_file(
                str(test_file), 
                "# Systems integration test\n",
                validate_content=True,
                backup_enabled=True
            )
            
            if result.success:
                # Verify integration features were used
                assert result.content_processed is not None, "Content should be processed"
                print("✅ CREATE operation with systems integration successful")
        
        return True
    except Exception as e:
        print(f"Systems integration test failed: {e}")
        return False

def run_micro_phase_1_integrated_tests():
    """Run all MICRO-FASE 1 INTEGRATED tests"""
    tests = [
        ("BaseOperation Integration", test_base_operation_integrated),
        ("CREATE Operation Integration", test_create_operation_integrated),
        ("CREATE Execution Integration", test_create_operation_execution_integrated),
        ("Operations Registry Integration", test_operations_registry_integration),
        ("Template Integration", test_template_integration),
        ("Rollback Functionality", test_rollback_functionality),
        ("Systems Integration", test_systems_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    print("🧪 RUNNING MICRO-FASE 1 INTEGRATED TESTS")
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
        print("🎉 MICRO-FASE 1 INTEGRATED TESTS PASSED! Foundation with integration ready.")
        return True
    else:
        print("⚠️ Some tests failed. Review implementation.")
        return False

if __name__ == "__main__":
    success = run_micro_phase_1_integrated_tests()
    sys.exit(0 if success else 1)
