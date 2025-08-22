#!/usr/bin/env python3
"""
Standalone Safe Replace Tool - Fixed version for quote handling
Usage: python3 replace_safe_standalone.py <file> <old> <new>
"""
import shutil
import sys
from pathlib import Path


def safe_replace(target_file, old_content, new_content):
    """Replace content safely with intelligent quote handling"""

    # Read file content
    with open(target_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Create backup
    backup_path = f"{target_file}.safe_backup"
    shutil.copy2(target_file, backup_path)

    try:
        # Perform replacement
        new_file_content = content.replace(old_content, new_content)

        # Write back safely
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(new_file_content)

        # Verify Python syntax if applicable
        if target_file.endswith(".py"):
            import ast

            try:
                with open(target_file, "r") as f:
                    ast.parse(f.read())
                print("✅ Python syntax validated")
            except SyntaxError as e:
                print(f"⚠️ Syntax validation failed: {e}")
                print("💡 Tip: Use double quotes for values containing single quotes")
                # Rollback
                shutil.copy2(backup_path, target_file)
                Path(backup_path).unlink()
                return False

        # Remove backup if successful
        Path(backup_path).unlink()
        print(f"✅ Safe replacement completed: '{old_content}' -> '{new_content}'")
        return True

    except Exception as e:
        # Rollback on any error
        shutil.copy2(backup_path, target_file)
        Path(backup_path).unlink()
        print(f"❌ Operation failed, rolled back: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 replace_safe_standalone.py <file> <old> <new>")
        print(
            "Example: python3 replace_safe_standalone.py file.py 'old' 'new \"quoted\" value'"
        )
        sys.exit(1)

    target_file, old_content, new_content = sys.argv[1], sys.argv[2], sys.argv[3]
    success = safe_replace(target_file, old_content, new_content)
    sys.exit(0 if success else 1)
