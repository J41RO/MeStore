#!/usr/bin/env python3
"""
MeStore Pydantic V2 Migration Script
===================================

Automated migration script to convert Pydantic V1 syntax to V2 syntax
across all schema files in the MeStore application.

Usage:
    python scripts/migrate_pydantic_v2.py [--dry-run] [--file specific_file.py]

Author: Technical Debt Manager AI
Date: 2025-09-18
"""

import os
import re
import sys
import argparse
import shutil
from pathlib import Path
from typing import List, Dict, Tuple


class PydanticV2Migrator:
    """Automated Pydantic V1 to V2 migration tool"""

    def __init__(self, schemas_dir: str = "app/schemas", backup_dir: str = "app/schemas.backup"):
        self.schemas_dir = Path(schemas_dir)
        self.backup_dir = Path(backup_dir)
        self.migration_log = []

    def backup_schemas(self) -> bool:
        """Create backup of current schemas directory"""
        try:
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
            shutil.copytree(self.schemas_dir, self.backup_dir)
            print(f"✅ Backup created at {self.backup_dir}")
            return True
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False

    def get_schema_files(self, specific_file: str = None) -> List[Path]:
        """Get list of Python schema files to migrate"""
        if specific_file:
            file_path = self.schemas_dir / specific_file
            if file_path.exists():
                return [file_path]
            else:
                print(f"❌ File {specific_file} not found")
                return []

        # Get all Python files except __pycache__ and __init__.py
        files = []
        for file_path in self.schemas_dir.rglob("*.py"):
            if "__pycache__" not in str(file_path) and file_path.name != "__init__.py":
                files.append(file_path)
        return files

    def migrate_imports(self, content: str) -> Tuple[str, List[str]]:
        """Migrate Pydantic imports from V1 to V2"""
        changes = []

        # Add ConfigDict import if Config class is found and ConfigDict not already imported
        if "class Config:" in content and "ConfigDict" not in content:
            # Find the pydantic import line
            import_pattern = r'^from pydantic import (.+)$'

            def add_configdict(match):
                imports = match.group(1)
                if "ConfigDict" not in imports:
                    changes.append("Added ConfigDict import")
                    return f"from pydantic import {imports}, ConfigDict"
                return match.group(0)

            content = re.sub(import_pattern, add_configdict, content, flags=re.MULTILINE)

        # Add field_validator import if @validator is found
        if "@validator" in content and "field_validator" not in content:
            import_pattern = r'^from pydantic import (.+)$'

            def add_field_validator(match):
                imports = match.group(1)
                if "field_validator" not in imports:
                    changes.append("Added field_validator import")
                    return f"from pydantic import {imports}, field_validator"
                return match.group(0)

            content = re.sub(import_pattern, add_field_validator, content, flags=re.MULTILINE)

        return content, changes

    def migrate_config_class(self, content: str) -> Tuple[str, List[str]]:
        """Migrate Config class to model_config"""
        changes = []

        # Pattern to match Config class
        config_pattern = r'(\s+)class Config:\s*\n((?:\1\s+.+\n)*)'

        def replace_config(match):
            indent = match.group(1)
            config_content = match.group(2)

            # Extract config attributes
            attributes = []
            for line in config_content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    attributes.append(line)

            if attributes:
                changes.append("Migrated Config class to model_config")
                formatted_attrs = ',\n        '.join(attributes)
                return f'{indent}model_config = ConfigDict(\n        {formatted_attrs}\n{indent})'

            return match.group(0)

        new_content = re.sub(config_pattern, replace_config, content, flags=re.MULTILINE)
        return new_content, changes

    def migrate_validators(self, content: str) -> Tuple[str, List[str]]:
        """Migrate @validator to @field_validator"""
        changes = []

        # Pattern for validator decorators and methods
        validator_pattern = r'(\s+)@validator\(([^)]+)\)\s*\n(\s+)def (\w+)\(cls, v(?:, values)?\):'

        def replace_validator(match):
            indent = match.group(1)
            validator_args = match.group(2)
            method_indent = match.group(3)
            method_name = match.group(4)

            changes.append(f"Migrated @validator for {method_name}")

            # Add @classmethod decorator and update to @field_validator
            return f'{indent}@field_validator({validator_args})\n{indent}@classmethod\n{method_indent}def {method_name}(cls, v):'

        new_content = re.sub(validator_pattern, replace_validator, content, flags=re.MULTILINE | re.DOTALL)

        # Handle validators that use 'values' parameter (need manual review)
        if ', values' in content:
            changes.append("⚠️  WARNING: Found validators using 'values' parameter - manual review required")

        return new_content, changes

    def migrate_json_schema_extra(self, content: str) -> Tuple[str, List[str]]:
        """Update json_schema_extra syntax if needed"""
        changes = []

        # This is mostly compatible, but we can add warnings for deprecated patterns
        if 'schema_extra' in content and 'json_schema_extra' not in content:
            changes.append("⚠️  WARNING: Found 'schema_extra' - should be 'json_schema_extra'")

        return content, changes

    def migrate_file(self, file_path: Path, dry_run: bool = False) -> Dict:
        """Migrate a single schema file"""
        print(f"\n📁 Processing: {file_path.relative_to(self.schemas_dir)}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            content = original_content
            all_changes = []

            # Apply migrations
            content, changes = self.migrate_imports(content)
            all_changes.extend(changes)

            content, changes = self.migrate_config_class(content)
            all_changes.extend(changes)

            content, changes = self.migrate_validators(content)
            all_changes.extend(changes)

            content, changes = self.migrate_json_schema_extra(content)
            all_changes.extend(changes)

            # Check if any changes were made
            if content != original_content and not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print("✅ File updated")
            elif content != original_content:
                print("🔍 Would be updated (dry run mode)")
            else:
                print("ℹ️  No changes needed")

            # Display changes
            for change in all_changes:
                if change.startswith("⚠️"):
                    print(f"  {change}")
                else:
                    print(f"  ✓ {change}")

            return {
                'file': str(file_path),
                'success': True,
                'changes': all_changes,
                'modified': content != original_content
            }

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return {
                'file': str(file_path),
                'success': False,
                'error': str(e),
                'changes': [],
                'modified': False
            }

    def generate_migration_report(self, results: List[Dict]) -> str:
        """Generate a detailed migration report"""
        report_lines = [
            "# Pydantic V2 Migration Report",
            f"# Generated: {Path.cwd()}",
            f"# Total files processed: {len(results)}",
            "",
            "## Summary",
        ]

        successful = sum(1 for r in results if r['success'])
        modified = sum(1 for r in results if r.get('modified', False))
        errors = sum(1 for r in results if not r['success'])

        report_lines.extend([
            f"- ✅ Successfully processed: {successful}/{len(results)}",
            f"- 🔄 Modified files: {modified}",
            f"- ❌ Errors: {errors}",
            "",
            "## File Details",
        ])

        for result in results:
            file_name = Path(result['file']).name
            if result['success']:
                status = "✅ SUCCESS" if result.get('modified') else "ℹ️  NO CHANGES"
                report_lines.append(f"### {file_name} - {status}")

                if result['changes']:
                    report_lines.append("Changes made:")
                    for change in result['changes']:
                        report_lines.append(f"- {change}")
                else:
                    report_lines.append("- No migration needed")
            else:
                report_lines.append(f"### {file_name} - ❌ ERROR")
                report_lines.append(f"Error: {result.get('error', 'Unknown error')}")

            report_lines.append("")

        # Add manual review section if needed
        warnings = []
        for result in results:
            for change in result.get('changes', []):
                if change.startswith("⚠️"):
                    warnings.append(f"- {Path(result['file']).name}: {change}")

        if warnings:
            report_lines.extend([
                "## ⚠️  Manual Review Required",
                "",
                "The following files require manual review:",
                ""
            ])
            report_lines.extend(warnings)

        return '\n'.join(report_lines)

    def run_migration(self, dry_run: bool = False, specific_file: str = None) -> bool:
        """Run the complete migration process"""
        print("🚀 Starting Pydantic V2 Migration")
        print(f"📂 Target directory: {self.schemas_dir}")

        if dry_run:
            print("🔍 DRY RUN MODE - No files will be modified")

        # Create backup (only if not dry run)
        if not dry_run and not self.backup_schemas():
            return False

        # Get files to migrate
        files = self.get_schema_files(specific_file)
        if not files:
            print("❌ No schema files found to migrate")
            return False

        print(f"📋 Found {len(files)} files to process")

        # Migrate each file
        results = []
        for file_path in files:
            result = self.migrate_file(file_path, dry_run)
            results.append(result)

        # Generate and save report
        report = self.generate_migration_report(results)
        report_path = Path("migration_report.md")

        if not dry_run:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n📊 Migration report saved to: {report_path}")
        else:
            print("\n📊 Migration Report (dry run):")
            print(report)

        # Summary
        successful = sum(1 for r in results if r['success'])
        modified = sum(1 for r in results if r.get('modified', False))

        print(f"\n🎉 Migration completed!")
        print(f"✅ {successful}/{len(results)} files processed successfully")
        print(f"🔄 {modified} files modified")

        if modified > 0 and not dry_run:
            print("\n📝 Next steps:")
            print("1. Run tests: python -m pytest tests/")
            print("2. Check API docs: uvicorn app.main:app --reload")
            print("3. Review any warnings in the migration report")
            print("4. Commit changes: git add . && git commit -m 'feat: migrate to Pydantic V2'")

        return True


def main():
    """Main migration script entry point"""
    parser = argparse.ArgumentParser(description="Migrate MeStore Pydantic schemas from V1 to V2")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without modifying files")
    parser.add_argument("--file", help="Migrate specific file only (relative to schemas directory)")
    parser.add_argument("--schemas-dir", default="app/schemas", help="Path to schemas directory")

    args = parser.parse_args()

    # Check if we're in the correct directory
    if not Path(args.schemas_dir).exists():
        print(f"❌ Schemas directory not found: {args.schemas_dir}")
        print("Please run this script from the MeStore root directory")
        sys.exit(1)

    # Initialize migrator
    migrator = PydanticV2Migrator(schemas_dir=args.schemas_dir)

    # Run migration
    success = migrator.run_migration(dry_run=args.dry_run, specific_file=args.file)

    if not success:
        print("❌ Migration failed")
        sys.exit(1)

    print("✅ Migration completed successfully")


if __name__ == "__main__":
    main()