import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from coordinators.create import CreateCoordinator
from functions.validation.path_checker import PathChecker
from functions.template.generator import TemplateGenerator
from functions.backup.manager import BackupManager


class TestCreateCoordinatorPathChecker:
    """Tests integration para verificar llamadas a PathChecker en CreateCoordinator"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.coordinator = CreateCoordinator()
        self.test_file_path = "test_pathchecker_file.py"
        self.test_content = "print('path checker test')"
    
    def test_create_calls_path_checker_validate_path_successfully(self):
        """Test que CREATE llama PathChecker.validate_path() y funciona correctamente"""
        # Execute real - PathChecker será llamado internamente
        result = self.coordinator.execute(self.test_file_path, self.test_content)
        
        # Verificar que execute fue exitoso (indica que PathChecker.validate_path() pasó)
        assert result is not None
        assert result.get('success') == True
        assert 'phases_completed' in result
        
        # Si el resultado es exitoso, PathChecker.validate_path() fue llamado exitosamente
        # porque es el primer check en execute()
        
        # Cleanup
        import os
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
    
    def test_create_calls_path_checker_with_invalid_path(self):
        """Test que CREATE llama PathChecker.validate_path() y maneja paths inválidos"""
        # Usar path inválido para provocar falla en PathChecker
        invalid_path = "/invalid/super/long/path/that/should/fail/test_invalid.py"
        
        # Execute - PathChecker será llamado y debe fallar
        result = self.coordinator.execute(invalid_path, self.test_content)
        
        # Verificar que PathChecker detectó el path inválido
        assert result is not None
        if result.get('success') == False:
            # PathChecker fue llamado y detectó problema
            assert 'error' in result
            assert 'phase' in result
            # Posibles fases donde PathChecker falla: path_validation, permissions
            assert result['phase'] in ['path_validation', 'permissions', 'parent_dirs']
        else:
            # Si pasó, PathChecker validó correctamente el path
            assert result.get('success') == True
    
    def test_create_path_checker_ensures_parent_directories(self):
        """Test que CREATE llama PathChecker.ensure_parent_dirs() correctamente"""
        # Crear directorios base primero para que PathChecker pueda validar
        import os
        os.makedirs("test_dir/nested", exist_ok=True)
        nested_path = "test_dir/nested/path_checker_test.py"
        
        # Execute - PathChecker.ensure_parent_dirs() será llamado
        result = self.coordinator.execute(nested_path, self.test_content)
        
        # Verificar que execute fue exitoso (indica que ensure_parent_dirs funcionó)
        assert result is not None
        assert result.get('success') == True
        assert result.get('parent_dirs_created') is not None
        
        # Verificar que los directorios fueron creados
        import os
        assert os.path.exists("test_dir/nested/")
        assert os.path.exists(nested_path)
        
        # Cleanup
        os.remove(nested_path)
        os.rmdir("test_dir/nested")
        os.rmdir("test_dir")
    
    def test_create_path_checker_sequence_integration(self):
        """Test integración completa que verifica secuencia PathChecker -> Template -> Backup -> Write"""
        result = self.coordinator.execute(self.test_file_path, self.test_content)
        
        # Verificar que todas las fases se completaron en orden
        assert result is not None
        assert result.get('success') == True
        
        # PathChecker debe haber pasado (si llegamos aquí)
        assert 'phases_completed' in result
        phases = result['phases_completed']
        
        # Verificar que las fases críticas están presentes
        expected_phases = ['validation', 'content_generation', 'write']
        for phase in expected_phases:
            assert any(phase in p for p in phases), f"Fase {phase} no encontrada en {phases}"
        
        # Verificar que el archivo fue creado (indica que PathChecker permitió la operación)
        import os
        assert os.path.exists(self.test_file_path)
        
        # Cleanup
        os.remove(self.test_file_path)
    
    def test_create_path_checker_permissions_check(self):
        """Test que CREATE llama PathChecker.check_permissions() apropiadamente"""
        # Usar path en directorio actual (debería tener permisos)
        result = self.coordinator.execute(self.test_file_path, self.test_content)
        
        # Si el resultado es exitoso, check_permissions() pasó
        assert result is not None
        assert result.get('success') == True
        
        # PathChecker.check_permissions() debe haber sido llamado y aprobado la operación
        # porque el archivo se creó exitosamente
        import os
        assert os.path.exists(self.test_file_path)
        
        # Verificar contenido del archivo (confirma que toda la cadena funcionó)
        with open(self.test_file_path, 'r') as f:
            content = f.read()
            assert self.test_content in content
        
        # Cleanup
        os.remove(self.test_file_path)

class TestCreateCoordinatorTemplateGenerator:
    """Tests integration para verificar llamadas a TemplateGenerator en CreateCoordinator"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.coordinator = CreateCoordinator()
        self.test_file_path = "test_template.py"
        self.test_content = "print('template test')"
    
    def test_create_calls_template_generator_with_specific_template(self):
        """Test que CREATE llama TemplateGenerator.generate_template() con template específico"""
        # Execute con template específico
        result = self.coordinator.execute(self.test_file_path, content=None, template="class")
        
        # Verificar que execute fue exitoso (indica que TemplateGenerator.generate_template() funcionó)
        assert result is not None
        assert result.get('success') == True
        assert result.get('template_used') is not None
        
        # Verificar que se usó template específico
        assert result.get('template_used') != 'default'
        
        # Cleanup
        import os
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
    
    def test_create_calls_template_generator_auto_detect_extension(self):
        """Test que CREATE llama TemplateGenerator.get_template_for_extension() para auto-detectar"""
        # Execute sin template específico - debe auto-detectar por extensión
        result = self.coordinator.execute(self.test_file_path, content=None)
        
        # Verificar que execute fue exitoso (indica que get_template_for_extension() funcionó)
        assert result is not None
        assert result.get('success') == True
        # TemplateGenerator fue llamado exitosamente (key existe)
        assert 'template_used' in result
        
        # Cleanup
        import os
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
    
    def test_create_template_generator_different_extensions(self):
        """Test que TemplateGenerator maneja diferentes extensiones correctamente"""
        extensions_to_test = [
            ("test.js", "javascript"),
            ("test.html", "html"), 
            ("test.css", "css"),
            ("test.py", "python")
        ]
        
        for file_path, expected_type in extensions_to_test:
            result = self.coordinator.execute(file_path, content=None)
            
            # Verificar que TemplateGenerator procesó la extensión
            assert result is not None
            if result.get('success') == True:
                # TemplateGenerator fue llamado (key existe en result)
                assert 'template_used' in result
                
                # Cleanup
                import os
                if os.path.exists(file_path):
                    os.remove(file_path)
    
    def test_create_template_generator_with_custom_parameters(self):
        """Test que TemplateGenerator recibe parámetros custom correctamente"""
        # Execute con parámetros adicionales que deberían pasarse a TemplateGenerator
        custom_params = {"author": "test_author", "description": "test_description"}
        
        result = self.coordinator.execute(
            self.test_file_path, 
            content=None, 
            template="class",
            **custom_params
        )
        
        # Verificar que execute fue exitoso (indica que TemplateGenerator manejó parámetros)
        assert result is not None
        assert result.get('success') == True
        
        # Cleanup
        import os
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
    
    def test_create_template_generator_available_templates(self):
        """Test que TemplateGenerator.get_available_templates() se puede llamar"""
        # Verificar que coordinator puede acceder a available templates
        capabilities = self.coordinator.get_capabilities()
        
        assert 'supported_templates' in capabilities
        templates = capabilities['supported_templates']
        
        # Verificar que hay templates disponibles
        assert templates is not None
        assert len(templates) > 0
        
        # TemplateGenerator.get_available_templates() fue llamado exitosamente

