#!/usr/bin/env python3
"""
🎯 EXTRACTOR DE PATRÓN EXACTO v1.0
===================================
Herramienta crítica que extrae el patrón EXACTO de cualquier línea de código
incluyendo espacios, indentación, caracteres especiales y contexto.

USO: python3 pattern_extractor.py <archivo> <término_buscar> [--context=3]
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class PatternExtractor:
    def __init__(self, file_path: str, context_lines: int = 3):
        self.file_path = Path(file_path)
        self.context_lines = context_lines
        self.lines = []
        self.load_file()

    def load_file(self):
        """Cargar archivo preservando espacios y caracteres especiales exactos"""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.lines = f.readlines()
            print(f"✅ Archivo cargado: {len(self.lines)} líneas")
        except Exception as e:
            print(f"❌ Error cargando archivo: {e}")
            sys.exit(1)

    def find_patterns(self, search_term: str) -> List[Dict]:
        """Buscar todas las ocurrencias del término y extraer patrón exacto"""
        matches = []

        for line_num, line in enumerate(self.lines, 1):
            if search_term.lower() in line.lower():
                pattern_info = self.extract_exact_pattern(line_num, line, search_term)
                matches.append(pattern_info)

        return matches

    def extract_exact_pattern(self, line_num: int, line: str, search_term: str) -> Dict:
        """Extraer información exacta del patrón incluyendo todos los detalles"""

        # Análisis de indentación
        leading_spaces = len(line) - len(line.lstrip())
        indentation_char = (
            "spaces"
            if line.startswith(" ")
            else "tabs" if line.startswith("\t") else "none"
        )

        # Análisis de la línea completa
        line_without_newline = line.rstrip("\n\r")
        trailing_spaces = len(line_without_newline) - len(line_without_newline.rstrip())

        # Detectar caracteres especiales
        special_chars = []
        for char in line_without_newline:
            if not char.isalnum() and not char.isspace() and char not in special_chars:
                special_chars.append(char)

        # Contexto antes y después
        context_before = self.get_context_lines(line_num, -self.context_lines, 0)
        context_after = self.get_context_lines(line_num, 1, self.context_lines + 1)

        return {
            "line_number": line_num,
            "exact_line": line_without_newline,
            "raw_line_with_newline": repr(line),
            "indentation": {
                "spaces_count": leading_spaces,
                "type": indentation_char,
                "exact_prefix": line[:leading_spaces] if leading_spaces > 0 else "",
            },
            "content": {
                "stripped": line.strip(),
                "trailing_spaces": trailing_spaces,
                "length": len(line_without_newline),
            },
            "special_characters": special_chars,
            "context": {"before": context_before, "after": context_after},
            "surgical_ready": self.prepare_surgical_pattern(line_without_newline),
        }

    def get_context_lines(
        self, center_line: int, start_offset: int, end_offset: int
    ) -> List[str]:
        """Obtener líneas de contexto alrededor de la línea objetivo"""
        start_idx = max(0, center_line + start_offset - 1)
        end_idx = min(len(self.lines), center_line + end_offset - 1)

        context = []
        for i in range(start_idx, end_idx):
            if i != center_line - 1:  # Excluir la línea central
                context.append(f"{i+1}: {self.lines[i].rstrip()}")

        return context

    def prepare_surgical_pattern(self, line: str) -> str:
        """Preparar patrón listo para usar con surgical_modifier"""
        # Escapar caracteres especiales para grep
        escaped = line

        # Caracteres que necesitan escape en grep
        special_grep_chars = [
            "[",
            "]",
            "(",
            ")",
            "{",
            "}",
            ".",
            "*",
            "+",
            "?",
            "^",
            "$",
            "|",
            "\\",
        ]

        for char in special_grep_chars:
            if char in escaped:
                escaped = escaped.replace(char, f"\\{char}")

        return escaped

    def display_match_details(self, match: Dict, index: int):
        """Mostrar detalles completos de una coincidencia"""
        print(f"\n🎯 COINCIDENCIA #{index + 1}")
        print("=" * 50)

        print(f"📍 UBICACIÓN:")
        print(f"  📄 Archivo: {self.file_path}")
        print(f"  📊 Línea: {match['line_number']}")

        print(f"\n📝 CONTENIDO EXACTO:")
        print(f"  💾 Línea completa: {repr(match['exact_line'])}")
        print(f"  📏 Longitud: {match['content']['length']} caracteres")

        print(f"\n🔍 INDENTACIÓN:")
        print(f"  📐 Espacios iniciales: {match['indentation']['spaces_count']}")
        print(f"  🏷️ Tipo: {match['indentation']['type']}")
        if match["indentation"]["exact_prefix"]:
            print(f"  📋 Prefijo exacto: {repr(match['indentation']['exact_prefix'])}")

        print(f"\n⚙️ CARACTERES ESPECIALES:")
        if match["special_characters"]:
            print(f"  🔧 Detectados: {', '.join(match['special_characters'])}")
        else:
            print(f"  ✅ Sin caracteres especiales")

        if match["content"]["trailing_spaces"] > 0:
            print(f"\n⚠️ ESPACIOS FINALES: {match['content']['trailing_spaces']}")

        print(f"\n📋 CONTEXTO ANTERIOR:")
        for line in match["context"]["before"]:
            print(f"    {line}")

        print(f"\n📍 LÍNEA OBJETIVO:")
        print(f"    {match['line_number']}: {match['exact_line']}")

        print(f"\n📋 CONTEXTO POSTERIOR:")
        for line in match["context"]["after"]:
            print(f"    {line}")

        print(f"\n🛠️ PATRÓN PARA SURGICAL_MODIFIER:")
        print(f"  🎯 Usar exactamente: '{match['surgical_ready']}'")

        print(f"\n✅ COMANDO LISTO:")
        print(f"  python3 .workspace/scripts/surgical_modifier_ultimate.py")
        print(f"  --verbose [operación] {self.file_path}")
        print(f"  '{match['surgical_ready']}'")
        print(f"  '[nuevo_contenido]'")

    def verify_pattern_uniqueness(self, matches: List[Dict]) -> Dict:
        """Verificar que el patrón aparece exactamente una vez"""
        verification = {
            "count": len(matches),
            "is_unique": len(matches) == 1,
            "is_safe_for_surgical": False,
            "recommendation": "",
        }

        if verification["count"] == 0:
            verification["recommendation"] = (
                "❌ Patrón no encontrado. Verificar término de búsqueda."
            )
        elif verification["count"] == 1:
            verification["is_safe_for_surgical"] = True
            verification["recommendation"] = (
                "✅ Patrón único encontrado. SEGURO para surgical_modifier."
            )
        else:
            verification["recommendation"] = (
                f"⚠️ {verification['count']} coincidencias. PELIGROSO para surgical_modifier. Usar patrón más específico."
            )

        return verification


def main():
    parser = argparse.ArgumentParser(description="Extractor de Patrón Exacto v1.0")
    parser.add_argument("file", help="Archivo a analizar")
    parser.add_argument("search_term", help="Término a buscar")
    parser.add_argument(
        "--context", type=int, default=3, help="Líneas de contexto (default: 3)"
    )
    parser.add_argument(
        "--show-all", action="store_true", help="Mostrar todas las coincidencias"
    )

    args = parser.parse_args()

    print("🎯 EXTRACTOR DE PATRÓN EXACTO v1.0")
    print("=" * 50)
    print(f"📄 Archivo: {args.file}")
    print(f"🔍 Buscando: '{args.search_term}'")
    print(f"📊 Contexto: {args.context} líneas")
    print()

    extractor = PatternExtractor(args.file, args.context)
    matches = extractor.find_patterns(args.search_term)

    print(f"📊 RESULTADO DE BÚSQUEDA:")
    print(f"  🎯 Coincidencias encontradas: {len(matches)}")

    verification = extractor.verify_pattern_uniqueness(matches)
    print(f"  {verification['recommendation']}")

    if matches:
        if args.show_all or len(matches) == 1:
            for i, match in enumerate(matches):
                extractor.display_match_details(match, i)
        else:
            print(f"\n⚠️ Múltiples coincidencias detectadas.")
            print(f"💡 Use --show-all para ver todas, o refine el término de búsqueda.")
            print(f"\n📋 VISTA RÁPIDA DE COINCIDENCIAS:")
            for i, match in enumerate(matches):
                print(
                    f"  {i+1}. Línea {match['line_number']}: {match['exact_line'][:60]}..."
                )

    # Conclusión y recomendaciones
    print(f"\n📋 RECOMENDACIONES:")
    if verification["is_safe_for_surgical"]:
        print(f"  ✅ SEGURO: Usar el patrón con surgical_modifier")
        print(f"  🎯 Patrón exacto verificado y único")
    else:
        print(f"  ⚠️ PELIGROSO: NO usar surgical_modifier hasta refinar patrón")
        print(f"  🔍 Refinar término de búsqueda para obtener resultado único")


if __name__ == "__main__":
    main()
