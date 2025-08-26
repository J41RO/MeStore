#!/usr/bin/env python3
"""
Cleanup Project Script - Execute safe project cleanup
Uses CleanupManager to clean backup and temporary files safely
"""

import sys
import os
from pathlib import Path

# Add core functions to Python path
sys.path.insert(0, str(Path(__file__).parent / 'core' / 'functions' / 'validation'))

try:
    from cleanup_manager import CleanupManager
except ImportError as e:
    print(f"ERROR: No se pudo importar CleanupManager: {e}")
    print("Verificar que core/functions/validation/cleanup_manager.py existe")
    sys.exit(1)

def main():
    """Execute controlled project cleanup"""
    print("=" * 60)
    print("SURGICAL MODIFIER v6.0 - LIMPIEZA CONTROLADA DEL PROYECTO")
    print("=" * 60)
    
    # Initialize cleanup manager
    cleaner = CleanupManager()
    
    try:
        print("\n1. CREANDO BACKUP DE SEGURIDAD...")
        backup_path = cleaner.create_safety_backup()
        print(f"✅ Backup creado en: {backup_path}")
        
        print("\n2. IDENTIFICANDO CANDIDATOS PARA LIMPIEZA...")
        candidates = cleaner.identify_cleanup_candidates()
        
        # Display candidates summary
        print("\nCANDIDATOS IDENTIFICADOS:")
        total_files = 0
        for category, files in candidates.items():
            count = len(files)
            total_files += count
            if count > 0:
                print(f"   • {category}: {count} archivos")
        
        print(f"\n   TOTAL A ELIMINAR: {total_files} archivos")
        
        print("\n3. VALIDANDO SEGURIDAD DE LA OPERACIÓN...")
        validation = cleaner.validate_cleanup_safety(candidates)
        
        size_mb = validation['size_savings'] / (1024 * 1024) if validation['size_savings'] > 0 else 0
        print(f"✅ Espacio a liberar: {size_mb:.1f} MB")
        
        if validation['warnings']:
            print("\n⚠️  ADVERTENCIAS:")
            for warning in validation['warnings']:
                print(f"   • {warning}")
        
        if validation['critical_files_found']:
            print("\n🚨 ARCHIVOS CRÍTICOS ENCONTRADOS - ABORTANDO:")
            for critical in validation['critical_files_found']:
                print(f"   • {critical}")
            return 1
        
        if not validation['safe_to_proceed']:
            print("\n🚨 LIMPIEZA NO SEGURA - ABORTANDO OPERACIÓN")
            return 1
        
        print("\n4. EJECUTANDO LIMPIEZA SEGURA...")
        cleanup_results = cleaner.execute_cleanup(candidates, confirm=False)
        
        if cleanup_results['status'] == 'completed':
            print(f"✅ LIMPIEZA COMPLETADA")
            print(f"   • Archivos eliminados: {cleanup_results['files_deleted']}")
            
            if cleanup_results['errors']:
                print(f"   • Errores durante limpieza: {len(cleanup_results['errors'])}")
                print("   • Revisar cleanup.log para detalles")
        else:
            print(f"⚠️ LIMPIEZA: {cleanup_results.get('status', 'unknown')}")
            return 1
        
        print("\n5. VERIFICANDO INTEGRIDAD POST-LIMPIEZA...")
        integrity = cleaner.verify_post_cleanup_integrity()
        
        print("VERIFICACIÓN DE INTEGRIDAD:")
        print(f"   • CLI funcional: {'SÍ' if integrity['cli_functional'] else 'NO'}")
        print(f"   • Archivos críticos presentes: {'SÍ' if integrity['critical_files_present'] else 'NO'}")
        print(f"   • Tests pasando: {'SÍ' if integrity['tests_passing'] else 'NO/SKIP'}")
        
        if integrity['import_errors']:
            print("   • Errores de importación:")
            for error in integrity['import_errors']:
                print(f"     - {error}")
        
        print("\n" + "=" * 60)
        if integrity['cli_functional'] and integrity['critical_files_present']:
            print("✅ LIMPIEZA EXITOSA - PROYECTO FUNCIONAL")
            print("   • Funcionalidad core verificada")
            print("   • Integridad del proyecto mantenida")
            print(f"   • {cleanup_results['files_deleted']} archivos eliminados")
            print(f"   • {size_mb:.1f} MB liberados")
        else:
            print("⚠️ LIMPIEZA CON ADVERTENCIAS")
            print("   • Revisar integridad del proyecto")
            print(f"   • Backup disponible en: {backup_path}")
        print("=" * 60)
        
        # Generate final report
        print("\n6. GENERANDO REPORTE FINAL...")
        cleaner.cleanup_report = cleanup_results
        final_report = cleaner.generate_cleanup_report()
        
        # Save cleanup report
        reports_dir = Path('reports')
        reports_dir.mkdir(exist_ok=True)
        
        import json
        from datetime import datetime
        
        report_file = reports_dir / f"cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'cleanup_results': cleanup_results,
                'integrity_check': integrity,
                'backup_location': backup_path,
                'final_report': final_report
            }, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Reporte final guardado en: {report_file}")
        
        return 0 if integrity['cli_functional'] and integrity['critical_files_present'] else 1
        
    except Exception as e:
        print(f"\n🚨 ERROR DURANTE LA LIMPIEZA: {e}")
        import traceback
        traceback.print_exc()
        print(f"\nEn caso de problemas, restaurar desde backup: {backup_path if 'backup_path' in locals() else 'no creado'}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)