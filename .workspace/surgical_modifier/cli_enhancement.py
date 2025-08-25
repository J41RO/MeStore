# Código para agregar al CLI existente
import argparse
import sys
from utils.pattern_analyzer import analyze_pattern_safety, suggest_unique_alternatives
from core.operations.basic.after_enhanced import enhanced_after_operation_with_occurrence

def add_enhanced_arguments(parser):
    """Agregar argumentos para funcionalidades avanzadas"""
    # Nuevas opciones para patrones
    parser.add_argument('--occurrence', type=int, default=1, 
                       help='Qué ocurrencia usar (1=primera, 2=segunda, etc.)')
    parser.add_argument('--context-before', 
                       help='Contexto requerido antes del patrón')
    parser.add_argument('--context-after', 
                       help='Contexto requerido después del patrón')
    parser.add_argument('--analyze-pattern', action='store_true', 
                       help='Analizar seguridad del patrón')
    parser.add_argument('--suggest-unique', type=int, 
                       help='Sugerir patrones únicos para línea N')
    return parser

def handle_pattern_analysis(args):
    """Manejar análisis de patrones"""
    if args.analyze_pattern and args.file and args.pattern:
        analysis = analyze_pattern_safety(args.file, args.pattern)
        
        print(f"ANÁLISIS DE PATRÓN: '{args.pattern}'")
        print(f"Archivo: {args.file}")
        print(f"Ocurrencias encontradas: {analysis['total_occurrences']}")
        print(f"Nivel de riesgo: {analysis['risk_level']}")
        print(f"Recomendación: {analysis['recommendation']}")
        
        if analysis['total_occurrences'] > 1:
            print("\nOCURRENCIAS:")
            for i, occ in enumerate(analysis['occurrences'][:5], 1):
                print(f"  {i}. Línea {occ['line_number']}: {occ['content']}")
        
        sys.exit(0)
    
    # Modo sugerencias
    if args.suggest_unique and args.file:
        suggestions = suggest_unique_alternatives(args.file, args.suggest_unique)
        print(f"PATRONES ÚNICOS SUGERIDOS para línea {args.suggest_unique}:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")
        sys.exit(0)

def handle_enhanced_after(args):
    """Manejar operación AFTER mejorada"""
    if args.operation == 'after':
        result = enhanced_after_operation_with_occurrence(
            args.file, args.pattern, args.content, 
            occurrence=args.occurrence,
            context_before=args.context_before or "",
            context_after=args.context_after or ""
        )
        
        if result['success']:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ Error: {result['error']}")
            if 'suggestion' in result:
                print(f"💡 Sugerencia: {result['suggestion']}")
        
        return result['success']
