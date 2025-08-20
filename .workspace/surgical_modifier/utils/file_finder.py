"""
Surgical Modifier v6.0 - Advanced File Finder System
Intelligent file search and discovery utilities
"""

import difflib
import fnmatch
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class AdvancedFileFinder:
    """
    Advanced file finding with intelligent search capabilities
    """

    def __init__(self, path_resolver):
        self.path_resolver = path_resolver
        self.search_cache = {}

    def find_files_by_pattern(
        self, pattern: str, search_root: Optional[Path] = None
    ) -> List[Path]:
        """
        Find files matching a glob pattern
        """
        if search_root is None:
            search_root = self.path_resolver.find_project_root() or Path.cwd()

        cache_key = f"pattern:{pattern}:{search_root}"
        if cache_key in self.search_cache:
            return self.search_cache[cache_key]

        matching_files = []
        try:
            for file_path in search_root.rglob(pattern):
                if file_path.is_file() and not self._should_ignore_file(file_path):
                    matching_files.append(file_path)
        except (PermissionError, OSError):
            pass

        # Cache results
        self.search_cache[cache_key] = matching_files
        return matching_files

    def find_files_by_content(
        self, content_pattern: str, file_extensions: List[str] = None
    ) -> List[Tuple[Path, List[str]]]:
        """
        Find files containing specific content
        Returns list of (file_path, matching_lines) tuples
        """
        if file_extensions is None:
            file_extensions = [".py", ".js", ".ts", ".jsx", ".tsx", ".txt", ".md"]

        project_root = self.path_resolver.find_project_root() or Path.cwd()
        results = []

        # Compile regex for performance
        try:
            content_regex = re.compile(content_pattern, re.IGNORECASE)
        except re.error:
            # If regex is invalid, use simple string search
            content_regex = None

        for ext in file_extensions:
            for file_path in project_root.rglob(f"*{ext}"):
                if not file_path.is_file() or self._should_ignore_file(file_path):
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        matching_lines = []
                        for line_num, line in enumerate(f, 1):
                            if content_regex:
                                if content_regex.search(line):
                                    matching_lines.append(f"{line_num}: {line.strip()}")
                            else:
                                if content_pattern.lower() in line.lower():
                                    matching_lines.append(f"{line_num}: {line.strip()}")

                        if matching_lines:
                            results.append((file_path, matching_lines))

                except (UnicodeDecodeError, PermissionError):
                    continue

        return results

    def find_similar_structure(self, reference_file: Path) -> List[Tuple[Path, float]]:
        """
        Find files with similar directory structure or naming patterns
        """
        project_root = self.path_resolver.find_project_root() or Path.cwd()

        try:
            ref_relative = reference_file.relative_to(project_root)
        except ValueError:
            return []

        ref_parts = ref_relative.parts
        ref_name = reference_file.name
        ref_suffix = reference_file.suffix

        similar_files = []

        for file_path in project_root.rglob("*"):
            if not file_path.is_file() or file_path == reference_file:
                continue

            try:
                file_relative = file_path.relative_to(project_root)
                file_parts = file_relative.parts

                # Calculate structural similarity
                structure_score = self._calculate_structure_similarity(
                    ref_parts, file_parts
                )

                # Calculate name similarity
                name_score = difflib.SequenceMatcher(
                    None, ref_name, file_path.name
                ).ratio()

                # Suffix bonus
                suffix_bonus = 0.3 if file_path.suffix == ref_suffix else 0

                # Combined score
                final_score = (
                    (structure_score * 0.5) + (name_score * 0.3) + suffix_bonus
                )

                if final_score > 0.3:
                    similar_files.append((file_path, final_score))

            except ValueError:
                continue

        # Sort by similarity score
        similar_files.sort(key=lambda x: x[1], reverse=True)
        return similar_files[:10]  # Top 10 similar files

    def find_related_files(self, base_file: Path) -> Dict[str, List[Path]]:
        """
        Find files related to the base file (tests, configs, etc.)
        """
        base_name = base_file.stem
        base_suffix = base_file.suffix
        project_root = self.path_resolver.find_project_root() or Path.cwd()

        related = {
            "tests": [],
            "configs": [],
            "similar_names": [],
            "same_directory": [],
            "imports": [],
        }

        # Find test files
        test_patterns = [
            f"test_{base_name}.*",
            f"*_test.*",
            f"{base_name}_test.*",
            f"test*.{base_name}.*",
        ]

        for pattern in test_patterns:
            related["tests"].extend(self.find_files_by_pattern(pattern))

        # Find config files
        config_patterns = [
            f"{base_name}.config.*",
            f"{base_name}.conf.*",
            f"config.{base_name}.*",
            f"{base_name}.json",
            f"{base_name}.yml",
            f"{base_name}.yaml",
        ]

        for pattern in config_patterns:
            related["configs"].extend(self.find_files_by_pattern(pattern))

        # Find files in same directory
        if base_file.parent.exists():
            for file_path in base_file.parent.iterdir():
                if file_path.is_file() and file_path != base_file:
                    related["same_directory"].append(file_path)

        # Find files with similar names
        similar_pattern = f"{base_name}*{base_suffix}"
        related["similar_names"] = self.find_files_by_pattern(similar_pattern)

        # Remove duplicates and base file
        for category in related:
            related[category] = list(set(related[category]))
            if base_file in related[category]:
                related[category].remove(base_file)

        return related

    def smart_file_search(self, query: str) -> Dict[str, List]:
        """
        Intelligent file search combining multiple strategies
        """
        results = {
            "exact_matches": [],
            "pattern_matches": [],
            "content_matches": [],
            "similar_names": [],
            "suggestions": [],
        }

        # Exact filename matches
        exact_files = self.find_files_by_pattern(query)
        results["exact_matches"] = exact_files

        # Pattern matches (with wildcards)
        if "*" in query or "?" in query:
            pattern_files = self.find_files_by_pattern(query)
            results["pattern_matches"] = pattern_files
        else:
            # Add implicit wildcards
            pattern_files = self.find_files_by_pattern(f"*{query}*")
            results["pattern_matches"] = pattern_files

        # Content search (if query looks like code)
        if len(query) > 3 and any(
            char in query for char in ["(", ")", "{", "}", "def ", "class ", "function"]
        ):
            content_matches = self.find_files_by_content(query)
            results["content_matches"] = [
                (path, lines[:3]) for path, lines in content_matches
            ]  # Limit lines

        # Similar names using path resolver
        suggestions = self.path_resolver.suggest_similar_files(
            query, max_suggestions=10
        )
        results["suggestions"] = suggestions

        return results

    def _calculate_structure_similarity(self, parts1: Tuple, parts2: Tuple) -> float:
        """Calculate similarity between directory structures"""
        if not parts1 or not parts2:
            return 0.0

        # Compare directory depth
        depth_diff = abs(len(parts1) - len(parts2))
        depth_score = max(0, 1 - (depth_diff * 0.2))

        # Compare common path elements
        common_parts = 0
        min_len = min(len(parts1), len(parts2))

        for i in range(min_len):
            if parts1[i] == parts2[i]:
                common_parts += 1
            else:
                break  # Stop at first difference

        path_score = common_parts / max(len(parts1), len(parts2))

        return (depth_score + path_score) / 2

    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored in searches"""
        ignore_patterns = [
            "__pycache__",
            ".git",
            ".venv",
            "node_modules",
            ".pytest_cache",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".DS_Store",
            "Thumbs.db",
            "*.log",
            "*.tmp",
            "*.temp",
            ".backup",
            "*.min.js",
            "*.min.css",
        ]

        file_str = str(file_path)
        return any(fnmatch.fnmatch(file_str, pattern) for pattern in ignore_patterns)


# Create global file finder instance
def create_file_finder():
    """Create file finder instance with path resolver"""
    from utils.path_resolver import path_resolver

    return AdvancedFileFinder(path_resolver)


# Global file finder (lazy initialization)
_file_finder = None


def get_file_finder():
    """Get global file finder instance"""
    global _file_finder
    if _file_finder is None:
        _file_finder = create_file_finder()
    return _file_finder


# Convenience functions
def find_files(pattern: str) -> List[Path]:
    """Convenience function for pattern-based file finding"""
    return get_file_finder().find_files_by_pattern(pattern)


def search_content(pattern: str) -> List[Tuple[Path, List[str]]]:
    """Convenience function for content-based search"""
    return get_file_finder().find_files_by_content(pattern)


def smart_search(query: str) -> Dict[str, List]:
    """Convenience function for smart file search"""
    return get_file_finder().smart_file_search(query)
