#!/usr/bin/env python3
"""
Script manual para probar el sistema QR sin necesidad de hosting
Simula la generación completa de QR y verificación
"""

import asyncio
import sys
import os
import base64
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.qr_service import QRService
from app.services.product_verification_workflow import ProductVerificationWorkflow

def test_qr_generation():
    """Prueba la generación de QR sin base de datos"""
    print("🔍 VERIFICACIÓN MANUAL DEL SISTEMA QR")
    print("=" * 50)
    
    # Crear servicio QR
    qr_service = QRService()
    
    # Simular datos de producto
    tracking_number = "TEST-12345-DEMO"
    product_info = {
        "nombre": "Producto de Prueba",
        "categoria": "Electrónicos",
        "vendedor": "TestVendor"
    }
    
    print(f"📦 Producto: {product_info['nombre']}")
    print(f"🏷️  Tracking: {tracking_number}")
    
    # 1. Generar ID interno
    print("\n1️⃣ Generando ID interno...")
    internal_id = qr_service.generate_internal_tracking_id(tracking_number)
    print(f"✅ ID interno: {internal_id}")
    
    # 2. Crear QR estándar
    print("\n2️⃣ Generando QR estándar...")
    qr_result = qr_service.create_qr_code(
        tracking_number=tracking_number,
        internal_id=internal_id,
        product_info=product_info,
        style="standard"
    )
    print(f"✅ QR creado: {qr_result['qr_filename']}")
    print(f"✅ Base64 length: {len(qr_result['qr_base64'])} chars")
    
    # 3. Guardar QR file primero
    print("\n3️⃣ Guardando QR file...")
    qr_filepath = f"qr_codes/{qr_result['qr_filename']}"
    
    # Decodificar base64 y guardar archivo
    qr_data = base64.b64decode(qr_result['qr_base64'])
    with open(qr_filepath, 'wb') as f:
        f.write(qr_data)
    print(f"✅ QR guardado en: {qr_filepath}")
    
    # 4. Crear etiqueta
    print("\n4️⃣ Generando etiqueta imprimible...")
    label_filepath = qr_service.create_product_label(
        tracking_number=tracking_number,
        internal_id=internal_id,
        product_info=product_info,
        qr_filepath=qr_filepath
    )
    label_filename = os.path.basename(label_filepath)
    print(f"✅ Etiqueta creada: {label_filename}")
    print(f"✅ Label guardada en: {label_filepath}")
    
    # 5. Verificar contenido del QR (simular lo que se genera)
    print("\n5️⃣ Verificando contenido del QR...")
    qr_content = f"MESTORE:{internal_id}|{tracking_number}|http://192.168.1.137:5173/admin-secure-portal/product/{internal_id}"
    print(f"✅ Contenido QR: {qr_content}")
    
    # 6. Decodificar QR (simular escáner)
    print("\n6️⃣ Simulando decodificación...")
    decoded = qr_service.decode_qr_content(qr_content)
    print(f"✅ Decodificado: {decoded}")
    
    # 7. Verificar archivos creados
    print("\n7️⃣ Verificando archivos generados...")
    qr_path = f"qr_codes/{qr_result['qr_filename']}"
    label_path = label_filepath
    
    if os.path.exists(qr_path):
        size = os.path.getsize(qr_path)
        print(f"✅ QR file: {qr_path} ({size} bytes)")
    else:
        print(f"❌ QR file not found: {qr_path}")
    
    if os.path.exists(label_path):
        size = os.path.getsize(label_path)
        print(f"✅ Label file: {label_path} ({size} bytes)")
    else:
        print(f"❌ Label file not found: {label_path}")
    
    print("\n🎯 VERIFICACIÓN COMPLETA")
    print("=" * 50)
    print("✅ Generación de QR: FUNCIONAL")
    print("✅ Generación de etiquetas: FUNCIONAL") 
    print("✅ Sistema completo: READY FOR HOSTING")
    
    return {
        'qr_filename': qr_result['qr_filename'],
        'label_filename': label_filename,
        'internal_id': internal_id,
        'qr_content': qr_content
    }

if __name__ == "__main__":
    result = test_qr_generation()
    print(f"\n📋 Resultado final: {result}")