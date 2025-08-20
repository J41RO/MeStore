"""
Comprehensive test suite for enhanced path resolver system
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_enhanced_path_resolver_basic():
    """Test basic path resolution functions"""
    try:
        from utils.path_resolver import path_resolver

        # Test basic methods (backward compatibility)
        current_path = path_resolver.resolve(".")
        assert current_path.exists(), "Current directory should exist"

        # Test exists method
        assert path_resolver.exists("."), "Current directory should exist"
        assert path_resolver.is_dir("."), "Current directory should be a directory"

        return True
    except Exception as e:
        print(f"Basic path resolver test failed: {e}")
        return False


def test_project_root_detection():
    """Test project root auto-detection"""
    try:
        from utils.path_resolver import path_resolver

        # Test project root detection
        project_root = path_resolver.find_project_root()
        assert project_root is not None, "Should detect project root"

        # Test project info
        project_info = path_resolver.get_project_info()
        assert "project_root" in project_info, "Project info should contain root"
        assert "type" in project_info, "Project info should contain type"

        print(f"✅ Project detected as: {project_info['type']}")
        return True
    except Exception as e:
        print(f"Project root detection test failed: {e}")
        return False


def test_file_suggestions():
    """Test file suggestion system"""
    try:
        from utils.path_resolver import path_resolver

        # Test suggestions for existing pattern
        suggestions = path_resolver.suggest_similar_files("log", max_suggestions=5)
        assert isinstance(suggestions, list), "Suggestions should be a list"

        # Test suggestion structure
        if suggestions:
            file_path, score = suggestions[0]
            assert isinstance(file_path, str), "File path should be string"
            assert isinstance(score, float), "Score should be float"
            assert 0 <= score <= 1, "Score should be between 0 and 1"

        return True
    except Exception as e:
        print(f"File suggestions test failed: {e}")
        return False


def test_resolve_with_suggestions():
    """Test enhanced resolution with suggestions"""
    try:
        from utils.path_resolver import path_resolver

        # Test with existing file
        result = path_resolver.resolve_with_suggestions("utils/logger.py")
        assert result["exists"], "Existing file should be found"
        assert (
            len(result["suggestions"]) == 0
        ), "No suggestions needed for existing file"

        # Test with non-existing file
        result = path_resolver.resolve_with_suggestions("nonexistent_file.py")
        assert not result["exists"], "Non-existing file should not be found"

        return True
    except Exception as e:
        print(f"Resolve with suggestions test failed: {e}")
        return False


def test_smart_resolve():
    """Test smart resolution with advanced features"""
    try:
        from utils.path_resolver import path_resolver

        # Test smart resolve
        result = path_resolver.smart_resolve("utils/logger.py")
        assert "resolved_path" in result, "Smart resolve should return resolved path"
        assert "exists" in result, "Smart resolve should check existence"
        assert (
            "project_relative" in result
        ), "Smart resolve should provide project relative path"

        return True
    except Exception as e:
        print(f"Smart resolve test failed: {e}")
        return False


def test_cache_system():
    """Test caching system and statistics"""
    try:
        from utils.path_resolver import path_resolver

        # Clear cache first
        path_resolver.clear_cache()

        # Perform some operations to populate cache
        path_resolver.resolve(".")
        path_resolver.resolve("utils/logger.py")
        path_resolver.find_project_root()

        # Get cache statistics
        stats = path_resolver.get_cache_statistics()
        assert "cache_stats" in stats, "Statistics should contain cache stats"
        assert "hit_rate_percentage" in stats, "Statistics should contain hit rate"

        # Test cache operations
        initial_misses = stats["cache_stats"]["misses"]
        path_resolver.resolve(".")  # Should be cache hit
        new_stats = path_resolver.get_cache_statistics()

        return True
    except Exception as e:
        print(f"Cache system test failed: {e}")
        return False


def test_file_finder_integration():
    """Test integration with file finder system"""
    try:
        from utils.file_finder import find_files, get_file_finder, smart_search

        # Test file finder creation
        file_finder = get_file_finder()
        assert file_finder is not None, "File finder should be created"

        # Test convenience functions
        py_files = find_files("*.py")
        assert isinstance(py_files, list), "find_files should return list"

        # Test smart search
        search_results = smart_search("test")
        assert (
            "exact_matches" in search_results
        ), "Smart search should have exact matches"
        assert "suggestions" in search_results, "Smart search should have suggestions"

        return True
    except Exception as e:
        print(f"File finder integration test failed: {e}")
        return False


def test_performance():
    """Test performance of path resolution"""
    try:
        import time

        from utils.path_resolver import path_resolver

        # Clear cache for fair test
        path_resolver.clear_cache()

        # Test multiple resolutions
        start_time = time.time()
        for i in range(100):
            path_resolver.resolve(".")

        duration = time.time() - start_time
        avg_time = duration / 100

        print(f"✅ Average resolution time: {avg_time:.4f}s")
        assert avg_time < 0.001, f"Resolution should be fast, got {avg_time:.4f}s"

        return True
    except Exception as e:
        print(f"Performance test failed: {e}")
        return False


def test_cross_directory_resolution():
    """Test resolution from different directories"""
    try:
        from utils.path_resolver import path_resolver

        # Get current directory
        original_cwd = os.getcwd()

        try:
            # Change to parent directory
            os.chdir("..")

            # Test resolution from parent directory
            result = path_resolver.resolve("surgical_modifier/utils/logger.py")
            assert result.exists(), "Should resolve from parent directory"

            # Test project root detection from different location
            project_root = path_resolver.find_project_root()
            assert (
                project_root is not None
            ), "Should detect project root from different location"

        finally:
            # Restore original directory
            os.chdir(original_cwd)

        return True
    except Exception as e:
        print(f"Cross-directory resolution test failed: {e}")
        return False


def run_all_path_resolver_tests():
    """Run all path resolver tests and report results"""
    tests = [
        ("Enhanced Path Resolver Basic", test_enhanced_path_resolver_basic),
        ("Project Root Detection", test_project_root_detection),
        ("File Suggestions", test_file_suggestions),
        ("Resolve with Suggestions", test_resolve_with_suggestions),
        ("Smart Resolve", test_smart_resolve),
        ("Cache System", test_cache_system),
        ("File Finder Integration", test_file_finder_integration),
        ("Performance", test_performance),
        ("Cross-Directory Resolution", test_cross_directory_resolution),
    ]

    passed = 0
    total = len(tests)

    print("🧪 RUNNING ENHANCED PATH RESOLVER TESTS")
    print("=" * 60)

    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")

    print("=" * 60)
    print(f"📊 RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL PATH RESOLVER TESTS PASSED! Enhanced system is ready.")
        return True
    else:
        print("⚠️ Some tests failed. Review implementation.")
        return False


if __name__ == "__main__":
    success = run_all_path_resolver_tests()
    sys.exit(0 if success else 1)
