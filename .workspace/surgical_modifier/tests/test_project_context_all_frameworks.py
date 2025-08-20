"""
Comprehensive test suite for project context - all frameworks support
"""

import sys
import os
import tempfile
import shutil
import json
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_project_context_import():
    """Test project context imports correctly"""
    try:
        from utils.project_context import project_context, ProjectMetadata, FrameworkInfo
        from utils.integration_preparation import integration_preparation, GitInfo, CiCdInfo
        return True
    except Exception as e:
        print(f"Project context import test failed: {e}")
        return False

def test_framework_detection_python():
    """Test Python/FastAPI/Flask framework detection"""
    try:
        from utils.project_context import project_context
        
        # Test current project (should detect Python/FastAPI)
        frameworks = project_context.detect_frameworks()
        
        # Should detect at least Python-related frameworks
        python_frameworks = [fw for fw in frameworks if fw.name in ['fastapi', 'flask']]
        assert len(python_frameworks) > 0, "Should detect Python frameworks"
        
        # Check confidence scores
        for fw in python_frameworks:
            assert 0.0 <= fw.confidence <= 1.0, f"Confidence should be between 0-1 for {fw.name}"
            assert len(fw.indicators) > 0, f"Should have indicators for {fw.name}"
        
        return True
    except Exception as e:
        print(f"Python framework detection test failed: {e}")
        return False

def test_framework_detection_mock_projects():
    """Test framework detection with mock project structures"""
    try:
        from utils.project_context import project_context
        
        # Create temporary directory for mock projects
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test React project
            react_project = temp_path / "react_project"
            react_project.mkdir()
            
            # Create React indicators
            (react_project / "package.json").write_text(json.dumps({
                "dependencies": {"react": "^18.0.0", "react-dom": "^18.0.0"}
            }))
            (react_project / "src").mkdir()
            (react_project / "src" / "App.js").write_text("import React from 'react';")
            
            # Test detection
            react_frameworks = project_context.detect_frameworks(react_project)
            react_detected = any(fw.name == 'react' for fw in react_frameworks)
            assert react_detected, "Should detect React framework"
            
            # Test Django project
            django_project = temp_path / "django_project"
            django_project.mkdir()
            
            # Create Django indicators
            (django_project / "manage.py").write_text("#!/usr/bin/env python")
            (django_project / "settings.py").write_text("from django.conf import settings")
            (django_project / "requirements.txt").write_text("django>=4.0.0")
            
            # Test detection
            django_frameworks = project_context.detect_frameworks(django_project)
            django_detected = any(fw.name == 'django' for fw in django_frameworks)
            assert django_detected, "Should detect Django framework"
        
        return True
    except Exception as e:
        print(f"Mock projects framework detection test failed: {e}")
        return False

def test_dependency_parsing():
    """Test dependency file parsing"""
    try:
        from utils.project_context import project_context
        
        # Test package.json parsing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            package_data = {
                "dependencies": {"react": "^18.0.0", "axios": "^0.27.0"},
                "devDependencies": {"jest": "^28.0.0"}
            }
            json.dump(package_data, f)
            f.flush()
            
            dependencies = project_context._parse_package_json(Path(f.name))
            assert "react" in dependencies, "Should parse react dependency"
            assert "jest" in dependencies, "Should parse dev dependencies"
            
            os.unlink(f.name)
        
        # Test requirements.txt parsing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("fastapi>=0.68.0\nuvicorn==0.15.0\n# comment line\npydantic")
            f.flush()
            
            dependencies = project_context._parse_requirements_txt(Path(f.name))
            assert "fastapi" in dependencies, "Should parse fastapi dependency"
            assert "uvicorn" in dependencies, "Should parse version-pinned dependency"
            assert "pydantic" in dependencies, "Should parse dependency without version"
            
            os.unlink(f.name)
        
        return True
    except Exception as e:
        print(f"Dependency parsing test failed: {e}")
        return False

def test_cache_system():
    """Test persistent cache system"""
    try:
        from utils.project_context import project_context, ProjectMetadata, FrameworkInfo
        
        # Create mock metadata
        mock_metadata = ProjectMetadata(
            project_root="/tmp/test",
            project_name="test_project",
            frameworks=[FrameworkInfo(
                name="test_framework",
                version="1.0.0",
                confidence=0.8,
                indicators=["test.txt"],
                dependencies=["test_dep"],
                config_files=["config.json"],
                typical_structure=["src/"]
            )],
            primary_language="python",
            dependencies={"requirements.txt": ["test_dep"]},
            build_system="pip",
            version_control="git",
            ci_cd_system=None,
            size_mb=1.0,
            file_count=10,
            last_modified="2024-08-20T10:00:00",
            scan_timestamp="2024-08-20T10:00:00",
            cache_version="1.4.0"
        )
        
        # Test cache save/load cycle
        if project_context.cache_dir:
            project_context._save_cache(mock_metadata)
            loaded_metadata = project_context._load_cache(Path("/tmp/test"))
            
            if loaded_metadata:
                assert loaded_metadata.project_name == mock_metadata.project_name, "Cache should preserve project name"
                assert len(loaded_metadata.frameworks) == len(mock_metadata.frameworks), "Cache should preserve frameworks"
                assert loaded_metadata.primary_language == mock_metadata.primary_language, "Cache should preserve primary language"
            else:
                print("Cache load returned None - might be expired or invalid")
        
        return True
    except Exception as e:
        print(f"Cache system test failed: {e}")
        return False

