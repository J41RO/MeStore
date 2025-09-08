# Arquitectura del Sistema - Surgical Modifier

## Visión General

Surgical Modifier implementa una arquitectura modular basada en el patrón Coordinator-Function para máxima flexibilidad y reutilización.

## Estructura Principal
surgical_modifier/
├── coordinators/          # Orquestadores ligeros (150-200 líneas)
│   ├── create.py         # Coordinador de creación
│   ├── replace.py        # Coordinador de reemplazos
│   ├── before.py         # Coordinador inserción anterior
│   ├── after.py          # Coordinador inserción posterior
│   ├── append.py         # Coordinador de adición
│   ├── update.py         # Coordinador multi-operaciones
│   ├── delete.py         # Coordinador de eliminación
│   └── explore.py        # Coordinador de análisis
│
├── functions/            # Funciones modulares reutilizables
│   ├── backup/           # Sistema de backup y rollback
│   ├── content/          # Procesamiento de contenido
│   ├── pattern/          # Matching de patrones
│   ├── insertion/        # Lógica de inserción
│   ├── validation/       # Validaciones
│   └── formatting/       # Formateo por lenguaje
│
├── utils/                # Utilidades de soporte
├── cli.py                # Interface de línea de comandos
└── main.py               # Entry point principal

## Principios de Diseño

### 1. Coordinadores Ligeros
- Solo orquestan operaciones, no implementan lógica de negocio
- Máximo 150-200 líneas por coordinador
- Responsabilidad única y bien definida
- Fácil testing y mantenimiento

### 2. Functions Modulares
- Funcionalidades específicas y reutilizables
- Testeable independientemente
- Sin dependencias entre functions
- Interface consistente

### 3. Separación de Responsabilidades
- CLI maneja interface y routing
- Coordinadores orquestan flujos
- Functions implementan lógica específica
- Utils proporcionan soporte común

## Flujo de Ejecución

1. **CLI** recibe comando y parámetros
2. **Router** determina coordinador apropiado
3. **Coordinador** orquesta sequence de functions
4. **Functions** ejecutan operaciones específicas
5. **Validation** verifica resultados
6. **Backup** maneja rollback si es necesario

## Extensibilidad

### Agregar Nuevo Coordinador
1. Crear archivo en `coordinators/`
2. Implementar interface estándar
3. Registrar en CLI router
4. Agregar tests correspondientes

### Agregar Nueva Function
1. Crear en directorio `functions/` apropiado
2. Implementar interface consistente
3. Documentar parámetros y retorno
4. Agregar tests unitarios
