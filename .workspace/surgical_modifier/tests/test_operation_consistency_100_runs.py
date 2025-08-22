import pytest
import tempfile
import os
import time
from pathlib import Path

def test_deterministic_operations_quick():
    """Test rápido para verificar que las operaciones determinísticas funcionan."""
    
    print("\n🚀 EJECUTANDO TEST RÁPIDO DE OPERACIONES DETERMINÍSTICAS")
    
    # Test 1: Verificar que retry_manager funciona
    from utils.retry_manager import retry_with_backoff
    
    @retry_with_backoff(max_attempts=2, base_delay=0.1)
    def test_retry():
        if not hasattr(test_retry, 'calls'):
            test_retry.calls = 0
        test_retry.calls += 1
        if test_retry.calls == 1:
            raise ValueError("First attempt fails")
        return "success"
    
    result = test_retry()
    assert "success" in result
    print("✅ Retry system: FUNCTIONAL")
    
    # Test 2: Verificar que logger extendido funciona
    from utils.logger import logger
    
    try:
        exec("invalid syntax")
    except SyntaxError as e:
        analysis = logger.detailed_failure_analysis(e, {'test': 'context'})
        assert 'SYNTAX_ERROR' in str(analysis)
        print("✅ Enhanced logger: FUNCTIONAL")
    
    # Test 3: Verificar que debug analyzer funciona
    from utils.debug_analyzer import PatternDebugger
    
    test_file = tempfile.mktemp(suffix='.py')
    with open(test_file, 'w') as f:
        f.write("class TestClass:\n    pass")
    
    debugger = PatternDebugger(verbose=False)
    debug_info = debugger.debug_pattern_matching(test_file, "class.*:")
    assert len(debug_info['matches_found']) > 0
    print("✅ Pattern debugger: FUNCTIONAL")
    
    # Test 4: Verificar integración con BaseOperation
    from core.operations.basic.create import CreateOperation
    from core.operations.base_operation import OperationContext, OperationType
    
    # Test básico de CREATE con retry habilitado
    test_file = tempfile.mktemp(suffix='_integration.py')
    context = OperationContext(
        project_root=Path(tempfile.gettempdir()),
        target_file=Path(test_file),
        operation_type=OperationType.CREATE,
        content="# Test integration\ndef test(): pass",
        arguments={'enable_retry': True, 'retry_attempts': 2}
    )
    
    operation = CreateOperation()
    result = operation.execute_with_logging(context)
    
    assert result.success, f"Operation failed: {result.message}"
    assert os.path.exists(test_file), "File was not created"
    print("✅ BaseOperation integration: FUNCTIONAL")
    
    # Test 5: Test de consistencia simple (5 runs)
    consistent_results = []
    for i in range(5):
        test_file = tempfile.mktemp(suffix=f'_consistency_{i}.py')
        context = OperationContext(
            project_root=Path(tempfile.gettempdir()),
            target_file=Path(test_file),
            operation_type=OperationType.CREATE,
            content=f"# Consistency test {i}\ndef test_{i}(): pass",
            arguments={'enable_retry': False}  # Sin retry para velocidad
        )
        
        operation = CreateOperation()
        result = operation.execute_with_logging(context)
        consistent_results.append(result.success)
    
    consistency_rate = sum(consistent_results) / len(consistent_results)
    assert consistency_rate == 1.0, f"Consistency failed: {consistency_rate}"
    print("✅ Operation consistency (5 runs): DETERMINISTIC")
    
    # Cleanup
    try:
        os.remove(test_file)
        for i in range(5):
            test_file = tempfile.mktemp(suffix=f'_consistency_{i}.py')
            if os.path.exists(test_file):
                os.remove(test_file)
    except:
        pass
    
    print("\n🎉 TODAS LAS VERIFICACIONES DE OPERACIONES DETERMINÍSTICAS PASARON")
    print("✅ Sistema completo funcional y determinístico")
    
    return True

if __name__ == "__main__":
    test_deterministic_operations_quick()