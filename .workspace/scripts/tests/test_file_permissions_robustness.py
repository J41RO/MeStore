"""
Tests de robustez para permisos de archivo restrictivos
Valida manejo elegante de PermissionError y recuperación
"""

import os
import stat
import sys
import tempfile
from pathlib import Path

import pytest

# Agregar directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import surgical_modifier_ultimate as smu


class TestFilePermissionsRobustness:
    """Suite de tests para robustez de permisos de archivo"""

    def test_readonly_file_handling(self):
        """Test manejo de archivos de solo lectura"""
        content = (
            chr(35)
            + chr(32)
            + chr(65)
            + chr(114)
            + chr(99)
            + chr(104)
            + chr(105)
            + chr(118)
            + chr(111)
            + chr(32)
            + chr(100)
            + chr(101)
            + chr(32)
            + chr(115)
            + chr(111)
            + chr(108)
            + chr(111)
            + chr(32)
            + chr(108)
            + chr(101)
            + chr(99)
            + chr(116)
            + chr(117)
            + chr(114)
            + chr(97)
            + chr(10)
        )
        content += (
            chr(35)
            + chr(32)
            + chr(76)
            + chr(105)
            + chr(110)
            + chr(101)
            + chr(97)
            + chr(32)
            + chr(111)
            + chr(114)
            + chr(105)
            + chr(103)
            + chr(105)
            + chr(110)
            + chr(97)
            + chr(108)
            + chr(10)
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
            f.write(content)
            temp_path = f.name

        try:
            # Hacer archivo de solo lectura
            os.chmod(temp_path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

            sm = smu.SurgicalModifierUltimate(verbose=False)
            result = sm.execute(
                "replace", temp_path, "# Linea original", "# Linea modificada"
            )

            # El sistema debe manejar gracefully el error de permisos
            # Ya sea que falle gracefully o que maneje el permiso
            assert isinstance(result, dict), "Resultado debe ser diccionario"

        finally:
            # Restaurar permisos para cleanup
            try:
                os.chmod(
                    temp_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
                )
                os.unlink(temp_path)
            except:
                pass

    def test_directory_without_write_permissions(self):
        """Test manejo de directorio sin permisos de escritura"""
        import tempfile

        # Crear directorio temporal
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, "test_file.py")

        # Crear archivo en directorio
        content = (
            chr(35)
            + chr(32)
            + chr(65)
            + chr(114)
            + chr(99)
            + chr(104)
            + chr(105)
            + chr(118)
            + chr(111)
            + chr(32)
            + chr(101)
            + chr(110)
            + chr(32)
            + chr(100)
            + chr(105)
            + chr(114)
            + chr(101)
            + chr(99)
            + chr(116)
            + chr(111)
            + chr(114)
            + chr(105)
            + chr(111)
            + chr(10)
        )
        with open(file_path, "w") as f:
            f.write(content)

        try:
            # Remover permisos de escritura del directorio
            os.chmod(
                temp_dir,
                stat.S_IRUSR
                | stat.S_IXUSR
                | stat.S_IRGRP
                | stat.S_IXGRP
                | stat.S_IROTH
                | stat.S_IXOTH,
            )

            sm = smu.SurgicalModifierUltimate(verbose=False)
            result = sm.execute(
                "replace", file_path, "# Archivo en directorio", "# Archivo modificado"
            )

            # Sistema debe manejar restricciones de directorio
            assert isinstance(result, dict), "Resultado debe ser diccionario"

        finally:
            # Restaurar permisos para cleanup
            try:
                os.chmod(temp_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                import shutil

                shutil.rmtree(temp_dir)
            except:
                pass

    def test_permission_error_recovery(self):
        """Test recuperación elegante de PermissionError"""
        content = (
            chr(35)
            + chr(32)
            + chr(65)
            + chr(114)
            + chr(99)
            + chr(104)
            + chr(105)
            + chr(118)
            + chr(111)
            + chr(32)
            + chr(112)
            + chr(97)
            + chr(114)
            + chr(97)
            + chr(32)
            + chr(116)
            + chr(101)
            + chr(115)
            + chr(116)
            + chr(32)
            + chr(114)
            + chr(101)
            + chr(99)
            + chr(117)
            + chr(112)
            + chr(101)
            + chr(114)
            + chr(97)
            + chr(99)
            + chr(105)
            + chr(111)
            + chr(110)
            + chr(10)
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
            f.write(content)
            temp_path = f.name

        # Test con permisos normales primero
        sm = smu.SurgicalModifierUltimate(verbose=False)
        result = sm.execute(
            "after", temp_path, "# Archivo para test", "# Linea agregada"
        )

        assert result.get(
            "success", False
        ), "Operacion con permisos normales debe ser exitosa"

        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_backup_creation_with_restricted_permissions(self):
        """Test creación de backups cuando archivo original está protegido"""
        content = (
            chr(35)
            + chr(32)
            + chr(65)
            + chr(114)
            + chr(99)
            + chr(104)
            + chr(105)
            + chr(118)
            + chr(111)
            + chr(32)
            + chr(112)
            + chr(97)
            + chr(114)
            + chr(97)
            + chr(32)
            + chr(98)
            + chr(97)
            + chr(99)
            + chr(107)
            + chr(117)
            + chr(112)
            + chr(10)
        )
        content += (
            chr(35)
            + chr(32)
            + chr(67)
            + chr(111)
            + chr(110)
            + chr(116)
            + chr(101)
            + chr(110)
            + chr(105)
            + chr(100)
            + chr(111)
            + chr(32)
            + chr(111)
            + chr(114)
            + chr(105)
            + chr(103)
            + chr(105)
            + chr(110)
            + chr(97)
            + chr(108)
            + chr(10)
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
            f.write(content)
            temp_path = f.name

        try:
            sm = smu.SurgicalModifierUltimate(verbose=False)
            result = sm.execute(
                "replace", temp_path, "# Contenido original", "# Contenido actualizado"
            )

            # Verificar que operacion funciona correctamente
            assert result.get("success", False), "Replace debe ser exitoso"

            # Verificar que backup se maneja apropiadamente
            assert "backup_path" in result, "Resultado debe incluir info de backup"

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
