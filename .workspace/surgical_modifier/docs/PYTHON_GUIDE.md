PYTHON - GUÍA COMPLETA
ESTADO: ✅ PERFECTO - NO MODIFICAR
COORDINADOR PRINCIPAL:

CreateCoordinator: Para archivos Python
Ubicación: coordinators/create.py (preservado)
Activación: Automática para archivos .py
Estado: Funcionalidad original intacta

FUNCTIONS ESPECÍFICAS:

validation/: Validación sintaxis Python
formatting/: PEP8, autopep8 integration
analysis/: AST Python parsing
operations/: Operaciones específicas Python

COMANDOS CLI:
Funcionalidad completa original:
bash# Crear archivo Python
python cli.py create models.py "class User:
    def __init__(self, name: str):
        self.name = name
    
    def greet(self):
        return f'Hello, {self.name}!'"

# Reemplazar contenido
python cli.py replace models.py "Hello" "Hi"

# Insertar antes
python cli.py before models.py "def greet(self):" "    # Greeting method"

# Insertar después
python cli.py after models.py "self.name = name" "        self.created_at = datetime.now()"

# Agregar al final
python cli.py append models.py "
if __name__ == '__main__':
    user = User('John')
    print(user.greet())"
CARACTERÍSTICAS PYTHON:
Validación Sintaxis:

AST parsing completo
Detección errores sintaxis
Validación imports

Formateo Código:

PEP8 compliance
Autopep8 integration
Consistent styling

Análisis Código:

Import analysis
Class detection
Function analysis

CASOS DE USO TÍPICOS:
Crear Modelo Django:
bashpython cli.py create models/user.py "from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name"
Agregar Métodos:
bashpython cli.py after models/user.py "def __str__(self):" "    
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'"
Crear API FastAPI:
bashpython cli.py create api/users.py "from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    name: str
    email: str

@app.get('/users')
def get_users():
    return {'users': []}"
FUNCIONALIDAD PRESERVADA:
Backup System:

Backup automático antes de modificaciones
Rollback seguro ante errores
Preservación integridad archivos

Error Handling:

Manejo robusto de errores
Rollback automático
Logging detallado

Performance:

Velocidad original mantenida
Operaciones optimizadas
Zero regresiones

TESTS DE REGRESIÓN:
bash# Verificar funcionalidad Python intacta
python -m pytest tests/regression/test_python_complete.py -v
TROUBLESHOOTING:
Error de Sintaxis:

Verificar indentación Python
Comprobar imports correctos
Validar estructura código

Backup Failures:

Verificar permisos archivos
Comprobar espacio disco
Validar rutas existentes

PRINCIPIO FUNDAMENTAL:
PYTHON FUNCIONA PERFECTAMENTE - NO MODIFICAR NUNCA
