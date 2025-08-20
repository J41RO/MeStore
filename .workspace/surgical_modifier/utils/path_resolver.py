"""
Surgical Modifier v6.0 - Enhanced Global Path Resolver
Resolve paths from anywhere in the system with intelligent project detection
"""

import difflib
import fnmatch
import os
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class EnhancedGlobalPathResolver:
    """
    Enhanced global path resolver with intelligent features:
    - Auto-detection of project root
    - File suggestions for similar patterns
    - Intelligent caching with statistics
    - Performance monitoring
    - Cross-platform compatibility
    """

    def __init__(self):
        self.cache = {}
        self.cache_stats = {"hits": 0, "misses": 0, "total_lookups": 0, "cache_size": 0}
        self.project_roots_cache = {}
        self.suggestion_cache = {}
        self.performance_stats = defaultdict(list)

        # Project root indicators (ordered by priority)
        self.project_indicators = [
            # Python projects
            "pyproject.toml",
            "setup.py",
            "setup.cfg",
            "requirements.txt",
            "Pipfile",
            "poetry.lock",
            "conda.yml",
            "environment.yml",
            # JavaScript/Node.js projects
            "package.json",
            "package-lock.json",
            "yarn.lock",
            "node_modules",
            "webpack.config.js",
            "vite.config.js",
            "next.config.js",
            # Java projects
            "pom.xml",
            "build.gradle",
            "gradle.properties",
            "maven.xml",
            # Other common indicators
            ".git",
            ".gitignore",
            "README.md",
            "README.rst",
            "README.txt",
            "Makefile",
            "Dockerfile",
            "docker-compose.yml",
            ".env",
            ".env.example",
            "LICENSE",
            "CHANGELOG.md",
        ]

    # ========== BACKWARD COMPATIBLE METHODS ==========

    def resolve(self, path_str: str) -> Path:
        """
        Resolve path string to absolute path (enhanced version)
        Works from any current working directory with intelligent detection
        """
        start_time = time.time()
        cache_key = f"resolve:{path_str}:{os.getcwd()}"

        # Check cache first
        if cache_key in self.cache:
            self.cache_stats["hits"] += 1
            self.cache_stats["total_lookups"] += 1
            return self.cache[cache_key]

        # Cache miss
        self.cache_stats["misses"] += 1
        self.cache_stats["total_lookups"] += 1

        path = Path(path_str)

        # Enhanced resolution logic
        if path.is_absolute():
            resolved = path
        else:
            # Try relative to current working directory first
            resolved = Path.cwd() / path

            # If not found, try relative to project root
            if not resolved.exists():
                project_root = self.find_project_root()
                if project_root:
                    alt_resolved = project_root / path
                    if alt_resolved.exists():
                        resolved = alt_resolved

        # Cache result
        self.cache[cache_key] = resolved
        self.cache_stats["cache_size"] = len(self.cache)

        # Performance tracking
        duration = time.time() - start_time
        self.performance_stats["resolve_times"].append(duration)

        return resolved

    def exists(self, path_str: str) -> bool:
        """Check if path exists"""
        return self.resolve(path_str).exists()

    def is_file(self, path_str: str) -> bool:
        """Check if path is a file"""
        return self.resolve(path_str).is_file()

    def is_dir(self, path_str: str) -> bool:
        """Check if path is a directory"""
        return self.resolve(path_str).is_dir()

    # ========== NEW ENHANCED FEATURES ==========

    def find_project_root(self, start_path: Optional[Path] = None) -> Optional[Path]:
        """
        Find project root by looking for common indicators
        Caches results for performance
        """
        if start_path is None:
            start_path = Path.cwd()

        cache_key = str(start_path.absolute())
        if cache_key in self.project_roots_cache:
            return self.project_roots_cache[cache_key]

        current = start_path.absolute()

        # Traverse up the directory tree
        while current != current.parent:
            # Check for project indicators
            for indicator in self.project_indicators:
                indicator_path = current / indicator
                if indicator_path.exists():
                    # Cache result
                    self.project_roots_cache[cache_key] = current
                    return current
            current = current.parent

        # No project root found
        self.project_roots_cache[cache_key] = None
        return None

    def get_project_info(self) -> Dict[str, any]:
        """Get detailed information about current project"""
        project_root = self.find_project_root()
        if not project_root:
            return {"project_root": None, "indicators": [], "type": "unknown"}

        found_indicators = []
        project_type = "unknown"

        for indicator in self.project_indicators:
            if (project_root / indicator).exists():
                found_indicators.append(indicator)

        # Determine project type based on indicators
        if any(
            ind in found_indicators
            for ind in ["pyproject.toml", "setup.py", "requirements.txt"]
        ):
            project_type = "python"
        elif any(ind in found_indicators for ind in ["package.json", "node_modules"]):
            project_type = "javascript"
        elif any(ind in found_indicators for ind in ["pom.xml", "build.gradle"]):
            project_type = "java"
        elif ".git" in found_indicators:
            project_type = "git_repository"

        return {
            "project_root": project_root,
            "indicators": found_indicators,
            "type": project_type,
            "size_mb": self._calculate_project_size(project_root),
        }

    def suggest_similar_files(
        self, pattern: str, max_suggestions: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Suggest files similar to the given pattern
        Returns list of (file_path, similarity_score) tuples
        """
        cache_key = f"suggest:{pattern}:{max_suggestions}"
        if cache_key in self.suggestion_cache:
            return self.suggestion_cache[cache_key]

        project_root = self.find_project_root()
        search_root = project_root if project_root else Path.cwd()

        # Find all relevant files
        all_files = []
        try:
            for file_path in search_root.rglob("*"):
                if file_path.is_file() and not self._should_ignore_file(file_path):
                    # Store relative path from search root
                    rel_path = file_path.relative_to(search_root)
                    all_files.append(str(rel_path))
        except (PermissionError, OSError):
            # Handle permission errors gracefully
            pass

        # Calculate similarity scores
        suggestions = []
        pattern_lower = pattern.lower()

        for file_path in all_files:
            file_lower = file_path.lower()

            # Multiple similarity metrics
            scores = []

            # 1. Exact substring match
            if pattern_lower in file_lower:
                scores.append(0.9)

            # 2. Filename similarity (difflib)
            filename_sim = difflib.SequenceMatcher(
                None, pattern_lower, Path(file_path).name.lower()
            ).ratio()
            scores.append(filename_sim * 0.8)

            # 3. Path similarity
            path_sim = difflib.SequenceMatcher(None, pattern_lower, file_lower).ratio()
            scores.append(path_sim * 0.6)

            # 4. Extension match bonus
            if Path(pattern).suffix and Path(pattern).suffix == Path(file_path).suffix:
                scores.append(0.7)

            # Use maximum score
            final_score = max(scores) if scores else 0

            if final_score > 0.3:  # Minimum threshold
                suggestions.append((file_path, final_score))

        # Sort by score and limit results
        suggestions.sort(key=lambda x: x[1], reverse=True)
        result = suggestions[:max_suggestions]

        # Cache result
        self.suggestion_cache[cache_key] = result
        return result

    def resolve_with_suggestions(self, path_str: str) -> Dict[str, any]:
        """
        Resolve path and provide suggestions if not found
        """
        resolved_path = self.resolve(path_str)

        result = {
            "resolved_path": resolved_path,
            "exists": resolved_path.exists(),
            "suggestions": [],
        }

        # If file doesn't exist, provide suggestions
        if not resolved_path.exists():
            suggestions = self.suggest_similar_files(path_str)
            result["suggestions"] = suggestions

        return result

    def smart_resolve(
        self, path_str: str, create_missing_dirs: bool = False
    ) -> Dict[str, any]:
        """
        Smart resolution with advanced features
        """
        start_time = time.time()

        # Basic resolution
        resolved_path = self.resolve(path_str)
        exists = resolved_path.exists()

        result = {
            "resolved_path": resolved_path,
            "exists": exists,
            "is_file": resolved_path.is_file() if exists else None,
            "is_dir": resolved_path.is_dir() if exists else None,
            "suggestions": [],
            "project_relative": None,
            "created_dirs": [],
        }

        # Add project-relative path
        project_root = self.find_project_root()
        if project_root:
            try:
                result["project_relative"] = str(
                    resolved_path.relative_to(project_root)
                )
            except ValueError:
                result["project_relative"] = None

        # Create missing directories if requested
        if create_missing_dirs and not exists:
            parent_dir = resolved_path.parent
            if not parent_dir.exists():
                try:
                    parent_dir.mkdir(parents=True, exist_ok=True)
                    result["created_dirs"].append(str(parent_dir))
                except (PermissionError, OSError) as e:
                    result["error"] = str(e)

        # Provide suggestions if not found
        if not exists:
            result["suggestions"] = self.suggest_similar_files(path_str)

        # Performance tracking
        duration = time.time() - start_time
        self.performance_stats["smart_resolve_times"].append(duration)

        return result

    def get_cache_statistics(self) -> Dict[str, any]:
        """Get detailed cache statistics"""
        hit_rate = (
            self.cache_stats["hits"] / max(self.cache_stats["total_lookups"], 1)
        ) * 100

        return {
            "cache_stats": self.cache_stats.copy(),
            "hit_rate_percentage": round(hit_rate, 2),
            "average_resolve_time": (
                round(
                    sum(self.performance_stats["resolve_times"])
                    / max(len(self.performance_stats["resolve_times"]), 1),
                    4,
                )
                if self.performance_stats["resolve_times"]
                else 0
            ),
            "project_roots_cached": len(self.project_roots_cache),
            "suggestions_cached": len(self.suggestion_cache),
        }

    def clear_cache(self, cache_type: str = "all"):
        """Clear specific or all caches"""
        if cache_type in ["all", "resolve"]:
            self.cache.clear()
            self.cache_stats["cache_size"] = 0

        if cache_type in ["all", "project_roots"]:
            self.project_roots_cache.clear()

        if cache_type in ["all", "suggestions"]:
            self.suggestion_cache.clear()

    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored in suggestions"""
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
        ]

        file_str = str(file_path)
        return any(fnmatch.fnmatch(file_str, pattern) for pattern in ignore_patterns)

    def _calculate_project_size(self, project_root: Path) -> float:
        """Calculate project size in MB"""
        try:
            total_size = sum(
                f.stat().st_size
                for f in project_root.rglob("*")
                if f.is_file() and not self._should_ignore_file(f)
            )
            return round(total_size / (1024 * 1024), 2)
        except (PermissionError, OSError):
            return 0.0


# Global enhanced path resolver instance
path_resolver = EnhancedGlobalPathResolver()

# Maintain backward compatibility
GlobalPathResolver = EnhancedGlobalPathResolver