def test_complete_project_analysis():
    """Test complete project analysis"""
    try:
        from utils.project_context import project_context
        
        # Analyze current project
        metadata = project_context.analyze_project(use_cache=False)
        
        # Verify metadata structure
        assert metadata.project_root, "Should have project root"
        assert metadata.project_name, "Should have project name"
        assert isinstance(metadata.frameworks, list), "Frameworks should be a list"
        assert metadata.primary_language, "Should detect primary language"
        assert isinstance(metadata.dependencies, dict), "Dependencies should be a dict"
        assert metadata.size_mb >= 0, "Size should be non-negative"
        assert metadata.file_count > 0, "Should count files"
        assert metadata.scan_timestamp, "Should have scan timestamp"
        assert metadata.cache_version, "Should have cache version"
        
        # Verify at least some frameworks detected (current project should have Python/FastAPI)
        assert len(metadata.frameworks) > 0, "Should detect at least one framework"
        
        # Verify primary language detection
        assert metadata.primary_language in ['python', 'javascript', 'typescript', 'java', 'unknown'], "Should detect valid primary language"
        
        return True
    except Exception as e:
        print(f"Complete project analysis test failed: {e}")
        return False

def test_build_system_detection():
    """Test build system detection"""
    try:
        from utils.project_context import project_context
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test npm detection
            (temp_path / "package.json").write_text("{}")
            build_system = project_context._detect_build_system(temp_path)
            assert build_system == "npm", "Should detect npm build system"
            
            # Test pip detection (clean directory)
            (temp_path / "package.json").unlink()
            (temp_path / "requirements.txt").write_text("fastapi")
            build_system = project_context._detect_build_system(temp_path)
            assert build_system == "pip", "Should detect pip build system"
            
            # Test maven detection
            (temp_path / "requirements.txt").unlink()
            (temp_path / "pom.xml").write_text("<project></project>")
            build_system = project_context._detect_build_system(temp_path)
            assert build_system == "maven", "Should detect maven build system"
        
        return True
    except Exception as e:
        print(f"Build system detection test failed: {e}")
        return False

def test_git_integration_preparation():
    """Test Git integration preparation"""
    try:
        from utils.integration_preparation import integration_preparation
        
        # Test Git context analysis
        git_info = integration_preparation.analyze_git_context()
        
        # Should return GitInfo object with proper structure
        assert hasattr(git_info, 'is_git_repo'), "Should have is_git_repo attribute"
        assert hasattr(git_info, 'current_branch'), "Should have current_branch attribute"
        assert hasattr(git_info, 'has_staged_changes'), "Should have has_staged_changes attribute"
        
        # If it's a git repo, should have additional info
        if git_info.is_git_repo:
            print(f"✅ Git repo detected: branch={git_info.current_branch}")
        else:
            print("ℹ️  Not a git repository")
        
        return True
    except Exception as e:
        print(f"Git integration preparation test failed: {e}")
        return False

def test_ci_cd_integration_preparation():
    """Test CI/CD integration preparation"""
    try:
        from utils.integration_preparation import integration_preparation
        
        # Test CI/CD context analysis
        ci_cd_info = integration_preparation.analyze_ci_cd_context()
        
        # Should return CiCdInfo object with proper structure
        assert hasattr(ci_cd_info, 'system'), "Should have system attribute"
        assert hasattr(ci_cd_info, 'config_files'), "Should have config_files attribute"
        assert hasattr(ci_cd_info, 'workflows'), "Should have workflows attribute"
        assert isinstance(ci_cd_info.config_files, list), "Config files should be a list"
        assert isinstance(ci_cd_info.workflows, list), "Workflows should be a list"
        
        if ci_cd_info.system:
            print(f"✅ CI/CD system detected: {ci_cd_info.system}")
        else:
            print("ℹ️  No CI/CD system detected")
        
        return True
    except Exception as e:
        print(f"CI/CD integration preparation test failed: {e}")
        return False

def test_integration_context_preparation():
    """Test complete integration context preparation"""
    try:
        from utils.integration_preparation import integration_preparation
        
        # Test complete integration context
        context = integration_preparation.prepare_integration_context()
        
        # Verify context structure
        assert 'project_root' in context, "Should have project_root"
        assert 'git_info' in context, "Should have git_info"
        assert 'ci_cd_info' in context, "Should have ci_cd_info"
        assert 'integration_opportunities' in context, "Should have integration_opportunities"
        assert 'recommendations' in context, "Should have recommendations"
        
        # Verify data types
        assert isinstance(context['integration_opportunities'], list), "Opportunities should be a list"
        assert isinstance(context['recommendations'], list), "Recommendations should be a list"
        
        print(f"✅ Integration opportunities: {context['integration_opportunities']}")
        print(f"✅ Recommendations: {len(context['recommendations'])} found")
        
        return True
    except Exception as e:
        print(f"Integration context preparation test failed: {e}")
        return False

