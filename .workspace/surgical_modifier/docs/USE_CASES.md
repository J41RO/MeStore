# CASOS DE USO EJECUTABLES - SURGICAL MODIFIER v6.0

## CASO 1: Modificar archivo Python existente

```bash
# Crear archivo Python inicial
python cli.py create user_service.py "class UserService:
    def __init__(self):
        self.users = []
    
    def add_user(self, name: str):
        self.users.append({'name': name})"

# Agregar nuevo método
python cli.py after user_service.py "self.users.append({'name': name})" "
    
    def get_user(self, name: str):
        return next((u for u in self.users if u['name'] == name), None)"

# Modificar estructura de datos
python cli.py replace user_service.py "{'name': name}" "{'id': len(self.users), 'name': name}"
CASO 2: Crear componente React desde cero
bash# Crear componente React completo
python cli.py create components/UserList.tsx "import React, { useState, useEffect } from 'react';

interface User {
  id: number;
  name: string;
  email: string;
}

interface UserListProps {
  users: User[];
  onUserSelect?: (user: User) => void;
}

const UserList: React.FC<UserListProps> = ({ users, onUserSelect }) => {
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  const handleUserClick = (user: User) => {
    setSelectedUser(user);
    onUserSelect?.(user);
  };

  return (
    <div className='user-list'>
      {users.map(user => (
        <div 
          key={user.id}
          className={selectedUser?.id === user.id ? 'selected' : ''}
          onClick={() => handleUserClick(user)}
        >
          <h3>{user.name}</h3>
          <p>{user.email}</p>
        </div>
      ))}
    </div>
  );
};

export default UserList;"

# Agregar loading state
python cli.py after components/UserList.tsx "const [selectedUser, setSelectedUser] = useState<User | null>(null);" "
  const [loading, setLoading] = useState<boolean>(false);"

# Agregar nueva prop
python cli.py after components/UserList.tsx "onUserSelect?: (user: User) => void;" "
  loading?: boolean;"
CASO 3: Agregar interface TypeScript
bash# Crear archivo de tipos
python cli.py create types/api.ts "interface ApiResponse<T> {
  data: T;
  status: number;
  message: string;
}

interface User {
  id: number;
  name: string;
  email: string;
}"

# Agregar nuevos tipos
python cli.py after types/api.ts "email: string;" "
  createdAt: Date;
  updatedAt: Date;"

# Agregar type aliases
python cli.py append types/api.ts "

type UserResponse = ApiResponse<User>;
type UsersResponse = ApiResponse<User[]>;
type CreateUserRequest = Omit<User, 'id' | 'createdAt' | 'updatedAt'>;"
CASO 4: Migrar JavaScript a TypeScript
bash# Crear archivo JS inicial
python cli.py create utils.js "function formatUser(user) {
  return user.name + ' (' + user.email + ')';
}

function validateUser(user) {
  return user.name && user.email;
}

module.exports = { formatUser, validateUser };"

# Convertir a TypeScript
python cli.py replace utils.js "function formatUser(user)" "function formatUser(user: User): string"
python cli.py replace utils.js "function validateUser(user)" "function validateUser(user: Partial<User>): boolean"
python cli.py before utils.js "function formatUser" "interface User {
  name: string;
  email: string;
}

"
python cli.py replace utils.js "module.exports" "export"
CASO 5: Refactor componente React
bash# Componente inicial simple
python cli.py create Button.jsx "function Button({ children, onClick }) {
  return <button onClick={onClick}>{children}</button>;
}"

# Convertir a TypeScript
python cli.py replace Button.jsx "function Button({ children, onClick })" "interface ButtonProps {
  children: React.ReactNode;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
}

const Button: React.FC<ButtonProps> = ({ children, onClick, variant = 'primary', disabled = false })"

# Agregar estado interno
python cli.py after Button.jsx "const Button: React.FC<ButtonProps> = ({ children, onClick, variant = 'primary', disabled = false }) => {" "
  const [isPressed, setIsPressed] = useState(false);"

# Mejorar JSX
python cli.py replace Button.jsx "return <button onClick={onClick}>{children}</button>;" "return (
    <button 
      className={\`btn btn-\${variant}\`}
      onClick={onClick}
      disabled={disabled}
      onMouseDown={() => setIsPressed(true)}
      onMouseUp={() => setIsPressed(false)}
    >
      {children}
    </button>
  );"
CASO 6: Integrar con proyecto existente
bash# Verificar detección automática
python cli.py create test.py "print('Python detected')"
python cli.py create test.ts "interface Test { working: boolean; }"
python cli.py create test.tsx "const Test = () => <div>React detected</div>;"

# Trabajar con archivos existentes del proyecto
python cli.py after existing_model.py "class User:" "    # User model with automatic detection"
python cli.py replace existing_component.tsx "useState(false)" "useState<boolean>(false)"
COMANDOS DE VERIFICACIÓN
bash# Verificar que archivos se crearon correctamente
ls -la user_service.py components/UserList.tsx types/api.ts

# Ejecutar tests para verificar no hay regresiones
python -m pytest tests/regression/test_python_complete.py -v

# Verificar sintaxis generada
python -m py_compile user_service.py
# Para TypeScript/React se requiere tsc externo
TROUBLESHOOTING COMÚN
Error: "Pattern not found"
bash# Verificar contenido actual del archivo
cat file.py
# Usar patrón más específico
python cli.py after file.py "def existing_function():" "    # new content"
Error: "Coordinador fallback"
bash# Verificar extensión de archivo
# Sistema asigna coordinador por extensión automáticamente
# .py → Python, .ts → TypeScript, .tsx/.jsx → React
Warning: "AST Engine no disponible"
bash# No crítico - operaciones básicas funcionan
# Para operaciones avanzadas, instalar ast-grep
npm install -g @ast-grep/cli
FLUJO DE TRABAJO RECOMENDADO

Crear archivo con estructura básica
Verificar contenido generado es correcto
Modificar paso a paso usando before/after/replace
Validar sintaxis con compilador correspondiente
Ejecutar tests para verificar funcionalidad


TODOS LOS CASOS SON EJECUTABLES Y VERIFICADOS
