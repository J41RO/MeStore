#!/usr/bin/env python3
"""
Audit Project Script - Execute comprehensive project analysis
Uses ProjectAuditor to generate detailed project health report
"""

import sys
import os
from pathlib import Path

# Add core functions to Python path
sys.path.insert(0, str(Path(__file__).parent / 'core' / 'functions' / 'detection'))

try:
    from project_auditor import ProjectAuditor
except ImportError as e:
    print(f"ERROR: No se pudo importar ProjectAuditor: {e}")
    print("Verificar que core/functions/detection/project_auditor.py existe")
    sys.exit(1)

def main():
    """Execute complete project audit"""
    print("=" * 60)
    print("SURGICAL MODIFIER v6.0 - AUDITORÍA COMPLETA DEL PROYECTO")
    print("=" * 60)
    
    # Initialize auditor
    auditor = ProjectAuditor()
    
    try:
        # Execute comprehensive analysis
        print("\n1. INICIANDO ANÁLISIS COMPLETO...")
        results = auditor.analyze_project()
        
        print("\n2. GENERANDO REPORTE DETALLADO...")
        # Create reports directory if it doesn't exist
        reports_dir = Path('reports')
        reports_dir.mkdir(exist_ok=True)
        
        # Generate detailed report
        report_file = 'reports/project_audit.json'
        report_content = auditor.generate_report(report_file)
        
        print(f"\n3. REPORTE GUARDADO EN: {report_file}")
        
        # Display summary
        print("\n" + "=" * 60)
        print("RESUMEN EJECUTIVO DE LA AUDITORÍA")
        print("=" * 60)
        
        summary = results
        file_inventory = summary.get('file_inventory', {})
        backup_analysis = summary.get('backup_analysis', {})
        functionality = summary.get('functionality_status', {})
        quality = summary.get('code_quality', {})
        
        print(f"📁 INVENTARIO DE ARCHIVOS:")
        print(f"   • Total archivos: {file_inventory.get('total_files', 0)}")
        print(f"   • Archivos Python: {len(file_inventory.get('python_files', []))}")
        print(f"   • Archivos backup: {len(file_inventory.get('backup_files', []))}")
        print(f"   • Archivos de test: {len(file_inventory.get('test_files', []))}")
        
        print(f"\n🔧 ESTADO FUNCIONAL:")
        print(f"   • CLI funcional: {'SÍ' if functionality.get('cli_functional', False) else 'NO'}")
        print(f"   • Operaciones disponibles: {len(functionality.get('operations_available', []))}")
        operations = functionality.get('operations_available', [])
        if operations:
            print(f"   • Lista: {', '.join(operations)}")
        
        print(f"\n📊 CALIDAD DEL CÓDIGO:")
        print(f"   • Total líneas: {quality.get('total_lines', 0)}")
        print(f"   • Promedio líneas/archivo: {quality.get('avg_file_size', 0):.1f}")
        print(f"   • Archivos grandes (>500 líneas): {len(quality.get('large_files', []))}")
        print(f"   • TODOs/FIXMEs: {quality.get('todo_fixme_count', 0)}")
        
        print(f"\n🧹 ANÁLISIS DE LIMPIEZA:")
        print(f"   • Archivos backup total: {backup_analysis.get('total_backup_files', 0)}")
        size_mb = backup_analysis.get('size_savings', 0) / (1024 * 1024)
        print(f"   • Espacio potencial a liberar: {size_mb:.1f} MB")
        
        patterns = backup_analysis.get('backup_patterns', {})
        if patterns:
            print(f"   • Patrones de backup encontrados:")
            for pattern, count in patterns.items():
                print(f"     - {pattern}: {count} archivos")
        
        print(f"\n💡 RECOMENDACIONES:")
        recommendations = summary.get('recommendations', [])
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        # Determine project readiness
        cli_ok = functionality.get('cli_functional', False)
        backup_count = backup_analysis.get('total_backup_files', 0)
        
        print(f"\n" + "=" * 60)
        if cli_ok and backup_count < 100:
            print("✅ PROYECTO LISTO PARA REESTRUCTURACIÓN v6.0")
            print("   • Funcionalidad core verificada")
            print("   • Limpieza recomendada pero no crítica")
        elif cli_ok:
            print("⚠️  PROYECTO FUNCIONAL - LIMPIEZA REQUERIDA")
            print("   • Funcionalidad core verificada")
            print(f"   • {backup_count} archivos backup requieren limpieza")
        else:
            print("🚨 PROYECTO REQUIERE REPARACIÓN")
            print("   • cli.py no funcional - reparación crítica necesaria")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"\n🚨 ERROR DURANTE LA AUDITORÍA: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)