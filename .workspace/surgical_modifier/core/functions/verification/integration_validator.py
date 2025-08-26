import functools
import logging
from typing import Callable, Any, Dict, Optional
from .structural_validator import StructuralValidator
from .rollback_manager import RollbackManager


def validate_structural_integrity(func: Callable) -> Callable:
    """
    Decorador que ejecuta validación estructural PRE y POST operación.
    
    Aplica validación automática antes y después de operaciones de modificación,
    con rollback automático si se detecta corrupción estructural.
    
    Args:
        func: Función a decorar (debe tomar file_path como primer argumento)
        
    Returns:
        Función decorada con validación estructural integrada
    """
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Configurar logging
        logger = logging.getLogger('integration_validator')
        validator = StructuralValidator()
        rollback_manager = RollbackManager()
        
        # Extraer file_path del primer argumento
        file_path = args[0] if args else kwargs.get('file_path')
        if not file_path:
            logger.error('No se pudo determinar file_path para validación')
            return func(*args, **kwargs)
        
        logger.info(f'🔍 INICIANDO validación estructural para: {file_path}')
        
        # VALIDACIÓN PRE-OPERACIÓN
        logger.info('📋 Ejecutando validación PRE-operación...')
        
        # Crear checkpoint antes de la operación
        checkpoint = rollback_manager.create_checkpoint(file_path)
        if not checkpoint:
            logger.warning('No se pudo crear checkpoint - continuando sin protección de rollback')
        
        # Validar sintaxis inicial
        syntax_valid, syntax_error = validator.validate_python_syntax(file_path)
        if not syntax_valid:
            logger.error(f'❌ SINTAXIS INVÁLIDA PRE-operación: {syntax_error}')
            if checkpoint:
                logger.info('Archivo ya tenía problemas - no se aplicará la operación')
                return False
        
        # Validar indentación inicial
        indent_valid, indent_issues = validator.validate_indentation(file_path)
        if not indent_valid:
            logger.warning(f'⚠️ INDENTACIÓN INCONSISTENTE PRE-operación: {len(indent_issues)} problemas')
        
        # Detectar constructos incompletos iniciales
        initial_issues = validator.detect_incomplete_constructs(file_path)
        logger.info(f'📊 Constructos incompletos iniciales: {len(initial_issues)}')
        
        try:
            # EJECUTAR OPERACIÓN ORIGINAL
            logger.info('🚀 Ejecutando operación original...')
            result = func(*args, **kwargs)
            
            # VALIDACIÓN POST-OPERACIÓN
            logger.info('📋 Ejecutando validación POST-operación...')
            
            # Validar sintaxis después de la operación
            post_syntax_valid, post_syntax_error = validator.validate_python_syntax(file_path)
            if not post_syntax_valid:
                logger.error(f'❌ CORRUPCIÓN DETECTADA - Sintaxis inválida POST-operación: {post_syntax_error}')
                
                # ACTIVAR ROLLBACK AUTOMÁTICO
                if checkpoint:
                    logger.info('🔄 ACTIVANDO rollback automático...')
                    rollback_success = rollback_manager.rollback_to_checkpoint(file_path, checkpoint)
                    if rollback_success:
                        logger.info('✅ Rollback exitoso - archivo restaurado')
                        raise StructuralIntegrityError(f'Operación corrupta detectada y revertida: {post_syntax_error}')
                    else:
                        logger.error('❌ ROLLBACK FALLÓ - archivo podría estar corrupto')
                        raise StructuralIntegrityError(f'Operación corrupta Y rollback falló: {post_syntax_error}')
                else:
                    raise StructuralIntegrityError(f'Operación corrupta sin posibilidad de rollback: {post_syntax_error}')
            
            # Validar indentación post-operación
            post_indent_valid, post_indent_issues = validator.validate_indentation(file_path)
            if not post_indent_valid and indent_valid:
                logger.warning(f'⚠️ INDENTACIÓN DEGRADADA POST-operación: {len(post_indent_issues)} nuevos problemas')
            
            # Detectar nuevos constructos incompletos
            final_issues = validator.detect_incomplete_constructs(file_path)
            new_issues_count = len(final_issues) - len(initial_issues)
            if new_issues_count > 0:
                logger.warning(f'⚠️ NUEVOS CONSTRUCTOS INCOMPLETOS: {new_issues_count} detectados')
            
            logger.info('✅ VALIDACIÓN ESTRUCTURAL COMPLETADA - Operación exitosa')
            return result
            
        except StructuralIntegrityError:
            # Re-lanzar errores de integridad estructural
            raise
        except Exception as e:
            logger.error(f'❌ ERROR DURANTE OPERACIÓN: {str(e)}')
            
            # Intentar rollback en caso de excepción
            if checkpoint:
                logger.info('🔄 Intentando rollback por excepción...')
                rollback_success = rollback_manager.rollback_to_checkpoint(file_path, checkpoint)
                if rollback_success:
                    logger.info('✅ Rollback por excepción exitoso')
                else:
                    logger.error('❌ Rollback por excepción falló')
            
            # Re-lanzar la excepción original
            raise
        
        finally:
            # Limpiar checkpoints antiguos
            rollback_manager.cleanup_checkpoints(max_age_hours=1)
    
    return wrapper


class StructuralIntegrityError(Exception):
    """
    Excepción lanzada cuando se detecta corrupción estructural.
    
    Indica que una operación ha causado problemas en la estructura
    del código que requieren rollback automático.
    """
    pass


# Función de utilidad para validación manual
def manual_structural_validation(file_path: str) -> Dict[str, Any]:
    """
    Ejecuta validación estructural manual de un archivo.
    
    Args:
        file_path: Ruta al archivo a validar
        
    Returns:
        Dict con resultados completos de validación
    """
    validator = StructuralValidator()
    
    # Ejecutar todas las validaciones
    syntax_valid, syntax_error = validator.validate_python_syntax(file_path)
    indent_valid, indent_issues = validator.validate_indentation(file_path)
    structure = validator.analyze_structure(file_path)
    incomplete_constructs = validator.detect_incomplete_constructs(file_path)
    
    return {
        'file_path': file_path,
        'syntax': {
            'valid': syntax_valid,
            'error': syntax_error
        },
        'indentation': {
            'valid': indent_valid,
            'issues': indent_issues
        },
        'structure': structure,
        'incomplete_constructs': incomplete_constructs,
        'overall_valid': syntax_valid and indent_valid,
        'total_issues': len(indent_issues) + len(incomplete_constructs)
    }