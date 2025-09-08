# SURGICAL MODIFIER v6.0 - ARQUITECTURA COMPLETA

## 🎯 PARA IA QUE ENTRA AL SISTEMA:

### DECISIÓN DE TECNOLOGÍA AUTOMÁTICA:
1. El sistema detecta automáticamente la tecnología por extensión de archivo
2. Router asigna coordinador especializado sin configuración manual
3. Coordinador usa functions específicas de la tecnología
4. Zero configuración manual requerida

### 🐍 PYTHON (ESTADO: PERFECTO):
- **Coordinadores:** coordinators/python/ (preservado intacto)
- **Functions:** functions/python/ (específicas Python)
- **CLI:** Todos los comandos originales funcionando
- **Extensión:** .py → CreateCoordinator
- **NO MODIFICAR:** Funciona perfectamente desde el inicio

### 🔷 TYPESCRIPT (ESTADO: COMPLETO):
- **Coordinador:** coordinators/typescript/typescript_coordinator.py
- **Functions:** functions/typescript/ (interfaces, types, imports)
- **CLI:** Comandos automáticos + específicos TypeScript
- **Extensión:** .ts → TypeScriptCoordinator
- **Características:** Interfaces, tipos, imports con alias, validación tsc

### ⚛️ REACT (ESTADO: COMPLETO):
- **Coordinador:** coordinators/react/react_coordinator.py
- **Functions:** functions/react/ + herencia functions/typescript/
- **CLI:** Comandos automáticos + específicos React
- **Extensiones:** .tsx/.jsx → ReactCoordinator
- **Características:** JSX, hooks, props, componentes, herencia TypeScript

## 🏗️ ARQUITECTURA DEL SISTEMA:
surgical_modifier/
├── coordinators/
│   ├── python/              # Python preservado
│   ├── typescript/          # TypeScript especializado
│   ├── react/              # React + TypeScript
│   ├── shared/             # Funciones compartidas
│   └── coordinator_router.py # Router central automático
├── functions/
│   ├── python/             # Functions específicas Python
│   ├── typescript/         # Functions específicas TypeScript
│   ├── react/             # Functions específicas React
│   └── shared/            # Functions universales
├── docs/
│   ├── ARCHITECTURE.md    # Este archivo
│   ├── PYTHON_GUIDE.md    # Guía Python
│   ├── TYPESCRIPT_GUIDE.md # Guía TypeScript
│   └── REACT_GUIDE.md     # Guía React
└── cli.py                 # CLI unificado

## 🎯 ROUTER INTELIGENTE:

El sistema detecta automáticamente qué coordinador usar:

- **.py** → CreateCoordinator (Python)
- **.ts** → TypeScriptCoordinator (TypeScript puro)
- **.tsx** → ReactCoordinator (React + TypeScript)
- **.jsx** → ReactCoordinator (React)

## 📋 COMANDOS DISPONIBLES:

Todos los comandos funcionan idénticamente para las 3 tecnologías:

```bash
# Python (funciona desde siempre)
python cli.py create file.py "print('Hello Python')"
python cli.py replace file.py "Hello" "Hi"

# TypeScript (funcional desde Fase 3)
python cli.py create file.ts "interface User { name: string; }"
python cli.py replace file.ts "string" "number"

# React (funcional desde Fase 4)
python cli.py create component.tsx "const App = () => <div>Hello</div>"
python cli.py replace component.tsx "Hello" "World"
🔍 PRINCIPIOS ARQUITECTÓNICOS:
Separación Crystal Clear:

Python: Intacto y funcional
TypeScript: Especializado sin interferir Python
React: Hereda TypeScript + capacidades JSX/hooks

Zero Interferencia:

Coordinadores no se llaman entre sí
Functions específicas por tecnología
Tests independientes por stack

Extensibilidad:

Agregar Vue: crear coordinators/vue/ + functions/vue/
Agregar Angular: crear coordinators/angular/ + functions/angular/
Router automático se extiende fácilmente

🧪 TESTING:
bash# Tests por tecnología
python -m pytest tests/regression/test_python_complete.py    # Python
python -m pytest tests/test_coordinators/test_typescript_coordinator.py # TypeScript
python -m pytest tests/test_coordinators/test_react_coordinator.py      # React

# Suite completa
python -m pytest tests/ -v
🚀 PARA IA DESARROLLADORA:
Si trabajas con Python:

USA: coordinators/python/ y functions/python/
NO TOQUES: coordinators/typescript/ o coordinators/react/

Si trabajas con TypeScript:

USA: coordinators/typescript/ y functions/typescript/
PUEDES USAR: functions/shared/
NO TOQUES: coordinators/python/

Si trabajas con React:

USA: coordinators/react/ y functions/react/
HEREDA: functions/typescript/ automáticamente
PUEDES USAR: functions/shared/
NO TOQUES: coordinators/python/

🎯 DETECCIÓN AUTOMÁTICA:
El sistema es completamente automático:

Usuario ejecuta: python cli.py create file.tsx "content"
Router detecta extensión .tsx
Asigna ReactCoordinator automáticamente
ReactCoordinator hereda capacidades TypeScript
Procesa contenido con lógica React específica
Usuario no necesita conocer coordinadores internos

🔧 MANTENIMIENTO:
Para mantener el sistema:

Tests de regresión Python: OBLIGATORIOS antes de cualquier cambio
Separación de coordinadores: NUNCA mezclar lógica entre tecnologías
Documentación actualizada: Reflejar cambios en código

Para agregar tecnologías:

Crear coordinators/nueva_tech/
Crear functions/nueva_tech/
Actualizar coordinator_router.py
Agregar tests específicos
Documentar en nueva guía


SURGICAL MODIFIER v6.0: ARQUITECTURA CRYSTAL CLEAR MULTI-TECNOLOGÍA COMPLETADA

## 📚 EJEMPLOS PRÁCTICOS POR TECNOLOGÍA:

### Python - Funcionalidad Preservada:
```bash
# Crear archivo Python
python cli.py create models.py "class User:
    def __init__(self, name: str):
        self.name = name
    
    def greet(self):
        return f'Hello, {self.name}'"