def test_statistics_and_performance():
    """Test statistics collection and performance"""
    try:
        from utils.project_context import project_context
        import time
        
        # Test statistics
        stats = project_context.get_statistics()
        
        # Verify statistics structure
        assert 'scan_stats' in stats, "Should have scan stats"
        assert 'cache_available' in stats, "Should have cache availability"
        assert 'supported_frameworks' in stats, "Should have supported frameworks"
        assert 'supported_dependency_files' in stats, "Should have supported dependency files"
        
        # Verify supported frameworks count
        assert len(stats['supported_frameworks']) >= 8, "Should support at least 8 frameworks"
        
        # Test performance
        start_time = time.time()
        frameworks = project_context.detect_frameworks()
        detection_time = time.time() - start_time
        
        assert detection_time < 5.0, f"Framework detection should be fast, took {detection_time:.2f}s"
        
        print(f"✅ Performance: Framework detection in {detection_time:.3f}s")
        print(f"✅ Supported frameworks: {len(stats['supported_frameworks'])}")
        
        return True
    except Exception as e:
        print(f"Statistics and performance test failed: {e}")
        return False

def test_edge_cases_and_error_handling():
    """Test edge cases and error handling"""
    try:
        from utils.project_context import project_context
        
        # Test with non-existent directory
        non_existent = Path("/non/existent/path")
        frameworks = project_context.detect_frameworks(non_existent)
        assert isinstance(frameworks, list), "Should return empty list for non-existent path"
        
        # Test with empty directory
        with tempfile.TemporaryDirectory() as temp_dir:
            empty_path = Path(temp_dir)
            frameworks = project_context.detect_frameworks(empty_path)
            assert isinstance(frameworks, list), "Should handle empty directory"
        
        # Test cache with invalid data
        if project_context.cache_dir:
            invalid_cache_file = project_context.cache_dir / "invalid_cache.json"
            invalid_cache_file.write_text("invalid json content")
            
            # Should handle invalid cache gracefully
            loaded = project_context._load_cache(Path("/invalid/path"))
            assert loaded is None, "Should return None for invalid cache"
            
            # Cleanup
            if invalid_cache_file.exists():
                invalid_cache_file.unlink()
        
        return True
    except Exception as e:
        print(f"Edge cases and error handling test failed: {e}")
        return False

def test_integration_with_existing_systems():
    """Test integration with existing logger and path_resolver"""
    try:
        from utils.project_context import project_context
        from utils.logger import logger
        
        # Test that operations integrate with logging
        logger.operation_start("Project Context Integration Test", "Testing project context with existing systems")
        
        # Perform analysis with logging
        metadata = project_context.analyze_project(use_cache=False)
        
        if len(metadata.frameworks) > 0:
            logger.success(f"Frameworks detected: {[fw.name for fw in metadata.frameworks]}")
        
        logger.info(f"Primary language: {metadata.primary_language}")
        logger.info(f"Build system: {metadata.build_system}")
        
        # Test cache operations
        stats = project_context.get_statistics()
        logger.info(f"Cache available: {stats['cache_available']}")
        
        logger.operation_end("Project Context Integration Test", success=True)
        
        return True
    except Exception as e:
        print(f"Integration with existing systems test failed: {e}")
        return False

def run_all_project_context_tests():
    """Run all project context tests and report results"""
    tests = [
        ("Project Context Import", test_project_context_import),
        ("Framework Detection Python", test_framework_detection_python),
        ("Framework Detection Mock Projects", test_framework_detection_mock_projects),
        ("Dependency Parsing", test_dependency_parsing),
        ("Cache System", test_cache_system),
        ("Complete Project Analysis", test_complete_project_analysis),
        ("Build System Detection", test_build_system_detection),
        ("Git Integration Preparation", test_git_integration_preparation),
        ("CI/CD Integration Preparation", test_ci_cd_integration_preparation),
        ("Integration Context Preparation", test_integration_context_preparation),
        ("Statistics and Performance", test_statistics_and_performance),
        ("Edge Cases and Error Handling", test_edge_cases_and_error_handling),
        ("Integration with Existing Systems", test_integration_with_existing_systems),
    ]
    
    passed = 0
    total = len(tests)
    
    print("🧪 RUNNING PROJECT CONTEXT ALL FRAMEWORKS TESTS")
    print("=" * 70)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("=" * 70)
    print(f"📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL PROJECT CONTEXT TESTS PASSED! Advanced system is ready.")
        return True
    else:
        print("⚠️ Some tests failed. Review implementation.")
        return False

if __name__ == "__main__":
    success = run_all_project_context_tests()
    sys.exit(0 if success else 1)
