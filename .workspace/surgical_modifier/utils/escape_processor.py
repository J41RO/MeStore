#!/usr/bin/env python3
"""
EscapeProcessor - Procesador mejorado para escape de caracteres
Integrado con SmartContentProcessor para máxima eficiencia
"""
import re

# Typing imports cleaned for pre-commit

try:
    from utils.smart_content_processor import SmartContentProcessor

    SMART_PROCESSOR_AVAILABLE = True
except ImportError:
    SMART_PROCESSOR_AVAILABLE = False

try:
    from utils.logger import get_logger

    logger = get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


def process_content_escapes(content):
    """
    Función principal para procesar escapes de contenido.
    Usa SmartContentProcessor si está disponible, fallback a regex básico.

    Args:
        content (str): Content with potential escape sequences
    Returns:
        str: Content with properly processed escape sequences
    """
    if not content:
        return content

    # Usar SmartContentProcessor si está disponible
    if SMART_PROCESSOR_AVAILABLE:
        try:
            return SmartContentProcessor.smart_content_processing(content, "general")
        except Exception as e:
            logger.warning(f"SmartContentProcessor failed, using fallback: {e}")

    # Fallback: procesamiento básico con regex
    try:
        # Convertir escapes básicos
        processed = re.sub(r"(?<!\\)\\n", "\n", content)
        processed = re.sub(r"(?<!\\)\\t", "\t", processed)
        processed = re.sub(r"(?<!\\)\\'", "'", processed)
        processed = re.sub(r'(?<!\\)\\"', '"', processed)
        return processed
    except Exception as e:
        logger.error(f"Error in fallback processing: {e}")
        return content


class EscapeProcessor:
    """Procesador avanzado para casos complejos de escape"""

    def __init__(self):
        """Inicializa el EscapeProcessor"""
        self.logger = logger
        self.logger.info("EscapeProcessor inicializado correctamente")

    def fix_escape_issues(self, content: str, issue_type: str) -> str:
        """Corrige problemas específicos de escape"""
        if not content:
            return content

        # Delegar al SmartContentProcessor si está disponible
        if SMART_PROCESSOR_AVAILABLE:
            try:
                return SmartContentProcessor.smart_content_processing(
                    content, issue_type
                )
            except Exception as e:
                self.logger.warning(f"SmartContentProcessor failed: {e}")

        # Fallback básico
        return process_content_escapes(content)

    def analyze_escape_patterns(self, content: str) -> dict:
        """Analiza patrones de escape en contenido"""
        analysis = {"total_escapes": 0, "escape_types": {}, "problematic_sequences": []}

        if not content:
            return analysis

        try:
            # Contar diferentes tipos de escape
            patterns = {
                "newlines": r"\\n",
                "tabs": r"\\t",
                "quotes": r'\\"',
                "single_quotes": r"\\'",
                "backslashes": r"\\\\",
            }

            for name, pattern in patterns.items():
                matches = re.findall(pattern, content)
                if matches:
                    analysis["escape_types"][name] = len(matches)
                    analysis["total_escapes"] += len(matches)

            return analysis
        except Exception as e:
            self.logger.error(f"Error analyzing escape patterns: {e}")
            return analysis
