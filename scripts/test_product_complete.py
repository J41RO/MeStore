#!/usr/bin/env python3
"""
Script para ejecutar todos los tests de Product de manera organizada.
"""

import subprocess
import sys
import os
import glob

def find_product_test_files():
    """Encontrar todos los archivos de tests relacionados con Product."""
    
    test_patterns = [
        '**/test_product*.py',
        '**/test*product*.py',
        'tests/test_product*.py',
        'backend/tests/test_product*.py',
        'app/tests/test_product*.py'
    ]
    
    found_files = []
    for pattern in test_patterns:
        files = glob.glob(pattern, recursive=True)
        found_files.extend(files)
    
    # Eliminar duplicados y archivos que no existen
    unique_files = []
    for file in found_files:
        if os.path.exists(file) and file not in unique_files:
            unique_files.append(file)
    
    return unique_files

def run_all_product_tests():
    """Ejecutar todos los tests relacionados con Product."""
    
    print('=== 🧪 EJECUCIÓN COMPLETA DE TESTS PRODUCT ===')
    
    # Buscar archivos de tests automáticamente
    test_files = find_product_test_files()
    
    if not test_files:
        print('❌ NO SE ENCONTRARON ARCHIVOS DE TESTS PRODUCT')
        print('🔍 BUSCANDO EN DIRECTORIOS COMUNES:')
        
        # Listar directorios de tests posibles
        possible_dirs = ['tests/', 'backend/tests/', 'app/tests/', 'test/']
        for test_dir in possible_dirs:
            if os.path.exists(test_dir):
                files = os.listdir(test_dir)
                product_files = [f for f in files if 'product' in f.lower() and f.endswith('.py')]
                if product_files:
                    print(f'   📁 {test_dir}: {product_files}')
        return False
    
    print(f'✅ ARCHIVOS DE TESTS ENCONTRADOS: {len(test_files)}')
    for f in test_files:
        print(f'   📄 {f}')
    
    total_passed = 0
    total_failed = 0
    
    for test_file in test_files:
        print(f'\n🔍 EJECUTANDO: {test_file}')
        print('=' * 50)
        
        try:
            result = subprocess.run([
                'python3', '-m', 'pytest', test_file, '-v'
            ], capture_output=True, text=True, cwd='.')
            
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            
            # Contar resultados
            stdout = result.stdout
            passed = stdout.count(' PASSED')
            failed = stdout.count(' FAILED')
            
            total_passed += passed
            total_failed += failed
            
            print(f'📊 RESULTADOS {test_file}: {passed} ✅ PASSED, {failed} ❌ FAILED')
            
        except Exception as e:
            print(f'❌ ERROR ejecutando {test_file}: {e}')
            total_failed += 1
    
    print('\n' + '=' * 60)
    print(f'🏆 RESUMEN TOTAL DE TESTS PRODUCT:')
    print(f'   ✅ PASSED: {total_passed}')
    print(f'   ❌ FAILED: {total_failed}')
    print(f'   📊 TOTAL: {total_passed + total_failed}')
    
    if total_failed == 0 and total_passed > 0:
        print('🎉 ✅ TODOS LOS TESTS PRODUCT PASARON EXITOSAMENTE')
        return True
    elif total_passed == 0:
        print('⚠️ NO SE EJECUTARON TESTS - VERIFICAR RUTAS')
        return False
    else:
        print('⚠️ HAY TESTS FALLIDOS - REVISAR ARRIBA')
        return False

if __name__ == '__main__':
    success = run_all_product_tests()
    sys.exit(0 if success else 1)
