#!/usr/bin/env python3
"""
Script para probar el exception handler global con FastAPI.
"""
import requests
import time
import subprocess
import sys
from threading import Thread

def start_server():
    """Iniciar servidor FastAPI en background."""
    subprocess.run([
        sys.executable, "-c",
        """
import uvicorn
from app.main import app
uvicorn.run(app, host='127.0.0.1', port=8001, log_level='error')
        """
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def test_exception_handler():
    """Probar exception handler haciendo request a endpoint que falla."""
    print("🧪 PROBANDO EXCEPTION HANDLER")
    print("=" * 50)
    
    # Iniciar servidor en background
    server_thread = Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Esperar que servidor inicie
    print("⏳ Esperando que servidor inicie...")
    time.sleep(3)
    
    try:
        # Hacer request a endpoint que no existe (debería generar excepción)
        print("📡 Haciendo request a endpoint inexistente...")
        response = requests.get("http://127.0.0.1:8001/endpoint-que-no-existe", timeout=5)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response: {response.json()}")
        
    except requests.exceptions.RequestException as e:
        print(f"🔗 Error de conexión (esperado): {e}")
    
    print("✅ Prueba de exception handler completada")

if __name__ == "__main__":
    test_exception_handler()
