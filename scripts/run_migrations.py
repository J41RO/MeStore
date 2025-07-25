#!/usr/bin/env python3
"""
MeStore - Script principal para ejecutar migraciones Alembic en deployment.
Proporciona validación robusta, logging estructurado y manejo de errores.

Uso:
    python scripts/run_migrations.py --env production --validate
    python scripts/run_migrations.py --env development --rollback abc123
    python scripts/run_migrations.py --env test --dry-run
"""

import os
import sys
import argparse
import logging
import time
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

# Importaciones específicas para validación DB y Alembic
try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("⚠️ psycopg2 no disponible - funcionalidad DB limitada")
    psycopg2 = None

try:
    from alembic.config import Config
    from alembic import command
    from alembic.script import ScriptDirectory
    from alembic.runtime.environment import EnvironmentContext
except ImportError:
    print("❌ Alembic no disponible - script no funcional")
    sys.exit(1)


class MigrationRunner:
    """Ejecutor robusto de migraciones Alembic con validación y logging."""
    
    def __init__(self, environment: str = "development"):
        """Inicializar runner de migraciones."""
        self.environment = environment
        self.project_root = Path(__file__).parent.parent
        self.alembic_cfg_path = self.project_root / "alembic.ini"
        
        # Configurar logging
        self.setup_logging()
        
        # Cargar configuración de entorno
        self.load_environment_config()
        
        # Configurar Alembic
        self.alembic_cfg = Config(str(self.alembic_cfg_path))
        
        self.logger.info(f"🚀 MigrationRunner inicializado para entorno: {environment}")
    
    def setup_logging(self) -> None:
        """Configurar logging estructurado."""
        log_dir = self.project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"migration_python_{timestamp}.log"
        
        # Configurar formato de logging
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Handler para archivo
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Configurar logger
        self.logger = logging.getLogger("MigrationRunner")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.log_file = log_file
        self.logger.info(f"📝 Logging configurado: {log_file}")
    
    def load_environment_config(self) -> None:
        """Cargar configuración según entorno."""
        env_file = self.project_root / f".env.{self.environment}"
        
        if not env_file.exists():
            env_file = self.project_root / ".env"
        
        if env_file.exists():
            self.logger.info(f"🔧 Cargando configuración desde: {env_file}")
            
            # Cargar variables de entorno
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "=" in line:
                            key, value = line.split("=", 1)
                            os.environ[key.strip()] = value.strip().strip('"\'')
        else:
            self.logger.warning(f"⚠️ Archivo de configuración no encontrado: {env_file}")
        
        # Validar variables críticas
        self.validate_environment_variables()
    
    def validate_environment_variables(self) -> None:
        """Validar que existan variables de entorno críticas."""
        required_vars = [
            "DATABASE_URL",
            "POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_DB",
            "POSTGRES_USER", "POSTGRES_PASSWORD"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            error_msg = f"❌ Variables de entorno faltantes: {missing_vars}"
            self.logger.error(error_msg)
            raise EnvironmentError(error_msg)
        
        self.logger.info("✅ Variables de entorno validadas correctamente")
    
    def validate_database_connection(self) -> bool:
        """Validar conexión a base de datos."""
        if psycopg2 is None:
            self.logger.warning("⚠️ psycopg2 no disponible - saltando validación DB")
            return True
        
        self.logger.info("🔍 Validando conexión a base de datos...")
        
        try:
            # Construir configuración de conexión
            db_config = {
                "host": os.getenv("POSTGRES_HOST"),
                "port": os.getenv("POSTGRES_PORT"),
                "database": os.getenv("POSTGRES_DB"),
                "user": os.getenv("POSTGRES_USER"),
                "password": os.getenv("POSTGRES_PASSWORD")
            }
            
            # Intentar conexión
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            
            # Verificar que la base de datos esté accesible
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            self.logger.info(f"✅ Conexión DB exitosa: {db_version[:50]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error de conexión DB: {str(e)}")
            return False
    
    def get_current_revision(self) -> Optional[str]:
        """Obtener revisión actual de la base de datos."""
        try:
            result = subprocess.run(
                ["alembic", "current"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output and "current)" in output:
                    # Extraer revisión del output
                    revision = output.split(" ")[0]
                    self.logger.info(f"📊 Revisión actual: {revision}")
                    return revision
                else:
                    self.logger.info("📊 No hay revisiones aplicadas (base de datos nueva)")
                    return None
            else:
                self.logger.error(f"❌ Error obteniendo revisión: {result.stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo revisión actual: {str(e)}")
            return None
    
    def run_migrations(self, dry_run: bool = False) -> bool:
        """Ejecutar migraciones pendientes."""
        if dry_run:
            self.logger.info("🧪 MODO DRY-RUN: Solo validación, sin ejecutar migraciones")
            
            # Verificar migraciones pendientes sin ejecutar
            result = subprocess.run(
                ["alembic", "show", "head"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                self.logger.info("✅ Configuración Alembic válida - migraciones disponibles")
                return True
            else:
                self.logger.error(f"❌ Error en configuración Alembic: {result.stderr}")
                return False
        
        self.logger.info("🚀 Iniciando ejecución de migraciones...")
        
        try:
            # Ejecutar migraciones usando Alembic
            command.upgrade(self.alembic_cfg, "head")
            
            self.logger.info("✅ Migraciones ejecutadas exitosamente")
            
            # Verificar estado final
            final_revision = self.get_current_revision()
            self.logger.info(f"📊 Revisión final: {final_revision}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error ejecutando migraciones: {str(e)}")
            return False
    
    def rollback_to_revision(self, target_revision: str) -> bool:
        """Realizar rollback a revisión específica."""
        self.logger.info(f"🔄 Iniciando rollback a revisión: {target_revision}")
        
        try:
            # Validar que la revisión existe
            result = subprocess.run(
                ["alembic", "show", target_revision],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode != 0:
                self.logger.error(f"❌ Revisión no válida: {target_revision}")
                return False
            
            # Ejecutar rollback
            command.downgrade(self.alembic_cfg, target_revision)
            
            self.logger.info(f"✅ Rollback completado a: {target_revision}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error en rollback: {str(e)}")
            return False
    
    def run_full_validation(self) -> Dict[str, Any]:
        """Ejecutar validación completa del sistema."""
        self.logger.info("🔍 Iniciando validación completa del sistema...")
        
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "environment": self.environment,
            "database_connection": False,
            "alembic_config": False,
            "current_revision": None,
            "validation_passed": False
        }
        
        # 1. Validar conexión DB
        validation_results["database_connection"] = self.validate_database_connection()
        
        # 2. Validar configuración Alembic
        try:
            if self.alembic_cfg_path.exists():
                # Verificar que Alembic puede acceder a la configuración
                result = subprocess.run(
                    ["alembic", "check"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root
                )
                
                if result.returncode == 0:
                    validation_results["alembic_config"] = True
                    self.logger.info("✅ Configuración Alembic válida")
                else:
                    self.logger.error(f"❌ Error en configuración Alembic: {result.stderr}")
            else:
                self.logger.error("❌ alembic.ini no encontrado")
        except Exception as e:
            self.logger.error(f"❌ Error validando Alembic: {str(e)}")
        
        # 3. Obtener estado actual
        validation_results["current_revision"] = self.get_current_revision()
        
        # 4. Determinar resultado final
        validation_results["validation_passed"] = (
            validation_results["database_connection"] and
            validation_results["alembic_config"]
        )
        
        if validation_results["validation_passed"]:
            self.logger.info("✅ Validación completa exitosa")
        else:
            self.logger.error("❌ Validación completa falló")
        
        return validation_results


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Script robusto para ejecutar migraciones Alembic",
        epilog="Ejemplo: python scripts/run_migrations.py --env production --validate"
    )
    
    parser.add_argument(
        "--env",
        choices=["development", "production", "test"],
        default="development",
        help="Entorno de ejecución (default: development)"
    )
    
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Solo validar sistema sin ejecutar migraciones"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simular ejecución sin aplicar cambios"
    )
    
    parser.add_argument(
        "--rollback",
        type=str,
        help="Revisión objetivo para rollback"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Forzar ejecución sin validaciones previas"
    )
    
    args = parser.parse_args()
    
    try:
        # Inicializar runner
        runner = MigrationRunner(environment=args.env)
        
        # Ejecutar según argumentos
        if args.validate:
            # Solo validación
            results = runner.run_full_validation()
            print(json.dumps(results, indent=2))
            sys.exit(0 if results["validation_passed"] else 1)
        
        elif args.rollback:
            # Rollback a revisión específica
            if not args.force:
                validation = runner.run_full_validation()
                if not validation["database_connection"]:
                    runner.logger.error("❌ Conexión DB falló - use --force para continuar")
                    sys.exit(1)
            
            success = runner.rollback_to_revision(args.rollback)
            sys.exit(0 if success else 1)
        
        else:
            # Ejecución normal de migraciones
            if not args.force:
                validation = runner.run_full_validation()
                if not validation["validation_passed"]:
                    runner.logger.error("❌ Validación falló - use --force para continuar")
                    sys.exit(1)
            
            success = runner.run_migrations(dry_run=args.dry_run)
            sys.exit(0 if success else 1)
    
    except Exception as e:
        print(f"❌ Error crítico: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
