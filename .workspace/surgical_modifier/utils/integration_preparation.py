"""
Surgical Modifier v6.0 - Integration Preparation System
Prepare for future Git/CI/CD integrations with context awareness
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass
import subprocess
import json

try:
    from utils.project_context import project_context
    from utils.logger import logger
    CONTEXT_AVAILABLE = True
except ImportError:
    CONTEXT_AVAILABLE = False

@dataclass
class GitInfo:
    """Git repository information"""
    is_git_repo: bool
    current_branch: Optional[str]
    remote_url: Optional[str]
    has_staged_changes: bool
    has_unstaged_changes: bool
    last_commit_hash: Optional[str]
    last_commit_message: Optional[str]

@dataclass
class CiCdInfo:
    """CI/CD system information"""
    system: Optional[str]
    config_files: List[str]
    workflows: List[str]
    build_commands: List[str]
    test_commands: List[str]

class IntegrationPreparation:
    """
    Prepare project context for future Git/CI/CD integrations
    """
    
    def __init__(self):
        self.git_commands = {
            'status': ['git', 'status', '--porcelain'],
            'branch': ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            'remote': ['git', 'config', '--get', 'remote.origin.url'],
            'last_commit': ['git', 'rev-parse', 'HEAD'],
            'last_message': ['git', 'log', '-1', '--pretty=%B']
        }
    
    def analyze_git_context(self, project_root: Optional[Path] = None) -> GitInfo:
        """Analyze Git repository context"""
        if project_root is None:
            project_root = Path.cwd()
        
        # Check if it's a git repository
        git_dir = project_root / '.git'
        if not git_dir.exists():
            return GitInfo(
                is_git_repo=False,
                current_branch=None,
                remote_url=None,
                has_staged_changes=False,
                has_unstaged_changes=False,
                last_commit_hash=None,
                last_commit_message=None
            )
        
        # Gather git information
        git_info = {
            'is_git_repo': True,
            'current_branch': self._run_git_command('branch', project_root),
            'remote_url': self._run_git_command('remote', project_root),
            'last_commit_hash': self._run_git_command('last_commit', project_root),
            'last_commit_message': self._run_git_command('last_message', project_root)
        }
        
        # Check for changes
        status_output = self._run_git_command('status', project_root)
        git_info['has_staged_changes'] = bool(status_output and any(
            line.startswith(('A ', 'M ', 'D ', 'R ', 'C ')) for line in status_output.split('\n')
        ))
        git_info['has_unstaged_changes'] = bool(status_output and any(
            line.startswith((' M', ' D', '??')) for line in status_output.split('\n')
        ))
        
        return GitInfo(**git_info)
    
    def _run_git_command(self, command_name: str, project_root: Path) -> Optional[str]:
        """Run a git command and return output"""
        try:
            command = self.git_commands[command_name]
            result = subprocess.run(
                command,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return None
    
    def analyze_ci_cd_context(self, project_root: Optional[Path] = None) -> CiCdInfo:
        """Analyze CI/CD system context"""
        if project_root is None:
            project_root = Path.cwd()
        
        ci_cd_systems = {
            'github_actions': {
                'config_files': ['.github/workflows/'],
                'patterns': ['*.yml', '*.yaml'],
                'build_commands': ['npm run build', 'python setup.py build', 'mvn compile'],
                'test_commands': ['npm test', 'pytest', 'mvn test']
            },
            'gitlab_ci': {
                'config_files': ['.gitlab-ci.yml'],
                'patterns': ['*.yml'],
                'build_commands': ['build', 'compile'],
                'test_commands': ['test', 'unit_test']
            },
            'jenkins': {
                'config_files': ['Jenkinsfile', 'jenkins/'],
                'patterns': ['Jenkinsfile*'],
                'build_commands': ['sh "make build"', 'sh "npm run build"'],
                'test_commands': ['sh "make test"', 'sh "npm test"']
            }
        }
        
        detected_system = None
        config_files = []
        workflows = []
        build_commands = []
        test_commands = []
        
        for system_name, system_config in ci_cd_systems.items():
            found_configs = []
            
            for config_path in system_config['config_files']:
                full_path = project_root / config_path
                if full_path.exists():
                    found_configs.append(config_path)
                    
                    # If it's a directory, look for workflow files
                    if full_path.is_dir():
                        for pattern in system_config['patterns']:
                            workflow_files = list(full_path.glob(pattern))
                            workflows.extend([str(wf.relative_to(project_root)) for wf in workflow_files])
            
            if found_configs:
                detected_system = system_name
                config_files = found_configs
                build_commands = system_config['build_commands']
                test_commands = system_config['test_commands']
                break
        
        return CiCdInfo(
            system=detected_system,
            config_files=config_files,
            workflows=workflows,
            build_commands=build_commands,
            test_commands=test_commands
        )
    
    def prepare_integration_context(self, project_root: Optional[Path] = None) -> Dict[str, Any]:
        """Prepare complete integration context for future use"""
        if project_root is None:
            project_root = Path.cwd()
        
        integration_context = {
            'project_root': str(project_root),
            'preparation_timestamp': None,
            'git_info': None,
            'ci_cd_info': None,
            'project_metadata': None,
            'integration_opportunities': [],
            'recommendations': []
        }
        
        # Get project metadata if available
        if CONTEXT_AVAILABLE:
            try:
                metadata = project_context.analyze_project(project_root)
                integration_context['project_metadata'] = {
                    'frameworks': [fw.name for fw in metadata.frameworks],
                    'primary_language': metadata.primary_language,
                    'build_system': metadata.build_system,
                    'dependencies_count': sum(len(deps) for deps in metadata.dependencies.values())
                }
            except Exception:
                pass
        
        # Analyze Git context
        git_info = self.analyze_git_context(project_root)
        integration_context['git_info'] = {
            'is_git_repo': git_info.is_git_repo,
            'current_branch': git_info.current_branch,
            'has_changes': git_info.has_staged_changes or git_info.has_unstaged_changes,
            'remote_configured': git_info.remote_url is not None
        }
        
        # Analyze CI/CD context
        ci_cd_info = self.analyze_ci_cd_context(project_root)
        integration_context['ci_cd_info'] = {
            'system': ci_cd_info.system,
            'has_ci_cd': ci_cd_info.system is not None,
            'config_files_count': len(ci_cd_info.config_files),
            'workflows_count': len(ci_cd_info.workflows)
        }
        
        # Generate integration opportunities
        opportunities = self._identify_integration_opportunities(
            integration_context['project_metadata'],
            integration_context['git_info'],
            integration_context['ci_cd_info']
        )
        integration_context['integration_opportunities'] = opportunities
        
        # Generate recommendations
        recommendations = self._generate_integration_recommendations(
            integration_context['project_metadata'],
            integration_context['git_info'],
            integration_context['ci_cd_info']
        )
        integration_context['recommendations'] = recommendations
        
        integration_context['preparation_timestamp'] = str(Path.cwd())
        
        return integration_context
    
    def _identify_integration_opportunities(self, project_metadata: Optional[Dict],
                                         git_info: Dict, ci_cd_info: Dict) -> List[str]:
        """Identify potential integration opportunities"""
        opportunities = []
        
        # Git integration opportunities
        if git_info['is_git_repo']:
            opportunities.append('git_operations')
            if git_info['remote_configured']:
                opportunities.append('remote_sync')
            if git_info['has_changes']:
                opportunities.append('change_management')
        
        # CI/CD integration opportunities
        if ci_cd_info['has_ci_cd']:
            opportunities.append('automated_testing')
            opportunities.append('deployment_automation')
            if ci_cd_info['system'] == 'github_actions':
                opportunities.append('github_integration')
        
        # Project-specific opportunities
        if project_metadata:
            if 'python' in project_metadata.get('primary_language', ''):
                opportunities.append('python_tooling')
            if any(fw in ['react', 'nextjs', 'vue', 'angular'] for fw in project_metadata.get('frameworks', [])):
                opportunities.append('frontend_tooling')
            if project_metadata.get('build_system'):
                opportunities.append('build_automation')
        
        return opportunities
    
    def _generate_integration_recommendations(self, project_metadata: Optional[Dict],
                                           git_info: Dict, ci_cd_info: Dict) -> List[str]:
        """Generate integration recommendations"""
        recommendations = []
        
        # Git recommendations
        if not git_info['is_git_repo']:
            recommendations.append('Initialize Git repository for version control')
        elif not git_info['remote_configured']:
            recommendations.append('Configure remote repository for collaboration')
        
        # CI/CD recommendations
        if not ci_cd_info['has_ci_cd']:
            recommendations.append('Set up CI/CD pipeline for automated testing and deployment')
        
        # Project-specific recommendations
        if project_metadata:
            primary_lang = project_metadata.get('primary_language', '')
            if primary_lang == 'python':
                recommendations.append('Consider pre-commit hooks for Python code quality')
                recommendations.append('Set up automated testing with pytest')
            elif primary_lang == 'javascript':
                recommendations.append('Configure ESLint and Prettier for code quality')
                recommendations.append('Set up automated testing with Jest')
        
        return recommendations

# Global integration preparation instance
integration_preparation = IntegrationPreparation()
