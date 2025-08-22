"""
Safe Replace Operation for CLI v6.0
Handles quotes and special characters correctly
"""

import re
import shutil
from pathlib import Path


class SafeReplace:
    """Safe replacement that doesnt create literal escapes"""

    def __init__(self, console):
        self.console = console

    def safe_replace(self, target_file, old_content, new_content):
        """Replace content safely without literal escaping"""

        # Read file content
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Create backup
        backup_path = f"{target_file}.safe_backup"
        shutil.copy2(target_file, backup_path)

        try:
            # Perform replacement without literal escaping
            new_file_content = content.replace(old_content, new_content)

            # Validate the replacement worked
            if old_content in new_file_content:
                self.console.print(
                    f"⚠️ Warning: Some instances of {old_content} may remain"
                )

            # Write back safely
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(new_file_content)

            # Verify Python syntax if applicable
            if target_file.endswith(".py"):
                import ast

                try:
                    with open(target_file, "r") as f:
                        ast.parse(f.read())
                    self.console.print("✅ Python syntax validated")
                except SyntaxError as e:
                    self.console.print(f"❌ Syntax error after replacement: {e}")
                    # Rollback
                    shutil.copy2(backup_path, target_file)
                    raise e

            # Remove backup if successful
            Path(backup_path).unlink()
            return True

        except Exception as e:
            # Rollback on any error
            shutil.copy2(backup_path, target_file)
            Path(backup_path).unlink()
            self.console.print(f"❌ Operation failed, rolled back: {e}")
            return False
