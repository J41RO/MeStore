#!/bin/bash

# Script para identificar archivos de tests con errores
echo "Revisando todos los archivos de tests en tests/api/"
echo "==========================================="

failed_files=()
passed_files=()

for test_file in tests/api/test_*.py; do
    echo "Testing: $test_file"
    timeout 20 python -m pytest "$test_file" -v --tb=no -q 2>&1 > /tmp/test_output.txt
    exit_code=$?

    if [ $exit_code -ne 0 ]; then
        failed_files+=("$test_file")
        echo "  ❌ FAILED"
    else
        passed_files+=("$test_file")
        echo "  ✅ PASSED"
    fi
done

echo ""
echo "==========================================="
echo "RESUMEN:"
echo "==========================================="
echo "Archivos que PASARON (${#passed_files[@]}):"
for file in "${passed_files[@]}"; do
    echo "  ✅ $file"
done

echo ""
echo "Archivos con ERRORES (${#failed_files[@]}):"
for file in "${failed_files[@]}"; do
    echo "  ❌ $file"
done
