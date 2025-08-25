# Guía: Manejo de Template Literals en CLI v6.0

## Problema Resuelto
Bash interpreta `${}` antes de pasar contenido a Python, causando "bad substitution"

## Soluciones Disponibles

### 1. Usar Wrapper Script (RECOMENDADO)
```bash
./sm_wrapper.sh create component.tsx "" 'const msg = `Hello ${name}!`;'
2. Usar File Input
bashecho 'const html = `<div>${content}</div>`;' > content.js
python3 cli.py create component.js "" --file-input content.js
3. Usar Stdin
bashpython3 cli.py create component.js "" --stdin
# Pegar contenido y presionar Ctrl+D
4. Modo Raw (sin procesamiento)
bashpython3 cli.py create test.js "" 'contenido exacto' --raw
Ejemplos Comunes
React Component
bash./sm_wrapper.sh create Button.tsx "" 'interface Props { label: string; }

const Button = ({ label }: Props) => (
  <button className={`btn ${className}`}>
    {label}
  </button>
);'
Template Literal con Interpolación
bashecho 'const query = `SELECT * FROM users WHERE id = ${userId}`;' | python3 cli.py create query.js "" --stdin
JavaScript con Template Literals
bash./sm_wrapper.sh create utils.js "" 'const formatMessage = (name) => `Welcome ${name}!`;
const buildHTML = (content) => `<div class="container">${content}</div>`;'
Troubleshooting
Error: "bad substitution"

Usar wrapper script: ./sm_wrapper.sh en lugar de python3 cli.py
Usar --file-input para contenido complejo

Template literals no se preservan

Verificar que no uses --raw accidentalmente
El CLI automáticamente detecta archivos JS/TS/JSX/TSX

Contenido multilínea

Usar --stdin o --file-input
El wrapper maneja automáticamente contenido complejo
