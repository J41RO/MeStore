#!/usr/bin/env python3
"""
Script para iniciar servicios limpios de MeStore
"""
import os
import subprocess
import time
import signal
import sys

def kill_existing_services():
    """Termina servicios existentes"""
    print("🛑 Terminando servicios existentes...")

    # Obtener PIDs de procesos usando los puertos
    try:
        # Matar procesos en puerto 8000
        result = subprocess.run(
            ["lsof", "-ti:8000"],
            capture_output=True, text=True, check=False
        )
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"  ✅ Terminado proceso backend PID {pid}")

        # Matar procesos en puerto 5173
        result = subprocess.run(
            ["lsof", "-ti:5173"],
            capture_output=True, text=True, check=False
        )
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"  ✅ Terminado proceso frontend PID {pid}")

    except Exception as e:
        print(f"  ⚠️ Error terminando procesos: {e}")

    # Esperar a que terminen
    time.sleep(3)

def start_backend():
    """Inicia el backend"""
    print("🚀 Iniciando backend limpio...")

    # Configurar variables de entorno
    env = os.environ.copy()
    env.update({
        "DISABLE_REDIS": "1",
        "DISABLE_SEARCH_SERVICE": "1",
        "USE_SIMPLE_AUTH": "1",
        "ENVIRONMENT": "development"
    })

    # Iniciar backend
    backend_cmd = [
        "python", "-m", "uvicorn",
        "app.main:app",
        "--host", "192.168.1.137",
        "--port", "8000",
        "--reload"
    ]

    backend_process = subprocess.Popen(
        backend_cmd,
        env=env,
        cwd="/home/admin-jairo/MeStore",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    print("  ✅ Backend iniciado en http://192.168.1.137:8000")
    time.sleep(5)
    return backend_process

def start_frontend():
    """Inicia el frontend"""
    print("🎨 Iniciando frontend limpio...")

    frontend_cmd = [
        "npm", "run", "dev", "--",
        "--host", "192.168.1.137",
        "--port", "5173"
    ]

    frontend_process = subprocess.Popen(
        frontend_cmd,
        cwd="/home/admin-jairo/MeStore/frontend",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    print("  ✅ Frontend iniciado en http://192.168.1.137:5173")
    time.sleep(3)
    return frontend_process

def main():
    """Función principal"""
    print("🔄 Reiniciando servicios MeStore...")
    print("=" * 50)

    # Terminar servicios existentes
    kill_existing_services()

    # Iniciar servicios nuevos
    backend_process = start_backend()
    frontend_process = start_frontend()

    print("=" * 50)
    print("✅ Servicios iniciados exitosamente:")
    print("📍 Backend: http://192.168.1.137:8000")
    print("📍 Frontend: http://192.168.1.137:5173")
    print("🔐 Login: http://192.168.1.137:5173/auth/login")
    print("")
    print("🧪 Credenciales de prueba:")
    print("   vendor@test.com / vendor123")
    print("   admin@test.com / admin123")
    print("   buyer@test.com / buyer123")
    print("=" * 50)

    try:
        # Mantener servicios corriendo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servicios...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Servicios detenidos")

if __name__ == "__main__":
    main()