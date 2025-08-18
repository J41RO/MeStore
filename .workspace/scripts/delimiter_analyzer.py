#!/usr/bin/env python3
"""
🔍 ANALIZADOR DE DELIMITADORES v1.0
===================================
Herramienta crítica que analiza el balance exacto de delimitadores en código
detectando llaves sin cerrar, paréntesis sobrantes, comillas desbalanceadas.

USO: python3 delimiter_analyzer.py <archivo> [--braces] [--parentheses] [--brackets] [--quotes] [--context=3]
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


class DelimiterAnalyzer:
    def __init__(self, file_path: str, context_lines: int = 3):
        self.file_path = Path(file_path)
        self.context_lines = context_lines
        self.lines = []
        self.delimiters = {
            'braces': {'open': '{', 'close': '}', 'name': 'Llaves'},
            'parentheses': {'open': '(', 'close': ')', 'name': 'Paréntesis'},
            'brackets': {'open': '[', 'close': ']', 'name': 'Corchetes'},
            'quotes': {'open': '"', 'close': '"', 'name': 'Comillas dobles'},
            'single_quotes': {'open': "'", 'close': "'", 'name': 'Comillas simples'}
        }
        # Regex para detectar tags HTML/JSX
        self.html_tag_regex = re.compile(r'<(/?)([a-zA-Z][a-zA-Z0-9_.-]*)[^>]*?(/?)>')
        self.load_file()

    def load_file(self):
        """Cargar archivo preservando formato exacto"""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.lines = f.readlines()
            print(f"✅ Archivo cargado: {len(self.lines)} líneas")
        except Exception as e:
            print(f"❌ Error cargando archivo: {e}")
            sys.exit(1)

    def analyze_delimiters(self, enabled_delimiters: Dict[str, bool]) -> Dict[str, Any]:
        """Análisis completo de delimitadores con detección de errores"""
        
        analysis_result = {
            'file_info': {
                'path': str(self.file_path),
                'total_lines': len(self.lines),
                'analyzed_delimiters': [name for name, enabled in enabled_delimiters.items() if enabled]
            },
            'balance_status': 'FUNCIONAL',  # FUNCIONAL, ERROR, CRITICO
            'summary': {
                'total_openers': 0,
                'total_closers': 0,
                'valid_pairs': 0,
                'errors': 0
            },
            'valid_matches': [],
            'errors': [],
            'recommendations': []
        }

        # Análisis de tags HTML/JSX si está habilitado
        if enabled_delimiters.get('html_tags', False):
            self._analyze_html_tags(analysis_result)
            
        # Análisis de delimitadores tradicionales
        self._analyze_traditional_delimiters(analysis_result, enabled_delimiters)

        # Determinar estado final
        if analysis_result['summary']['errors'] == 0:
            analysis_result['balance_status'] = 'FUNCIONAL'
            analysis_result['recommendations'].append('✅ Todos los delimitadores están correctamente balanceados')
        else:
            analysis_result['balance_status'] = 'ERROR'
            analysis_result['recommendations'].append(f'❌ Se encontraron {analysis_result["summary"]["errors"]} errores críticos')

        return analysis_result

    def _analyze_html_tags(self, analysis_result: Dict[str, Any]):
        """Analizar tags HTML/JSX"""
        tag_stack = []
        file_content = ''.join(self.lines)
        
        # Tags que se auto-cierran y no necesitan tag de cierre
        self_closing_tags = {
            'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'
        }
        
        for line_num, line in enumerate(self.lines, 1):
            for match in self.html_tag_regex.finditer(line):
                is_closing = bool(match.group(1))  # True si es </tag>
                tag_name = match.group(2).lower()
                is_self_closing = bool(match.group(3)) or tag_name in self_closing_tags
                start_pos = match.start()
                column = start_pos + 1
                
                tag_info = {
                    'tag_name': tag_name,
                    'is_closing': is_closing,
                    'is_self_closing': is_self_closing,
                    'line': line_num,
                    'column': column,
                    'full_tag': match.group(0),
                    'context': self._get_line_context(line_num)
                }
                
                if is_closing:
                    # Tag de cierre
                    analysis_result['summary']['total_closers'] += 1
                    opener = self._find_matching_html_opener(tag_stack, tag_name)
                    
                    if opener:
                        tag_stack.remove(opener)
                        analysis_result['valid_matches'].append({
                            'type': 'html_tags',
                            'opener': opener,
                            'closer': tag_info,
                            'tag_name': tag_name,
                            'nesting_level': len(tag_stack)
                        })
                        analysis_result['summary']['valid_pairs'] += 1
                    else:
                        # Tag de cierre sin apertura
                        error = {
                            'type': 'TAG_CIERRE_SIN_APERTURA',
                            'delimiter_type': 'html_tags',
                            'tag_name': tag_name,
                            'full_tag': tag_info['full_tag'],
                            'line': line_num,
                            'column': column,
                            'context': tag_info['context'],
                            'severity': 'CRITICO',
                            'message': f'Tag de cierre "</{tag_name}>" sin apertura correspondiente'
                        }
                        analysis_result['errors'].append(error)
                        analysis_result['summary']['errors'] += 1
                        
                elif not is_self_closing:
                    # Tag de apertura que necesita cierre
                    analysis_result['summary']['total_openers'] += 1
                    tag_stack.append(tag_info)
        
        # Procesar tags sin cerrar
        for opener in tag_stack:
            error = {
                'type': 'TAG_APERTURA_SIN_CIERRE',
                'delimiter_type': 'html_tags',
                'tag_name': opener['tag_name'],
                'full_tag': opener['full_tag'],
                'line': opener['line'],
                'column': opener['column'],
                'context': opener['context'],
                'severity': 'CRITICO',
                'message': f'Tag de apertura "<{opener["tag_name"]}>" sin cierre correspondiente'
            }
            analysis_result['errors'].append(error)
            analysis_result['summary']['errors'] += 1

    def _find_matching_html_opener(self, tag_stack: List[Dict], tag_name: str) -> Optional[Dict]:
        """Encontrar el tag de apertura correspondiente"""
        for i in range(len(tag_stack) - 1, -1, -1):
            if tag_stack[i]['tag_name'].lower() == tag_name.lower():
                return tag_stack[i]
        return None

    def _analyze_traditional_delimiters(self, analysis_result: Dict[str, Any], enabled_delimiters: Dict[str, bool]):

        """Análisis de delimitadores tradicionales (paréntesis, llaves, etc.)"""
        stack = []
        chars = ''.join(self.lines)
        in_string = False
        string_char = ''
        current_line = 1
        current_column = 1

        for i, char in enumerate(chars):
            # Actualizar posición
            if char == '\n':
                current_line += 1
                current_column = 1
            else:
                current_column += 1

            # Manejo especial para comillas
            if self._is_quote_delimiter(char, enabled_delimiters):
                if not in_string:
                    in_string = True
                    string_char = char
                    stack.append({
                        'char': char,
                        'position': i,
                        'line': current_line,
                        'column': current_column - 1,
                        'type': self._get_quote_type(char),
                        'context': self._get_line_context(current_line)
                    })
                    analysis_result['summary']['total_openers'] += 1
                elif char == string_char:
                    opener = self._find_matching_opener(stack, self._get_quote_type(char))
                    if opener:
                        stack.remove(opener)
                        analysis_result['valid_matches'].append({
                            'type': opener['type'],
                            'opener': opener,
                            'closer': {
                                'char': char,
                                'position': i,
                                'line': current_line,
                                'column': current_column - 1,
                                'context': self._get_line_context(current_line)
                            },
                            'content_length': i - opener['position'] - 1,
                            'nesting_level': len(stack)
                        })
                        analysis_result['summary']['valid_pairs'] += 1
                        in_string = False
                        string_char = ''
                    analysis_result['summary']['total_closers'] += 1
                continue

            # Ignorar contenido dentro de strings
            if in_string:
                continue

            # Procesar otros delimitadores
            delimiter_type = self._get_delimiter_type(char, enabled_delimiters)
            
            if delimiter_type:
                delimiter = self.delimiters[delimiter_type]
                
                if char == delimiter['open']:
                    stack.append({
                        'char': char,
                        'position': i,
                        'line': current_line,
                        'column': current_column - 1,
                        'type': delimiter_type,
                        'context': self._get_line_context(current_line)
                    })
                    analysis_result['summary']['total_openers'] += 1
                    
                elif char == delimiter['close']:
                    analysis_result['summary']['total_closers'] += 1
                    opener = self._find_matching_opener(stack, delimiter_type)
                    
                    if opener:
                        stack.remove(opener)
                        analysis_result['valid_matches'].append({
                            'type': delimiter_type,
                            'opener': opener,
                            'closer': {
                                'char': char,
                                'position': i,
                                'line': current_line,
                                'column': current_column - 1,
                                'context': self._get_line_context(current_line)
                            },
                            'content_length': i - opener['position'] - 1,
                            'nesting_level': len(stack)
                        })
                        analysis_result['summary']['valid_pairs'] += 1
                    else:
                        # Delimitador de cierre sin apertura
                        error = {
                            'type': 'CIERRE_SIN_APERTURA',
                            'delimiter_type': delimiter_type,
                            'char': char,
                            'position': i,
                            'line': current_line,
                            'column': current_column - 1,
                            'context': self._get_line_context(current_line),
                            'severity': 'CRITICO',
                            'message': f'{delimiter["name"]} de cierre "{char}" sin apertura correspondiente'
                        }
                        analysis_result['errors'].append(error)
                        analysis_result['summary']['errors'] += 1

        # Procesar delimitadores sin cerrar
        for opener in stack:
            delimiter = self.delimiters[opener['type']]
            error = {
                'type': 'APERTURA_SIN_CIERRE',
                'delimiter_type': opener['type'],
                'char': opener['char'],
                'position': opener['position'],
                'line': opener['line'],
                'column': opener['column'],
                'context': opener['context'],
                'severity': 'CRITICO',
                'message': f'{delimiter["name"]} de apertura "{opener["char"]}" sin cierre correspondiente'
            }
            analysis_result['errors'].append(error)
            analysis_result['summary']['errors'] += 1

        # Determinar estado final
        if analysis_result['summary']['errors'] == 0:
            analysis_result['balance_status'] = 'FUNCIONAL'
            analysis_result['recommendations'].append('✅ Todos los delimitadores están correctamente balanceados')
        else:
            analysis_result['balance_status'] = 'ERROR'
            analysis_result['recommendations'].append(f'❌ Se encontraron {analysis_result["summary"]["errors"]} errores críticos')

        return analysis_result

    def _is_quote_delimiter(self, char: str, enabled_delimiters: Dict[str, bool]) -> bool:
        """Verificar si el carácter es un delimitador de comillas habilitado"""
        if char == '"' and enabled_delimiters.get('quotes', False):
            return True
        if char == "'" and enabled_delimiters.get('single_quotes', False):
            return True
        return False

    def _get_quote_type(self, char: str) -> str:
        """Obtener tipo de comilla"""
        return 'quotes' if char == '"' else 'single_quotes'

    def _get_delimiter_type(self, char: str, enabled_delimiters: Dict[str, bool]) -> Optional[str]:
        """Determinar tipo de delimitador"""
        for delim_type, enabled in enabled_delimiters.items():
            if enabled and delim_type in self.delimiters:
                delimiter = self.delimiters[delim_type]
                if char == delimiter['open'] or char == delimiter['close']:
                    return delim_type
        return None

    def _find_matching_opener(self, stack: List[Dict], delimiter_type: str) -> Optional[Dict]:
        """Encontrar el delimitador de apertura correspondiente"""
        for i in range(len(stack) - 1, -1, -1):
            if stack[i]['type'] == delimiter_type:
                return stack[i]
        return None

    def _get_line_context(self, line_number: int) -> Dict[str, Any]:
        """Obtener contexto de la línea"""
        line_idx = line_number - 1
        if 0 <= line_idx < len(self.lines):
            line_content = self.lines[line_idx].rstrip('\n\r')
            return {
                'line_content': line_content,
                'indentation': len(line_content) - len(line_content.lstrip()),
                'length': len(line_content)
            }
        return {'line_content': '', 'indentation': 0, 'length': 0}

    def display_analysis_report(self, analysis: Dict[str, Any]):
        """Mostrar reporte completo de análisis"""
        
        print(f"\n🔍 REPORTE DE ANÁLISIS DE DELIMITADORES")
        print("=" * 60)
        
        # Info del archivo
        print(f"📄 ARCHIVO: {analysis['file_info']['path']}")
        print(f"📊 LÍNEAS TOTALES: {analysis['file_info']['total_lines']}")
        print(f"🎯 DELIMITADORES ANALIZADOS: {', '.join(analysis['file_info']['analyzed_delimiters'])}")
        
        # Estado general
        status_icon = "✅" if analysis['balance_status'] == 'FUNCIONAL' else "❌"
        print(f"\n{status_icon} ESTADO GENERAL: {analysis['balance_status']}")
        
        # Resumen estadístico
        print(f"\n📊 RESUMEN ESTADÍSTICO:")
        print(f"  🔓 Total aperturas: {analysis['summary']['total_openers']}")
        print(f"  🔒 Total cierres: {analysis['summary']['total_closers']}")
        print(f"  ✅ Pares válidos: {analysis['summary']['valid_pairs']}")
        print(f"  ❌ Errores: {analysis['summary']['errors']}")

                    # Mostrar errores si existen
        if analysis['errors']:
            print(f"\n❌ ERRORES DETECTADOS ({len(analysis['errors'])}):")
            print("-" * 50)
            
            for i, error in enumerate(analysis['errors'], 1):
                if error['delimiter_type'] == 'html_tags':
                    print(f"\n🚨 ERROR #{i}: {error['type']}")
                    print(f"  🏷️ Tipo: HTML/JSX Tag")
                    print(f"  🔤 Tag: {error['full_tag']}")
                    print(f"  📍 Ubicación: Línea {error['line']}, Columna {error['column']}")
                    print(f"  📝 Contexto: {error['context']['line_content']}")
                    print(f"  💬 Mensaje: {error['message']}")
                else:
                    delimiter_name = self.delimiters[error['delimiter_type']]['name']
                    print(f"\n🚨 ERROR #{i}: {error['type']}")
                    print(f"  🏷️ Tipo: {delimiter_name}")
                    print(f"  🔤 Carácter: '{error['char']}'")
                    print(f"  📍 Ubicación: Línea {error['line']}, Columna {error['column']}")
                    print(f"  📝 Contexto: {error['context']['line_content']}")
                    print(f"  💬 Mensaje: {error['message']}")
                
                # Mostrar contexto ampliado
                if self.context_lines > 0:
                    print(f"  📋 CONTEXTO AMPLIADO:")
                    self._show_context_lines(error['line'])

        # Mostrar coincidencias válidas (resumen)
        if analysis['valid_matches']:
            print(f"\n✅ DELIMITADORES BALANCEADOS ({len(analysis['valid_matches'])}):")
            print("-" * 50)
            
            # Agrupar por tipo
            by_type = {}
            for match in analysis['valid_matches']:
                delim_type = match['type']
                if delim_type not in by_type:
                    by_type[delim_type] = 0
                by_type[delim_type] += 1
            
            for delim_type, count in by_type.items():
                if delim_type == 'html_tags':
                    print(f"  ✅ HTML/JSX Tags: {count} pares correctos")
                else:
                    delimiter_name = self.delimiters[delim_type]['name']
                    print(f"  ✅ {delimiter_name}: {count} pares correctos")

        # Recomendaciones
        print(f"\n💡 RECOMENDACIONES:")
        for recommendation in analysis['recommendations']:
            print(f"  {recommendation}")

        # Comandos de seguimiento
        if analysis['errors']:
            print(f"\n🛠️ COMANDOS DE SEGUIMIENTO SUGERIDOS:")
            for error in analysis['errors'][:3]:  # Mostrar solo los primeros 3
                print(f"  🔍 Revisar línea {error['line']}:")
                print(f"    python3 pattern_extractor.py {self.file_path} \"{error['context']['line_content'].strip()}\" --context=5")

    def _show_context_lines(self, center_line: int):
        """Mostrar líneas de contexto alrededor del error"""
        start_line = max(1, center_line - self.context_lines)
        end_line = min(len(self.lines), center_line + self.context_lines)
        
        for line_num in range(start_line, end_line + 1):
            line_content = self.lines[line_num - 1].rstrip('\n\r')
            marker = "  ►" if line_num == center_line else "   "
            print(f"    {marker} {line_num:3d}: {line_content}")


def main():
    parser = argparse.ArgumentParser(description="Analizador de Delimitadores v1.0")
    parser.add_argument("file", help="Archivo a analizar")
    parser.add_argument("--braces", action="store_true", help="Analizar llaves { }")
    parser.add_argument("--parentheses", action="store_true", help="Analizar paréntesis ( )")
    parser.add_argument("--brackets", action="store_true", help="Analizar corchetes [ ]")
    parser.add_argument("--quotes", action="store_true", help="Analizar comillas dobles \" \"")
    parser.add_argument("--single-quotes", action="store_true", help="Analizar comillas simples ' '")
    parser.add_argument("--html-tags", action="store_true", help="Analizar tags HTML/JSX <div></div>")
    parser.add_argument("--all", action="store_true", help="Analizar todos los delimitadores")
    parser.add_argument("--context", type=int, default=3, help="Líneas de contexto (default: 3)")
    parser.add_argument("--summary-only", action="store_true", help="Mostrar solo resumen")

    args = parser.parse_args()

    # Configurar delimitadores a analizar
    enabled_delimiters = {
        'braces': args.braces or args.all,
        'parentheses': args.parentheses or args.all,
        'brackets': args.brackets or args.all,
        'quotes': args.quotes or args.all,
        'single_quotes': args.single_quotes or args.all,
        'html_tags': args.html_tags or args.all
    }

    # Si no se especifica nada, analizar todos
    if not any(enabled_delimiters.values()):
        enabled_delimiters = {k: True for k in enabled_delimiters.keys()}

    print("🔍 ANALIZADOR DE DELIMITADORES v1.0")
    print("=" * 50)
    print(f"📄 Archivo: {args.file}")
    enabled_list = [k for k, v in enabled_delimiters.items() if v]
    print(f"🎯 Analizando: {', '.join(enabled_list)}")
    print(f"📊 Contexto: {args.context} líneas")
    print()

    analyzer = DelimiterAnalyzer(args.file, args.context)
    analysis = analyzer.analyze_delimiters(enabled_delimiters)

    if args.summary_only:
        print(f"ESTADO: {analysis['balance_status']}")
        print(f"ERRORES: {analysis['summary']['errors']}")
        print(f"PARES_VÁLIDOS: {analysis['summary']['valid_pairs']}")
    else:
        analyzer.display_analysis_report(analysis)

    # Código de salida
    sys.exit(0 if analysis['balance_status'] == 'FUNCIONAL' else 1)


if __name__ == "__main__":
    main()