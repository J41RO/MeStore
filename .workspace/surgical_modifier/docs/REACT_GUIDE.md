REACT + TYPESCRIPT - GUÍA COMPLETA
ESTADO: ✅ COMPLETO - FUNCIONAL
COORDINADOR PRINCIPAL:

ReactCoordinator: Para React + TypeScript
Ubicación: coordinators/react/react_coordinator.py
Activación: Automática para archivos .tsx y .jsx
Herencia: Todas las capacidades TypeScript incluidas

FUNCTIONS ESPECÍFICAS:

jsx_parser.py: Parsing y manipulación JSX segura
hook_manager.py: Gestión de hooks (useState, useEffect)
component_analyzer.py: Análisis de componentes
props_manager.py: Gestión automática de props/interfaces

COMANDOS CLI:
Funcionalidad completa para desarrollo React:
bash# Crear componente React
python cli.py create Button.tsx "import React from 'react';

interface ButtonProps {
  label: string;
  onClick: () => void;
}

const Button: React.FC<ButtonProps> = ({ label, onClick }) => {
  return <button onClick={onClick}>{label}</button>;
};

export default Button;"

# Agregar nuevas props
python cli.py after Button.tsx "onClick: () => void;" "disabled?: boolean;"

# Agregar hooks
python cli.py after Button.tsx "const Button: React.FC<ButtonProps> = ({ label, onClick }) => {" "  const [isPressed, setIsPressed] = useState(false);"

# Modificar JSX
python cli.py replace Button.tsx "<button" "<button className='btn'"
CARACTERÍSTICAS REACT:
JSX Parsing Seguro:

Análisis de estructura JSX
Modificación sin romper tags
Validación de sintaxis

Hook Management:

useState, useEffect automáticos
Custom hooks soportados
Inserción en posición correcta

Props e Interfaces:

Generación automática de interfaces Props
Actualización de destructuring
Tipado TypeScript completo

Component Analysis:

Detección de tipo de componente
Análisis de estructura
Optimizaciones sugeridas

CASOS DE USO AVANZADOS:
Componente con Estado:
bashpython cli.py create Counter.tsx "import React, { useState } from 'react';

const Counter: React.FC = () => {
  const [count, setCount] = useState<number>(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>+</button>
      <button onClick={() => setCount(count - 1)}>-</button>
    </div>
  );
};"
Agregar useEffect:
bashpython cli.py after Counter.tsx "const [count, setCount] = useState<number>(0);" "
  useEffect(() => {
    document.title = \`Count: \${count}\`;
  }, [count]);"
PATRONES SOPORTADOS:
Functional Components:

Arrow functions
Function declarations
React.FC typing

Hooks Patterns:

Estado local
Efectos secundarios
Custom hooks

Props Patterns:

Interface definitions
Optional props
Default values

TROUBLESHOOTING:
JSX Syntax Errors:

Verificar tags balanceados
Comprobar expresiones válidas
Validar imports React

Hook Rules:

Hooks al inicio del componente
No hooks en condicionales
Dependencias correctas en useEffect
