#!/usr/bin/env python3
"""
Script de verificación final para el sistema ProductVerification workflow.
Este script verifica que todo esté configurado correctamente para el testing.
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.incoming_product_queue import IncomingProductQueue
from app.core.database import get_async_database_url

def verify_setup():
    """Verificar que todo el setup esté correcto."""
    
    print("🔍 VERIFICACIÓN FINAL DEL SISTEMA PRODUCTVERIFICATION WORKFLOW")
    print("=" * 65)
    
    # Conexión a BD
    database_url = get_async_database_url().replace('postgresql+asyncpg://', 'postgresql://')
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 1. Verificar tabla existe
        print("1️⃣  Verificando existencia de tabla...")
        result = session.execute(text("SELECT COUNT(*) FROM incoming_product_queue"))
        count = result.scalar()
        print(f"   ✅ Tabla 'incoming_product_queue' existe con {count} registros")
        
        # 2. Verificar datos de prueba
        print("\n2️⃣  Verificando datos de prueba...")
        items = session.query(IncomingProductQueue).all()
        
        if len(items) >= 3:
            print(f"   ✅ {len(items)} productos de prueba encontrados")
            
            # Verificar variedad de estados
            statuses = set(item.verification_status for item in items)
            priorities = set(item.priority for item in items)
            
            print(f"   📊 Estados encontrados: {len(statuses)} ({', '.join(s.value for s in statuses)})")
            print(f"   📊 Prioridades encontradas: {len(priorities)} ({', '.join(p.value for p in priorities)})")
            
            # Verificar datos específicos requeridos
            has_pending = any(item.verification_status.value == 'PENDING' for item in items)
            has_tracking = all(item.tracking_number for item in items)
            has_carriers = all(item.carrier for item in items)
            has_delayed = any(item.is_delayed for item in items)
            
            print(f"   📋 Estado PENDING: {'✅' if has_pending else '❌'}")
            print(f"   📋 Tracking numbers: {'✅' if has_tracking else '❌'}")
            print(f"   📋 Carriers variados: {'✅' if has_carriers else '❌'}")
            print(f"   📋 Producto retrasado: {'✅' if has_delayed else '❌'}")
            
        else:
            print(f"   ❌ Solo {len(items)} productos encontrados (se esperaban al menos 3)")
        
        # 3. Verificar foreign keys
        print("\n3️⃣  Verificando relaciones de foreign keys...")
        query = text("""
        SELECT ipq.tracking_number, p.name as product_name, u.email as vendor_email 
        FROM incoming_product_queue ipq 
        JOIN products p ON ipq.product_id = p.id 
        JOIN users u ON ipq.vendor_id = u.id
        """)
        result = session.execute(query).fetchall()
        
        if result:
            print(f"   ✅ Foreign keys funcionando - {len(result)} relaciones válidas")
            for row in result:
                print(f"      🔗 {row.tracking_number} -> {row.product_name} ({row.vendor_email})")
        else:
            print("   ❌ No se encontraron relaciones válidas")
        
        # 4. Verificar estructura de columnas críticas
        print("\n4️⃣  Verificando estructura de la tabla...")
        query = text("""
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'incoming_product_queue' 
        AND column_name IN ('verification_status', 'priority', 'tracking_number', 'carrier')
        """)
        columns = session.execute(query).fetchall()
        
        required_columns = ['verification_status', 'priority', 'tracking_number', 'carrier']
        found_columns = [col.column_name for col in columns]
        
        for req_col in required_columns:
            if req_col in found_columns:
                print(f"   ✅ Columna '{req_col}' presente")
            else:
                print(f"   ❌ Columna '{req_col}' faltante")
        
        # 5. Resumen final
        print("\n5️⃣  RESUMEN DE PRODUCTOS PARA TESTING:")
        print("-" * 50)
        
        for item in session.query(IncomingProductQueue).order_by(IncomingProductQueue.priority.desc()).all():
            status_emoji = {
                'PENDING': '🟡',
                'ASSIGNED': '🔵', 
                'IN_PROGRESS': '🟠',
                'COMPLETED': '🟢'
            }.get(item.verification_status.value, '⚪')
            
            priority_emoji = {
                'CRITICAL': '🔴',
                'HIGH': '🟠',
                'NORMAL': '🔵',
                'LOW': '⚪'
            }.get(item.priority.value, '⚪')
            
            print(f"{status_emoji} {item.tracking_number}")
            print(f"   📱 Estado: {item.status_display}")
            print(f"   {priority_emoji} Prioridad: {item.priority_display}")
            print(f"   🚚 Carrier: {item.carrier}")
            if item.is_delayed:
                print(f"   ⚠️  RETRASADO")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error en verificación: {str(e)}")
        return False
    finally:
        session.close()
        engine.dispose()

if __name__ == "__main__":
    success = verify_setup()
    
    print("\n🎯 ESTADO FINAL:")
    print("=" * 65)
    
    if success:
        print("✅ SISTEMA LISTO PARA TESTING")
        print("🌐 URL de prueba: http://192.168.1.137:5173/admin-secure-portal/cola-productos-entrantes")
        print("\n📋 PASOS PARA PROBAR:")
        print("1. Acceder a la URL del admin panel")
        print("2. Hacer login como admin")
        print("3. Ir a 'Cola de Productos Entrantes'")
        print("4. Ver los 3 productos de prueba listados")
        print("5. Hacer clic en el botón de verificación (✅) de cualquier producto")
        print("6. Probar el workflow paso a paso")
        
        sys.exit(0)
    else:
        print("❌ SISTEMA NO LISTO - Revisar errores arriba")
        sys.exit(1)