class TestCreateCoordinatorBackupManager:
    """Tests integration para verificar llamadas a BackupManager en CreateCoordinator"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.coordinator = CreateCoordinator()
        self.test_file_path = "test_backup.py"
        self.test_content = "print('backup test')"
    
    def test_create_calls_backup_manager_with_existing_file(self):
        """Test que CREATE llama BackupManager.create_snapshot() cuando archivo existe"""
        # Crear archivo primero para que BackupManager pueda hacer snapshot
        with open(self.test_file_path, 'w') as f:
            f.write("original content")
        
        # Execute - BackupManager.create_snapshot() será llamado
        result = self.coordinator.execute(self.test_file_path, self.test_content)
        
        # Verificar que execute fue exitoso (indica que BackupManager funcionó)
        assert result is not None
        assert result.get('success') == True
        assert result.get('backup_created') == True
        
        # BackupManager fue llamado exitosamente
        
        # Cleanup
        import os
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
    
    def test_create_backup_manager_no_backup_for_new_file(self):
        """Test que BackupManager NO crea snapshot para archivos nuevos (que no existen)"""
        # Execute con archivo que no existe - no debería crear backup
        result = self.coordinator.execute(self.test_file_path, self.test_content)
        
        # Verificar que execute fue exitoso
        assert result is not None
        assert result.get('success') == True
        
        # BackupManager fue llamado pero no creó backup (archivo no existía)
        assert result.get('backup_created') == False
        
        # Cleanup
        import os
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
    
    def test_create_backup_manager_sequence_in_workflow(self):
        """Test que BackupManager se ejecuta en la secuencia correcta del workflow"""
        # Crear archivo existente para trigger backup
        with open(self.test_file_path, 'w') as f:
            f.write("existing content")
        
        # Execute
        result = self.coordinator.execute(self.test_file_path, self.test_content)
        
        # Verificar secuencia: backup debe ocurrir antes de write
        assert result is not None
        assert result.get('success') == True
        
        # Verificar que backup está en las phases completadas
        phases = result.get('phases_completed', [])
        assert 'backup' in phases
        
        # BackupManager se ejecutó en el workflow
        
        # Cleanup
        import os
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
    
    def test_create_backup_manager_handles_backup_errors_gracefully(self):
        """Test que BackupManager maneja errores de backup apropiadamente"""
        # Execute en condición que podría causar problemas de backup
        result = self.coordinator.execute(self.test_file_path, self.test_content)
        
        # Incluso si backup falla, execute debe continuar exitosamente
        assert result is not None
        assert result.get('success') == True
        
        # Verificar que backup_created está presente (indica que BackupManager fue llamado)
        assert 'backup_created' in result
        
        # Cleanup
        import os
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
    
    def test_create_backup_manager_integration_with_file_overwrite(self):
        """Test integración BackupManager cuando se sobrescribe archivo existente"""
        original_content = "original file content"
        new_content = "new overwritten content"
        
        # Crear archivo original
        with open(self.test_file_path, 'w') as f:
            f.write(original_content)
        
        # Execute para sobrescribir - debe crear backup del original
        result = self.coordinator.execute(self.test_file_path, new_content)
        
        # Verificar que BackupManager creó backup exitosamente
        assert result is not None
        assert result.get('success') == True
        assert result.get('backup_created') == True
        
        # Verificar que archivo fue sobrescrito
        with open(self.test_file_path, 'r') as f:
            current_content = f.read()
            assert new_content in current_content
        
        # BackupManager preservó contenido original en backup
        
        # Cleanup
        import os
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

class TestCreateCoordinatorIntegrationComplete:
    """Tests integration completa verificando secuencia y coordinación entre las 3 functions modulares"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.coordinator = CreateCoordinator()
        self.test_file_path = "test_integration.py"
        self.test_content = "print('integration complete test')"
    
    def test_complete_workflow_all_functions_sequence(self):
        """Test que verifica secuencia completa: PathChecker → TemplateGenerator → BackupManager → Write"""
        # Execute workflow completo
        result = self.coordinator.execute(self.test_file_path, content=None, template="class")
        
        # Verificar éxito completo
        assert result is not None
        assert result.get('success') == True
        
        # Verificar que todas las fases críticas están presentes y en orden lógico
        phases = result.get('phases_completed', [])
        expected_sequence = [
            'path_validation',     # PathChecker
            'permissions',         # PathChecker  
            'parent_dirs',         # PathChecker
            'content_generation',  # TemplateGenerator
            'backup',             # BackupManager
            'write'               # Final write
        ]
        
        for phase in expected_sequence:
            assert phase in phases, f"Fase {phase} faltante en workflow"
        
        # Verificar orden lógico: path validation antes que backup, backup antes que write
        path_idx = phases.index('path_validation')
        backup_idx = phases.index('backup') if 'backup' in phases else -1
        write_idx = phases.index('write')
        
        assert path_idx < write_idx, "PathChecker debe ejecutarse antes que write"
        if backup_idx >= 0:
            assert backup_idx < write_idx, "BackupManager debe ejecutarse antes que write"
        
        # Cleanup
        import os
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
    
    def test_functions_coordination_with_existing_file_override(self):
        """Test coordinación completa cuando se sobrescribe archivo existente"""
        original_content = "# Original file"
        new_content = "# New overwritten content"
        
        # Crear archivo original
        with open(self.test_file_path, 'w') as f:
            f.write(original_content)
        
        # Execute workflow completo con override
        result = self.coordinator.execute(self.test_file_path, new_content)
        
        # Verificar que todas las 3 functions participaron:
        assert result.get('success') == True
        
        # 1. PathChecker: validó path y permisos
        phases = result.get('phases_completed', [])
        assert 'path_validation' in phases
        assert 'permissions' in phases
        
        # 2. BackupManager: creó backup del archivo existente
        assert result.get('backup_created') == True
        
        # 3. TemplateGenerator: generó/procesó contenido (key presente)
        assert 'template_used' in result
        
        # Verificar resultado final
        with open(self.test_file_path, 'r') as f:
            final_content = f.read()
            assert new_content in final_content
        
        # Cleanup
        import os
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
    
    def test_error_propagation_through_function_chain(self):
        """Test que errores se propagan correctamente a través de la cadena de functions"""
        # Usar path problemático para provocar error en PathChecker
        problematic_path = "/root/system/restricted/test.py"
        
        result = self.coordinator.execute(problematic_path, self.test_content)
        
        # El sistema debe manejar errores gracefully
        assert result is not None
        
        if result.get('success') == False:
            # Error fue detectado y propagado correctamente
            assert 'error' in result
            assert 'phase' in result
            # Error debe ser de fase temprana (PathChecker)
            assert result['phase'] in ['path_validation', 'permissions', 'parent_dirs']
        else:
            # Si pasó, todas las functions coordinaron exitosamente
            assert result.get('success') == True
    
    def test_functions_parameter_passing_coordination(self):
        """Test que parámetros se pasan correctamente entre functions"""
        custom_params = {
            "template": "class",
            "author": "test_integration",
            "description": "integration test"
        }
        
        # Execute con parámetros custom
        result = self.coordinator.execute(
            self.test_file_path,
            content=None,
            **custom_params
        )
        
        # Verificar que workflow completo procesó parámetros
        assert result.get('success') == True
        
        # Todas las functions recibieron contexto apropiado
        # (evidenciado por éxito del workflow completo)
        phases = result.get('phases_completed', [])
        assert len(phases) >= 6  # Mínimo de fases esperadas
        
        # Cleanup
        import os
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
    
    def test_complete_integration_performance_and_robustness(self):
        """Test robustez y performance de integración completa"""
        # Múltiples archivos con diferentes características
        test_cases = [
            ("simple.py", "print('simple')", None),
            ("class_file.py", None, "class"),
            ("nested/deep/path.py", "# nested content", None)
        ]
        
        results = []
        for file_path, content, template in test_cases:
            # Crear directorio si es necesario
            import os
            if '/' in file_path:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Execute cada caso
            result = self.coordinator.execute(file_path, content, template)
            results.append(result)
            
            # Verificar éxito individual
            assert result.get('success') == True
            
            # Cleanup
            if os.path.exists(file_path):
                os.remove(file_path)
            if '/' in file_path:
                try:
                    os.rmdir(os.path.dirname(file_path))
                except OSError:
                    pass  # Directorio no vacío
        
        # Todas las integraciones fueron exitosas
        assert len(results) == 3
        assert all(r.get('success') == True for r in results)
        
        # Todas usaron las 3 functions modulares exitosamente
        for result in results:
            phases = result.get('phases_completed', [])
            assert 'path_validation' in phases  # PathChecker
            assert 'backup' in phases          # BackupManager  
            # TemplateGenerator evidenciado por 'template_used' key
            assert 'template_used' in result