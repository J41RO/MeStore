# 📚 CodeCraft Ultimate v6.0 - Manual de Uso Completo

## 🚀 Introducción

**CodeCraft Ultimate v6.0** es la evolución definitiva de las herramientas de modificación quirúrgica de código hacia una plataforma completa de desarrollo colaborativo IA-humano.

## 📦 Instalación Rápida

```bash
# 1. Navegar al directorio
cd /workspace/codecraft_ultimate

# 2. Instalar dependencias
pip install -e .

# 3. Verificar instalación
python3 codecraft.py --help
```

## 🎯 Comandos Básicos

### Operaciones Quirúrgicas (Mejoradas desde v5.3)

```bash
# Crear archivo nuevo
python3 codecraft.py create src/app.py "print('Hola CodeCraft')"

# Reemplazar contenido
python3 codecraft.py replace src/app.py "Hola" "Buenos días"

# Insertar después de un patrón
python3 codecraft.py after src/app.py "print" "# Comentario añadido"

# Insertar antes de un patrón
python3 codecraft.py before src/app.py "print" "# Preparando salida"

# Agregar al final del archivo
python3 codecraft.py append src/app.py "print('Fin del programa')"

# Eliminar líneas que contengan un patrón
python3 codecraft.py delete src/app.py "# Comentario"
```

### Operaciones Quirúrgicas Avanzadas

```bash
# Extraer método (refactoring)
python3 codecraft.py extract-method src/app.py 10 20 "procesar_datos"

# Extraer clase
python3 codecraft.py extract-class src/app.py "class Usuario" "Usuario"

# Renombrar símbolo
python3 codecraft.py rename-symbol src/app.py "variable_vieja" "variable_nueva"
```

## 🔍 Análisis de Código

### Análisis de Complejidad

```bash
# Análisis básico
python3 codecraft.py analyze-complexity src/

# Análisis detallado
python3 codecraft.py analyze-complexity src/ --format=detailed

# Salida JSON para IA
python3 codecraft.py analyze-complexity src/ --output-format=json
```

### Análisis de Dependencias

```bash
# Encontrar dependencias de un archivo
python3 codecraft.py find-dependencies src/app.py

# Incluir dependencias indirectas
python3 codecraft.py find-dependencies src/app.py --include-indirect
```

### Escaneo de Seguridad

```bash
# Escaneo básico
python3 codecraft.py security-scan .

# Escaneo de alta severidad
python3 codecraft.py security-scan . --severity=high

# Escaneo completo con salida JSON
python3 codecraft.py security-scan . --severity=low --output-format=json
```

### Salud del Proyecto

```bash
# Análisis completo de salud
python3 codecraft.py project-health .

# Con salida estructurada para IA
python3 codecraft.py project-health . --output-format=json
```

## 🤖 Generación de Código

### Componentes

```bash
# Componente React
python3 codecraft.py generate-component react UserProfile --framework=react

# Componente Vue
python3 codecraft.py generate-component vue ProductCard

# Componente Angular
python3 codecraft.py generate-component angular DataTable --framework=angular
```

### Tests Automáticos

```bash
# Tests para Python
python3 codecraft.py generate-tests src/app.py --test-framework=pytest

# Tests para JavaScript
python3 codecraft.py generate-tests src/utils.js --test-framework=jest

# Tests con cobertura específica
python3 codecraft.py generate-tests src/app.py --coverage=90
```

### Scaffolding de Proyectos

```bash
# Proyecto web
python3 codecraft.py scaffold-project web mi-app-web

# API REST
python3 codecraft.py scaffold-project api mi-api --template=fastapi

# Proyecto completo
python3 codecraft.py scaffold-project web mi-proyecto --template=react
```

## 🔄 Refactoring Inteligente

```bash
# Modernizar sintaxis
python3 codecraft.py modernize-syntax src/ --target-version=ES2023

# Optimizar imports
python3 codecraft.py optimize-imports src/ --remove-unused

# Aplicar patrones de diseño
python3 codecraft.py apply-patterns src/ --pattern=factory
```

## 🐛 Debugging y Depuración

```bash
# Encontrar bugs potenciales
python3 codecraft.py find-bugs src/app.py --severity=high

# Diagnosticar errores desde logs
python3 codecraft.py diagnose-error error.log --context=src/

# Sugerir correcciones
python3 codecraft.py suggest-fixes src/app.py "TypeError en línea 42"
```

## ⚡ Optimización de Performance

```bash
# Optimizar para velocidad
python3 codecraft.py optimize-performance src/ --target=speed

# Optimizar para memoria
python3 codecraft.py optimize-performance src/ --target=memory

# Análisis de bundle
python3 codecraft.py bundle-analysis . --bundler=webpack
```

## 🎛️ Opciones Globales

### Formatos de Salida

```bash
# Salida estructurada (por defecto)
python3 codecraft.py [comando] --output-format=structured

# Salida JSON para IA
python3 codecraft.py [comando] --output-format=json

# Salida de texto plano
python3 codecraft.py [comando] --output-format=text
```

### Modo Verbose

