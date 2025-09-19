# Convenciones de Naming - MeStore

## 📋 Backend (Python/FastAPI)

### Archivos y Módulos
- **Archivos Python**: snake_case
  - `user_model.py`
  - `auth_service.py`
  - `product_controller.py`

### Clases
- **Modelos**: PascalCase + Model suffix
  - `UserModel`
  - `ProductModel`
  - `OrderModel`

- **Servicios**: PascalCase + Service suffix
  - `AuthService`
  - `PaymentService`
  - `NotificationService`

- **Schemas**: PascalCase + Schema suffix
  - `UserCreateSchema`
  - `ProductResponseSchema`
  - `OrderUpdateSchema`

### Funciones y Variables
- **Funciones**: snake_case con verbo
  - `get_user_by_id()`
  - `create_product()`
  - `validate_payment()`

- **Variables**: snake_case descriptivo
  - `user_email`
  - `total_price`
  - `order_status`

### Constantes
- **Constantes**: UPPER_SNAKE_CASE
  - `MAX_FILE_SIZE`
  - `DEFAULT_PAGE_SIZE`
  - `JWT_EXPIRATION_TIME`

## 🎨 Frontend (React/TypeScript)

### Archivos y Componentes
- **Componentes React**: PascalCase
  - `UserCard.tsx`
  - `ProductList.tsx`
  - `NavigationHeader.tsx`

- **Páginas**: PascalCase + Page suffix
  - `HomePage.tsx`
  - `ProductPage.tsx`
  - `CheckoutPage.tsx`

- **Hooks**: camelCase con 'use' prefix
  - `useAuth.ts`
  - `useProducts.ts`
  - `useLocalStorage.ts`

- **Utils**: camelCase descriptivo
  - `formatPrice.ts`
  - `validateEmail.ts`
  - `apiClient.ts`

### Variables y Funciones
- **Variables**: camelCase
  - `userName`
  - `totalPrice`
  - `isLoading`

- **Funciones**: camelCase con verbo
  - `handleSubmit()`
  - `fetchUserData()`
  - `validateForm()`

### Interfaces y Types
- **Interfaces**: PascalCase + Interface suffix
  - `UserInterface`
  - `ProductInterface`
  - `ApiResponseInterface`

- **Types**: PascalCase + Type suffix
  - `UserType`
  - `ProductType`
  - `StatusType`

## 📁 Estructura de Carpetas

### Backend
```
app/
├── models/           # Modelos de datos
├── services/         # Lógica de negocio
├── api/             # Controladores API
│   └── v1/          # Versión específica
├── schemas/         # Validación Pydantic
├── agents/          # Lógica de agentes
├── fulfillment/     # Gestión de fulfillment
└── marketplace/     # Funcionalidad marketplace
```

### Frontend
```
src/
├── components/      # Componentes reutilizables
├── pages/          # Páginas principales
├── hooks/          # Custom hooks
├── utils/          # Utilidades
└── features/       # Funcionalidades específicas
    ├── agents/
    ├── fulfillment/
    └── marketplace/
```

## 🎯 Ejemplos Completos

### Backend Example
```python
# app/models/user.py
class UserModel(BaseModel):
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

# app/services/auth_service.py
class AuthService:
    def authenticate_user(self, email: str, password: str):
        return validated_user

# app/schemas/user.py
class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str
```

### Frontend Example
```typescript
// src/components/UserCard.tsx
interface UserCardProps {
  user: UserInterface;
  onEdit: (userId: string) => void;
}

export const UserCard: React.FC<UserCardProps> = ({ user, onEdit }) => {
  const handleEditClick = () => onEdit(user.id);

  return (
    <div className="user-card">
      {user.name}
    </div>
  );
};

// src/hooks/useAuth.ts
export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const login = async (email: string, password: string) => {
    // Logic here
  };

  return { isAuthenticated, login };
};
```

## ✅ Checklist de Cumplimiento

- [ ] Nombres de archivos siguen convención de su tipo
- [ ] Clases usan PascalCase apropiado
- [ ] Funciones usan snake_case (Python) / camelCase (TypeScript)
- [ ] Constantes usan UPPER_SNAKE_CASE
- [ ] Componentes React usan PascalCase
- [ ] Hooks usan 'use' prefix
- [ ] Interfaces/Types tienen suffix apropiado
- [ ] Estructura de carpetas es consistente
