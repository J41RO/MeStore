#!/usr/bin/env python
"""
Script to fix all hanging API tests by ensuring proper async handling
and adding timeout protection for problematic dependencies.
"""
import os
import sys

def add_pytest_timeout_to_file(filepath):
    """Add pytest timeout marker to all test functions in a file"""
    with open(filepath, 'r') as f:
        content = f.read()

    # Check if already has timeout import
    if '@pytest.mark.timeout(' not in content:
        # Add timeout import if pytest is imported
        if 'import pytest' in content:
            content = content.replace(
                'import pytest',
                'import pytest\nimport pytest_timeout'
            )

        # Add timeout decorator to all test functions
        lines = content.split('\n')
        new_lines = []
        for i, line in enumerate(lines):
            if line.strip().startswith('async def test_') or line.strip().startswith('def test_'):
                # Add timeout decorator before test function
                indent = len(line) - len(line.lstrip())
                new_lines.append(' ' * indent + '@pytest.mark.timeout(30)')  # 30 second timeout
            new_lines.append(line)

        content = '\n'.join(new_lines)

    return content

def main():
    """Fix all API test files"""
    test_dir = '/home/admin-jairo/MeStore/tests/api'
    test_files = [
        'test_admin_orders_endpoints.py',
        'test_admin_vendor_management.py',
        'test_comisiones_detalle.py',
        'test_critical_endpoints_mvp.py',
        'test_orders_buyer.py',
        'test_pagos_historial.py',
        'test_productos_upload.py',
        'test_shipping_endpoints.py',
        'test_user_profile_fields.py',
        'test_user_roles_verification.py',
        'test_user_schemas_refactored.py',
        'test_vendedor_dashboard.py',
        'test_vendedores_login.py',
        'test_vendor_registration.py',
    ]

    fixed_count = 0
    for test_file in test_files:
        filepath = os.path.join(test_dir, test_file)
        if os.path.exists(filepath):
            print(f"Processing {test_file}...")
            try:
                fixed_content = add_pytest_timeout_to_file(filepath)
                # Don't write back for now, just analyze
                print(f"  ✓ Would add timeouts to {test_file}")
                fixed_count += 1
            except Exception as e:
                print(f"  ✗ Error processing {test_file}: {e}")
        else:
            print(f"  ⚠ File not found: {filepath}")

    print(f"\nProcessed {fixed_count}/{len(test_files)} files")
    return fixed_count == len(test_files)

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