```bash
# Información detallada
python3 codecraft.py [comando] --verbose

# Análisis completo con diferencias
python3 codecraft.py replace src/app.py "old" "new" --verbose
```

### Configuración

```bash
# Usar archivo de configuración personalizado
python3 codecraft.py [comando] --config=/ruta/a/.codecraft.toml

# Directorio de plugins personalizado
python3 codecraft.py [comando] --plugin-dir=/ruta/a/plugins
```

## 🤖 Integración con IA

### Flujo Colaborativo IA-Humano

1. **IA analiza** la tarea y genera comando CodeCraft
2. **Humano ejecuta** el comando en terminal
3. **CodeCraft retorna** JSON estructurado con resultados
4. **IA interpreta** resultados y sugiere próximos pasos
5. **El ciclo continúa** hasta completar la tarea

### Ejemplo de Salida JSON para IA

```json
{
  "operation": "replace",
  "status": "success",
  "timestamp": "2024-01-15T10:30:00Z",
  "message": "Content replaced successfully",
  "data": {
    "file_path": "src/app.py",
    "lines_modified": 3,
    "backup_created": ".codecraft_backups/app.py.20240115_103000.backup"
  },
  "context": {
    "file_type": "python",
    "complexity_score": 12.5,
    "dependencies": ["os", "sys", "json"]
  },
  "next_suggestions": [
    "codecraft generate-tests src/app.py --test-framework=pytest",
    "codecraft analyze-complexity src/app.py"
  ]
}
```

## 📁 Estructura de Archivos Generados

```
proyecto/
├── .codecraft_backups/          # Backups automáticos
├── src/
│   ├── components/             # Componentes generados
│   ├── tests/                  # Tests generados
│   └── ...
├── .codecraft.toml            # Configuración (opcional)
└── .codecraft.log             # Log de operaciones
```

## 🛡️ Sistema de Backups

CodeCraft Ultimate incluye un sistema inteligente de backups:

- **Backup automático** antes de cada modificación
- **Restauración automática** en caso de error
- **Limpieza automática** de backups exitosos
- **Conservación** de backups de errores para investigación

## 🔌 Sistema de Plugins

### Plugins Incorporados

```bash
# Listar plugins disponibles
python3 codecraft.py --list-plugins

# Usar plugin específico de React
python3 codecraft.py react create-hook useCustomHook src/hooks/
```

### Crear Plugin Personalizado

```python
from codecraft_ultimate.core.plugin_system import BasePlugin

class MiPlugin(BasePlugin):
    @property
    def name(self):
        return "Mi Plugin Personalizado"
    
    def execute(self, operation, context, **kwargs):
        # Lógica del plugin
        return {"success": True}
```

## 📊 Métricas y Reportes

CodeCraft Ultimate proporciona métricas detalladas:

- **Complejidad ciclomática y cognitiva**
- **Líneas de código y funciones**
- **Dependencias y acoplamiento**
- **Puntuación de salud del proyecto (0-100)**
- **Vulnerabilidades de seguridad**
- **Sugerencias de mejora**

## 🚨 Resolución de Problemas

### Errores Comunes

1. **"Pattern not found"**
   - Verificar que el patrón existe exactamente en el archivo
   - Usar `--verbose` para ver sugerencias

2. **"File not found"**
   - Verificar rutas relativas al directorio del proyecto
   - Usar rutas absolutas si es necesario

3. **"Circular import"**
   - Revisar estructura de imports en el proyecto
   - Usar `codecraft find-dependencies` para análisis

### Comandos de Diagnóstico

```bash
# Verificar instalación
python3 codecraft.py --version

# Diagnóstico completo
python3 codecraft.py project-health . --verbose

# Log de operaciones
tail -f .codecraft.log
```

## 📞 Soporte

- **Documentación completa**: `/docs/`
- **Ejemplos prácticos**: `/examples/`
- **Tests unitarios**: `/tests/`
- **Código fuente**: Completamente documentado y modular

## 🎯 Casos de Uso Reales

### 1. Refactoring Seguro
```bash
# Crear backup y extraer método
python3 codecraft.py extract-method src/large_function.py 50 100 "process_user_data"

# Verificar que todo funciona
python3 codecraft.py analyze-complexity src/large_function.py
```

### 2. Desarrollo TDD
```bash
# Generar tests primero
python3 codecraft.py generate-tests src/new_feature.py --test-framework=pytest

# Implementar funcionalidad
python3 codecraft.py create src/new_feature.py "class NewFeature: pass"
```

### 3. Análisis de Código Legacy
```bash
# Análisis completo
python3 codecraft.py project-health legacy_code/ --output-format=json

# Escaneo de seguridad
python3 codecraft.py security-scan legacy_code/ --severity=high

# Sugerencias de modernización
python3 codecraft.py modernize-syntax legacy_code/ --target-version=Python3.11
```

---

## 🚀 **¡CodeCraft Ultimate v6.0 está listo para usar!**

**Comando de inicio rápido:**
```bash
python3 codecraft.py project-health . --output-format=json
```

Este manual cubre todas las funcionalidades disponibles. Para casos específicos, consulta los ejemplos en `/examples/` o la documentación detallada en `/docs/`.