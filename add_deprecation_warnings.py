#!/usr/bin/env python3
"""
Script to add deprecation warnings to Spanish API endpoints.
"""

deprecation_mappings = {
    'app/api/v1/endpoints/vendedores.py': '/api/v1/vendors/',
    'app/api/v1/endpoints/comisiones.py': '/api/v1/commissions/',
}

deprecation_header = """
# ⚠️⚠️⚠️ DEPRECATED ENDPOINTS - WILL BE REMOVED IN v2.0.0 ⚠️⚠️⚠️
#
# These Spanish endpoints are DEPRECATED and will be removed in v2.0.0
# Please migrate to {english_endpoint} instead
#
# Migration guide: See SAFE_API_MIGRATION_STRATEGY.md
# Timeline: These endpoints will be removed after 3 weeks (2025-10-22)
#
"""

for file_path, english_endpoint in deprecation_mappings.items():
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find the first import or meaningful line after headers
        lines = content.split('\n')
        insert_position = 0

        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                insert_position = i
                break

        # Insert deprecation warning before imports
        deprecation_text = deprecation_header.format(english_endpoint=english_endpoint)
        lines.insert(insert_position, deprecation_text)

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"✅ Added deprecation warning to {file_path}")
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")

print("\n✅ All deprecation warnings added successfully!")
