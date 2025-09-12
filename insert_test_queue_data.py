#!/usr/bin/env python3
"""
Script para insertar datos de prueba en la tabla incoming_product_queue.
Este script crea productos de prueba con datos variados para testing del workflow.
"""

import sys
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import de modelos
from app.models.incoming_product_queue import IncomingProductQueue, QueuePriority, VerificationStatus, DelayReason
from app.core.database import get_async_database_url

def insert_test_data():
    """Insertar datos de prueba en incoming_product_queue."""
    
    # Obtener URL de conexión síncrona
    database_url = get_async_database_url().replace('postgresql+asyncpg://', 'postgresql://')
    
    print(f"🔗 Conectando a: {database_url}")
    
    # Crear engine y sesión síncrona
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # IDs reales de la base de datos
        product_ids = [
            'd2500220-ceb6-487b-94f4-abe759caae43',  # Producto Test 1
            '51e6f51e-8d47-4c65-9d02-9a3fbe97a099',  # Producto Test 2
            'df1fac2c-1bb9-4696-a6be-77c0fccade81'   # Producto Test 3
        ]
        
        vendor_ids = [
            '1c90b7b0-9223-4fc8-ba03-94c20cd34763',  # Vendedor 1
            'c761efc0-b922-43d5-bdc0-caf4aab21e91',  # Vendedor 2
            '00610b91-fb46-4e44-935f-bde2098284d0'   # Vendedor 3
        ]
        
        # Admin para asignaciones (usando el primer vendedor como admin)
        admin_id = 'c923f9d1-4022-43c1-8a45-fb8dab660731'
        
        # Datos de prueba variados
        test_products = [
            {
                'product_id': product_ids[0],
                'vendor_id': vendor_ids[0],
                'expected_arrival': datetime.now() + timedelta(days=2),
                'verification_status': VerificationStatus.PENDING,
                'priority': QueuePriority.HIGH,
                'tracking_number': 'TRK-001-2024-HIGH',
                'carrier': 'DHL Express',
                'notes': 'Producto prioritario - Cliente VIP',
                'verification_attempts': 0,
                'is_delayed': False
            },
            {
                'product_id': product_ids[1],
                'vendor_id': vendor_ids[1],
                'expected_arrival': datetime.now() + timedelta(days=5),
                'verification_status': VerificationStatus.ASSIGNED,
                'priority': QueuePriority.NORMAL,
                'assigned_to': admin_id,
                'assigned_at': datetime.now() - timedelta(hours=2),
                'tracking_number': 'TRK-002-2024-NORM',
                'carrier': 'FedEx',
                'notes': 'Envío estándar - Verificación rutinaria',
                'verification_notes': 'Asignado para verificación por admin',
                'verification_attempts': 1,
                'is_delayed': False
            },
            {
                'product_id': product_ids[2],
                'vendor_id': vendor_ids[2],
                'expected_arrival': datetime.now() + timedelta(days=1),
                'actual_arrival': datetime.now() + timedelta(days=3),  # Llegó tarde
                'verification_status': VerificationStatus.IN_PROGRESS,
                'priority': QueuePriority.CRITICAL,
                'assigned_to': admin_id,
                'assigned_at': datetime.now() - timedelta(days=1),
                'processing_started_at': datetime.now() - timedelta(hours=6),
                'tracking_number': 'TRK-003-2024-CRIT',
                'carrier': 'UPS',
                'is_delayed': True,
                'delay_reason': DelayReason.TRANSPORT,
                'notes': 'Producto crítico con retraso en transporte',
                'verification_notes': 'Iniciada verificación - Retraso documentado',
                'verification_attempts': 2,
                'deadline': datetime.now() + timedelta(hours=12)  # Deadline pronto
            }
        ]
        
        print("📦 Insertando productos de prueba...")
        
        for i, data in enumerate(test_products):
            print(f"   🔄 Insertando producto {i+1}/3...")
            
            # Crear producto en la cola
            queue_item = IncomingProductQueue(**data)
            session.add(queue_item)
            
            print(f"   ✅ Producto {i+1}: {data['tracking_number']} - {data['verification_status'].value}")
        
        # Commit de todos los cambios
        session.commit()
        print("✅ Todos los productos de prueba insertados exitosamente!")
        
        # Verificar inserción
        count = session.query(IncomingProductQueue).count()
        print(f"📊 Total de productos en cola: {count}")
        
        # Mostrar resumen
        print("\n📋 RESUMEN DE DATOS DE PRUEBA:")
        print("=" * 50)
        
        for item in session.query(IncomingProductQueue).all():
            print(f"🔸 {item.tracking_number}")
            print(f"   Estado: {item.status_display}")
            print(f"   Prioridad: {item.priority_display}")
            print(f"   Carrier: {item.carrier}")
            print(f"   Días en cola: {item.days_in_queue}")
            if item.is_delayed:
                print(f"   ⚠️  RETRASADO: {item.delay_reason.value if item.delay_reason else 'N/A'}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error al insertar datos: {str(e)}")
        session.rollback()
        return False
    finally:
        session.close()
        engine.dispose()

if __name__ == "__main__":
    print("🚀 Iniciando inserción de datos de prueba...")
    success = insert_test_data()
    
    if success:
        print("✅ ¡Datos de prueba insertados exitosamente!")
        print("🌐 Ahora puedes probar el workflow en: http://192.168.1.137:5173/admin-secure-portal/cola-productos-entrantes")
        sys.exit(0)
    else:
        print("❌ Error al insertar datos de prueba!")
        sys.exit(1)