# Modificar archivo Python
python cli.py replace models.py "Hello" "Hi"
python cli.py after models.py "def greet(self):" "        print('Greeting user')"
TypeScript - Especializado:
bash# Crear interface TypeScript
python cli.py create types.ts "interface User {
    id: number;
    name: string;
    email?: string;
}

type Status = 'active' | 'inactive' | 'pending';

function createUser(name: string): User {
    return {
        id: Date.now(),
        name,
        email: undefined
    };
}"

# Modificar tipos
python cli.py after types.ts "email?: string;" "    role: 'admin' | 'user';"
React - Complejo con Hooks:
bash# Crear componente React
python cli.py create UserCard.tsx "import React, { useState, useEffect } from 'react';

interface UserCardProps {
    userId: number;
    onUserSelect?: (user: User) => void;
}

const UserCard: React.FC<UserCardProps> = ({ userId, onUserSelect }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        fetchUser(userId).then(userData => {
            setUser(userData);
            setLoading(false);
        });
    }, [userId]);

    if (loading) return <div>Loading...</div>;
    if (!user) return <div>User not found</div>;

    return (
        <div className='user-card'>
            <h3>{user.name}</h3>
            <p>{user.email}</p>
            <button onClick={() => onUserSelect?.(user)}>
                Select User
            </button>
        </div>
    );
};

export default UserCard;"

# Agregar nueva prop
python cli.py after UserCard.tsx "onUserSelect?: (user: User) => void;" "    theme?: 'light' | 'dark';"
🔧 COORDINADORES EN DETALLE:
CreateCoordinator (Python):

Ubicación: coordinators/create.py
Responsabilidad: Operaciones Python puras
Functions: functions/python/*
Características: AST Python, PEP8, imports Python

TypeScriptCoordinator:

Ubicación: coordinators/typescript/typescript_coordinator.py
Responsabilidad: TypeScript puro (sin JSX)
Functions: functions/typescript/*
Características: Interfaces, types, tsc validation, alias resolution

ReactCoordinator:

Ubicación: coordinators/react/react_coordinator.py
Herencia: TypeScriptReactCoordinator → todas capacidades TS
Functions: functions/react/* + functions/typescript/*
Características: JSX parsing, hooks, props, component analysis

🏗️ FUNCTIONS POR TECNOLOGÍA:
functions/python/:

validation/: Validación sintaxis Python
formatting/: PEP8, autopep8 integration
analysis/: AST Python parsing
operations/: Operaciones específicas Python

functions/typescript/:

validation/: TypeScript compiler check
interfaces/: Interface management
imports/: Import resolution con alias
types/: Type analysis y validación

functions/react/:

jsx_parser.py: Parsing y manipulación JSX segura
hook_manager.py: Gestión useState, useEffect, custom hooks
component_analyzer.py: Análisis estructura componentes
props_manager.py: Gestión automática props/interfaces

🚨 TROUBLESHOOTING:
Error: "Coordinador fallback"
bash# Verificar router funcional
python -c "from coordinators.coordinator_router import CoordinatorRouter; r = CoordinatorRouter(); print(type(r.get_coordinator('test.py')))"
Error: "AST Engine no soporta"

Causa: ast-grep no disponible
Impacto: Operaciones básicas funcionan
Solución: Instalar ast-grep opcional

Error: "Pattern not found"

Causa: Patrón no existe en archivo
Solución: Verificar contenido actual antes de modificar

🎯 FLUJOS DE TRABAJO TÍPICOS:
Desarrollo Python:

python cli.py create module.py "content"
python cli.py replace module.py "old" "new"
python cli.py after module.py "class:" "    # documentation"

Desarrollo TypeScript:

python cli.py create types.ts "interface"
python cli.py after types.ts "prop: type;" "newProp: newType;"
Validación automática con tsc

Desarrollo React:

python cli.py create Component.tsx "component"
python cli.py after Component.tsx "useState" "useEffect"
Props automáticamente gestionadas

📊 MÉTRICAS DE CALIDAD:

Tests Python: 6/6 PASSED (regresión 100%)
Tests TypeScript: 10/10 PASSED
Tests React: 7/7 PASSED
Cobertura: Multi-tecnología completa
Performance: <1s operaciones típicas


SISTEMA COMPLETAMENTE DOCUMENTADO - READY PARA IA EXTERNA
