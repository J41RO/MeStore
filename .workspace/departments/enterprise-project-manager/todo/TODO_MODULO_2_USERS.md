# 👥 TODO MÓDULO 2: USER MANAGEMENT ADVANCED

**Base Compatible**: TODO_CONFIGURACION_BASE_ENTERPRISE.md ✅
**Dependencias**: Database Architecture ✅, Auth System ✅, RBAC ✅
**Tiempo Estimado**: 18 horas (10h backend + 8h frontend)
**Prioridad**: 🔴 CRÍTICA - Core Foundation Module

---

## 🎯 OBJETIVO DEL MÓDULO
Crear el sistema avanzado de gestión de usuarios donde el SUPERUSUARIO tiene control absoluto sobre todos los usuarios, con analytics comportamental, gestión de permisos granulares y preparación para agentes IA.

---

## 🗄️ BACKEND - DATABASE & MODELS (5 horas)

### 2.1 Extender Modelo User Enterprise (2h)
**Compatible con**: User model existente ✅, Auth system ✅

```python
# app/models/user.py - EXTENDER MODELO EXISTENTE
class User(BaseModel):
    # CAMPOS EXISTENTES (mantener compatibilidad)
    id: int
    email: str = Field(unique=True)
    password_hash: str
    user_type: UserType
    created_at: datetime
    updated_at: datetime

    # NUEVOS CAMPOS ENTERPRISE
    # Información Personal Colombia
    cedula: str = Field(unique=True, nullable=True)
    nombres: str
    apellidos: str
    fecha_nacimiento: date = Field(nullable=True)
    genero: GenderType = Field(nullable=True)  # masculino, femenino, otro
    estado_civil: MaritalStatus = Field(nullable=True)

    # Contacto y Ubicación
    telefono_movil: str = Field(nullable=True)
    telefono_fijo: str = Field(nullable=True)
    departamento: str = Field(nullable=True)  # Departamento Colombia
    ciudad: str = Field(nullable=True)
    direccion_completa: text = Field(nullable=True)
    codigo_postal: str = Field(nullable=True)

    # Control Empresarial
    created_by: FK to User = Field(nullable=True)  # SUPERUSER puede crear usuarios
    supervised_by: FK to User = Field(nullable=True)  # Para agentes IA → SUPERUSER
    ai_assistant_id: FK to User = Field(nullable=True)  # IA asignada (futuro)
    department: str = Field(nullable=True)  # área de responsabilidad
    position: str = Field(nullable=True)  # cargo en la empresa

    # Performance y Analytics
    performance_score: decimal = Field(default=0.0, ge=0, le=100)
    last_activity: datetime = Field(nullable=True)
    activity_streak: int = Field(default=0)  # días activos consecutivos
    login_count: int = Field(default=0)
    failed_login_attempts: int = Field(default=0)
    last_failed_login: datetime = Field(nullable=True)

    # Estado y Control
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    is_suspended: bool = Field(default=False)
    suspension_reason: text = Field(nullable=True)
    suspended_until: datetime = Field(nullable=True)
    suspended_by: FK to User = Field(nullable=True)

    # Configuraciones
    timezone: str = Field(default="America/Bogota")
    language: str = Field(default="es")
    notification_preferences: JSON = Field(default=dict)
    ui_preferences: JSON = Field(default=dict)
    privacy_settings: JSON = Field(default=dict)

    # Metadata
    metadata: JSON = Field(default=dict)  # Configuraciones personalizadas
    tags: JSON = Field(default=list)  # Etiquetas para categorización
```

**Dependencias**: Existing User model ✅
**Specialist**: @backend-senior-developer

### 2.2 Crear UserPermissions Granular (1.5h)
**Propósito**: Sistema de permisos granulares por área de negocio

```python
# app/models/user_permission.py - NUEVO MODELO
class Permission(BaseModel):
    id: int = Field(primary_key=True)
    name: str = Field(unique=True)  # 'buyer.view_all'
    description: str
    category: PermissionCategory  # COMPRADORES, VENDEDORES, ADMINISTRADORES, SISTEMA
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserPermission(BaseModel):
    id: int = Field(primary_key=True)
    user_id: FK to User
    permission_id: FK to Permission
    granted_by: FK to User  # Quién otorgó el permiso
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(nullable=True)  # Permisos temporales
    is_active: bool = Field(default=True)

    # Constraints específicos
    resource_constraints: JSON = Field(default=dict)  # {"vendor_id": [1,2,3]}
    time_constraints: JSON = Field(default=dict)  # {"days": ["mon","tue"]}

class RolePermissionTemplate(BaseModel):
    """Templates de permisos por rol para fácil asignación"""
    id: int = Field(primary_key=True)
    role: UserType
    permissions: JSON  # Lista de permission names
    created_by: FK to User
    is_default: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Dependencias**: User model ✅
**Specialist**: @backend-senior-developer

### 2.3 Crear UserActivity y Analytics (1h)
**Propósito**: Tracking completo de actividad para analytics

```python
# app/models/user_activity.py - NUEVO MODELO
class UserActivity(BaseModel):
    id: int = Field(primary_key=True)
    user_id: FK to User
    activity_type: ActivityType  # login, logout, page_view, action_performed
    activity_details: JSON  # Detalles específicos de la actividad
    ip_address: str
    user_agent: text
    session_id: str = Field(nullable=True)
    duration_seconds: int = Field(nullable=True)  # Para page_views
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserMetrics(BaseModel):
    """Métricas calculadas por usuario para performance"""
    id: int = Field(primary_key=True)
    user_id: FK to User
    metric_type: MetricType  # login_frequency, task_completion, performance_score
    metric_value: decimal
    calculation_period: str  # daily, weekly, monthly
    period_start: date
    period_end: date
    calculated_at: datetime = Field(default_factory=datetime.utcnow)

class UserSession(BaseModel):
    """Control de sesiones concurrentes"""
    id: str = Field(primary_key=True)  # session_id
    user_id: FK to User
    ip_address: str
    user_agent: text
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    ended_at: datetime = Field(nullable=True)
```

**Dependencias**: User model ✅
**Specialist**: @backend-senior-developer

### 2.4 Sistema de Notificaciones Usuario (0.5h)
**Propósito**: Preferencias y gestión de notificaciones

```python
# app/models/user_notification.py - NUEVO MODELO
class UserNotification(BaseModel):
    id: int = Field(primary_key=True)
    user_id: FK to User
    notification_type: NotificationType  # email, sms, push, in_app
    title: str
    message: text
    data: JSON = Field(default=dict)  # Datos adicionales
    is_read: bool = Field(default=False)
    read_at: datetime = Field(nullable=True)
    sent_at: datetime = Field(nullable=True)
    delivery_status: DeliveryStatus = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class NotificationPreference(BaseModel):
    id: int = Field(primary_key=True)
    user_id: FK to User
    notification_category: str  # orders, products, system, marketing
    email_enabled: bool = Field(default=True)
    sms_enabled: bool = Field(default=False)
    push_enabled: bool = Field(default=True)
    in_app_enabled: bool = Field(default=True)
    frequency: FrequencyType = Field(default="immediate")  # immediate, daily, weekly
```

**Dependencias**: User model ✅
**Specialist**: @backend-senior-developer

---

## 🔌 BACKEND - SERVICES & APIS (5 horas)

### 2.5 UserManagement Service Enterprise (2h)
**Propósito**: Servicios completos de gestión de usuarios

```python
# app/services/user_management_service.py - NUEVO SERVICIO
class UserManagementService:

    def create_user_enterprise(
        self,
        user_data: dict,
        created_by: User,
        assign_permissions: List[str] = None
    ) -> User:
        """SUPERUSER puede crear cualquier tipo de usuario"""
        if not created_by.user_type == UserType.SUPERUSER:
            raise PermissionDenied("Only SUPERUSER can create users")

        # Crear usuario con todos los campos enterprise
        user = User(**user_data, created_by=created_by.id)
        db.add(user)
        db.commit()

        # Asignar permisos si se especifican
        if assign_permissions:
            self.assign_permissions(user.id, assign_permissions, created_by)

        # Log de auditoría
        self.log_user_action(created_by, "create_user", user.id)

        return user

    def get_users_for_role(self, requesting_user: User, role: UserType = None):
        """Control de acceso basado en rol del solicitante"""
        if requesting_user.user_type == UserType.SUPERUSER:
            # SUPERUSER ve todos los usuarios
            query = db.query(User)
            if role:
                query = query.filter(User.user_type == role)
            return query.all()

        elif requesting_user.user_type.startswith("ADMIN_"):
            # Admins ven usuarios de su área
            return self.get_users_by_department(requesting_user.department)

        else:
            # Vendors/Buyers solo se ven a sí mismos
            return [requesting_user]

    def suspend_user(
        self,
        user_id: int,
        suspended_by: User,
        reason: str,
        duration_days: int = None
    ):
        """Sistema de suspensión con auditoría"""
        if not self.can_suspend_user(suspended_by, user_id):
            raise PermissionDenied("Cannot suspend this user")

        user = db.query(User).filter(User.id == user_id).first()
        user.is_suspended = True
        user.suspension_reason = reason
        user.suspended_by = suspended_by.id

        if duration_days:
            user.suspended_until = datetime.utcnow() + timedelta(days=duration_days)

        # Invalidar sesiones activas
        self.invalidate_user_sessions(user_id)

        # Notificación al usuario
        self.send_suspension_notification(user_id, reason)

        db.commit()

    def bulk_update_users(
        self,
        user_ids: List[int],
        updates: dict,
        updated_by: User
    ):
        """SUPERUSER puede hacer bulk updates"""
        if updated_by.user_type != UserType.SUPERUSER:
            raise PermissionDenied("Only SUPERUSER can bulk update users")

        users = db.query(User).filter(User.id.in_(user_ids)).all()

        for user in users:
            for key, value in updates.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            user.updated_at = datetime.utcnow()

        db.commit()

        return {"updated_count": len(users)}
```

**Dependencias**: User models ✅, Permission system ✅
**Specialist**: @backend-senior-developer

### 2.6 UserAnalytics Service (1.5h)
**Propósito**: Analytics y métricas de usuarios

```python
# app/services/user_analytics_service.py - NUEVO SERVICIO
class UserAnalyticsService:

    def calculate_user_performance_score(self, user_id: int) -> decimal:
        """Calcula score de performance basado en múltiples factores"""
        user = db.query(User).filter(User.id == user_id).first()

        # Factores para el cálculo
        login_frequency = self.get_login_frequency(user_id)
        activity_level = self.get_activity_level(user_id)
        task_completion = self.get_task_completion_rate(user_id)

        # Score ponderado
        score = (
            login_frequency * 0.3 +
            activity_level * 0.4 +
            task_completion * 0.3
        )

        # Actualizar en base de datos
        user.performance_score = round(score, 2)
        db.commit()

        return score

    def get_user_behavior_analytics(self, user_id: int, period_days: int = 30):
        """Analytics comportamental detallado"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)

        activities = db.query(UserActivity).filter(
            UserActivity.user_id == user_id,
            UserActivity.created_at.between(start_date, end_date)
        ).all()

        return {
            "total_sessions": len(set(a.session_id for a in activities)),
            "total_activities": len(activities),
            "most_active_hours": self.calculate_active_hours(activities),
            "activity_breakdown": self.breakdown_by_type(activities),
            "average_session_duration": self.calculate_avg_session_duration(user_id, period_days)
        }

    def get_superuser_global_analytics(self, requesting_user: User):
        """Analytics globales solo para SUPERUSER"""
        if requesting_user.user_type != UserType.SUPERUSER:
            raise PermissionDenied("Only SUPERUSER can access global analytics")

        return {
            "total_users_by_type": self.count_users_by_type(),
            "active_users_today": self.count_active_users_today(),
            "user_growth_trend": self.calculate_user_growth_trend(),
            "top_performers": self.get_top_performing_users(limit=10),
            "users_needing_attention": self.get_underperforming_users(),
            "geographic_distribution": self.get_user_geographic_distribution()
        }
```

**Dependencies**: User models ✅, UserActivity ✅
**Specialist**: @backend-senior-developer

### 2.7 User APIs Enterprise (1.5h)
**Propósito**: APIs completas para gestión de usuarios

```python
# app/api/v1/endpoints/users.py - EXTENDER ENDPOINTS EXISTENTES

# ENDPOINTS EXISTENTES (mantener compatibilidad)
@router.post("/register", response_model=UserResponse)
async def register_user():
    """Registro público de usuarios"""
    pass

@router.post("/login", response_model=TokenResponse)
async def login():
    """Login existente"""
    pass

# NUEVOS ENDPOINTS ENTERPRISE - SUPERUSER
@router.get("/superuser/users/all", response_model=List[UserResponse])
@require_role([UserType.SUPERUSER])
async def get_all_users_superuser(
    role: UserType = None,
    department: str = None,
    is_active: bool = None,
    skip: int = 0,
    limit: int = 100
):
    """SUPERUSER obtiene todos los usuarios con filtros"""
    pass

@router.put("/superuser/users/{user_id}", response_model=UserResponse)
@require_role([UserType.SUPERUSER])
async def update_any_user_superuser(user_id: int, user_data: UserUpdateSchema):
    """SUPERUSER puede editar cualquier usuario"""
    pass

@router.post("/superuser/users/create", response_model=UserResponse)
@require_role([UserType.SUPERUSER])
async def create_user_superuser(user_data: UserCreateSchema):
    """SUPERUSER puede crear usuarios de cualquier tipo"""
    pass

@router.post("/superuser/users/bulk-update", response_model=BulkUpdateResponse)
@require_role([UserType.SUPERUSER])
async def bulk_update_users(user_ids: List[int], updates: dict):
    """Operaciones masivas en usuarios"""
    pass

@router.post("/superuser/users/{user_id}/suspend")
@require_role([UserType.SUPERUSER])
async def suspend_user(user_id: int, suspension_data: SuspensionSchema):
    """Suspender usuario con motivo"""
    pass

@router.get("/superuser/analytics/users", response_model=UserAnalyticsResponse)
@require_role([UserType.SUPERUSER])
async def get_user_analytics():
    """Analytics globales de usuarios"""
    pass

# ENDPOINTS PARA ADMINS
@router.get("/admin/users/department", response_model=List[UserResponse])
@require_role([UserType.ADMIN_VENTAS, UserType.ADMIN_ALMACEN, UserType.ADMIN_FINANZAS, UserType.ADMIN_CLIENTES])
async def get_department_users():
    """Admin ve usuarios de su departamento"""
    pass

# ENDPOINTS PARA USUARIOS NORMALES
@router.get("/users/profile", response_model=UserProfileResponse)
@require_authentication
async def get_own_profile():
    """Usuario ve su propio perfil"""
    pass

@router.put("/users/profile", response_model=UserProfileResponse)
@require_authentication
async def update_own_profile(profile_data: ProfileUpdateSchema):
    """Usuario actualiza su propio perfil"""
    pass
```

**Dependencias**: Existing API structure ✅, Auth middleware ✅
**Specialist**: @backend-senior-developer

---

## ⚛️ FRONTEND - COMPONENTS & INTERFACES (8 horas)

### 2.8 UserManagementDashboard SUPERUSER (3h)
**Propósito**: Control total de usuarios para SUPERUSER

```jsx
// frontend/src/components/superuser/UserManagementDashboard.tsx
import { useState, useEffect } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { userService } from '../../services/userService';

const UserManagementDashboard = () => {
  const { user, hasPermission } = useAuthStore();
  const [users, setUsers] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [filters, setFilters] = useState({});
  const [selectedUsers, setSelectedUsers] = useState([]);

  if (!hasPermission('user.manage_all')) {
    return <Unauthorized />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header con métricas globales de usuarios */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <UserMetricCard
              title="Total Usuarios"
              value={analytics.totalUsers}
              change={analytics.userGrowth}
              icon={Users}
            />
            <UserMetricCard
              title="Activos Hoy"
              value={analytics.activeToday}
              change={analytics.activityChange}
              icon={UserCheck}
            />
            <UserMetricCard
              title="Nuevos (30d)"
              value={analytics.newUsers30d}
              change={analytics.newUserGrowth}
              icon={UserPlus}
            />
            <UserMetricCard
              title="Performance Promedio"
              value={`${analytics.avgPerformance}%`}
              change={analytics.performanceChange}
              icon={TrendingUp}
            />
          </div>
        </div>
      </div>

      {/* Filtros avanzados */}
      <div className="max-w-7xl mx-auto py-6 px-4">
        <UserAdvancedFilters
          filters={filters}
          onFiltersChange={setFilters}
          roles={Object.values(UserType)}
          departments={analytics.departments}
        />

        {/* Acciones masivas */}
        {selectedUsers.length > 0 && (
          <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-blue-800">
                {selectedUsers.length} usuarios seleccionados
              </span>
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  onClick={() => handleBulkAction('activate')}
                >
                  Activar
                </Button>
                <Button
                  variant="outline"
                  onClick={() => handleBulkAction('suspend')}
                >
                  Suspender
                </Button>
                <Button
                  variant="outline"
                  onClick={() => handleBulkAction('export')}
                >
                  Exportar
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Tabla de usuarios */}
        <UserDataTable
          users={users}
          selectedUsers={selectedUsers}
          onSelectionChange={setSelectedUsers}
          actions={[
            'view', 'edit', 'suspend', 'permissions',
            'impersonate', 'analytics', 'reset_password'
          ]}
          onAction={handleUserAction}
        />

        {/* Paginación */}
        <UserPagination
          currentPage={filters.page}
          totalPages={Math.ceil(analytics.totalUsers / filters.limit)}
          onPageChange={(page) => setFilters({...filters, page})}
        />
      </div>

      {/* Modales */}
      <UserEditModal />
      <UserCreateModal />
      <UserPermissionsModal />
      <UserAnalyticsModal />
      <BulkActionConfirmModal />
    </div>
  );
};
```

**Dependencias**: Auth store ✅, UI components ✅
**Specialist**: @frontend-react-specialist

### 2.9 UserProfileEditor Universal (2h)
**Propósito**: Editor de perfil que se adapta según permisos

```jsx
// frontend/src/components/ui/UserProfileEditor.tsx
import { useForm } from 'react-hook-form';
import { UserProfileSchema } from '../../schemas/userSchemas';

const UserProfileEditor = ({ userId, mode = 'edit' }) => {
  const { user: currentUser } = useAuthStore();
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<UserProfileSchema>();

  const canEditField = (fieldName: string) => {
    // SUPERUSER puede editar todo
    if (currentUser.user_type === 'SUPERUSER') return true;

    // Usuario puede editar su propio perfil (campos limitados)
    if (userId === currentUser.id) {
      const selfEditableFields = [
        'nombres', 'apellidos', 'telefono_movil', 'direccion_completa',
        'notification_preferences', 'ui_preferences'
      ];
      return selfEditableFields.includes(fieldName);
    }

    // Admins pueden editar usuarios de su departamento (campos limitados)
    if (currentUser.user_type.startsWith('ADMIN_')) {
      const adminEditableFields = [
        'is_active', 'performance_score', 'department', 'position'
      ];
      return adminEditableFields.includes(fieldName);
    }

    return false;
  };

  return (
    <div className="max-w-4xl mx-auto">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        {/* Información Personal */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium mb-6">Información Personal</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FormField
              label="Nombres"
              {...register('nombres')}
              disabled={!canEditField('nombres')}
              error={errors.nombres?.message}
            />
            <FormField
              label="Apellidos"
              {...register('apellidos')}
              disabled={!canEditField('apellidos')}
              error={errors.apellidos?.message}
            />
            <FormField
              label="Cédula"
              {...register('cedula')}
              disabled={!canEditField('cedula')}
              error={errors.cedula?.message}
            />
            <FormField
              label="Fecha de Nacimiento"
              type="date"
              {...register('fecha_nacimiento')}
              disabled={!canEditField('fecha_nacimiento')}
              error={errors.fecha_nacimiento?.message}
            />
          </div>
        </div>

        {/* Contacto */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium mb-6">Información de Contacto</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FormField
              label="Teléfono Móvil"
              {...register('telefono_movil')}
              disabled={!canEditField('telefono_movil')}
              error={errors.telefono_movil?.message}
            />
            <FormField
              label="Email"
              type="email"
              {...register('email')}
              disabled={!canEditField('email')}
              error={errors.email?.message}
            />
            <FormField
              label="Departamento"
              {...register('departamento')}
              disabled={!canEditField('departamento')}
              error={errors.departamento?.message}
            />
            <FormField
              label="Ciudad"
              {...register('ciudad')}
              disabled={!canEditField('ciudad')}
              error={errors.ciudad?.message}
            />
          </div>
        </div>

        {/* Control Enterprise - Solo SUPERUSER */}
        {currentUser.user_type === 'SUPERUSER' && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <h3 className="text-lg font-medium mb-6 text-yellow-800">
              Control Enterprise (Solo SUPERUSER)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <SelectField
                label="Tipo de Usuario"
                {...register('user_type')}
                options={Object.values(UserType)}
              />
              <FormField
                label="Departamento Asignado"
                {...register('department')}
              />
              <FormField
                label="Score de Performance"
                type="number"
                min="0"
                max="100"
                {...register('performance_score')}
              />
            </div>
          </div>
        )}

        {/* Botones de acción */}
        <div className="flex justify-end space-x-4">
          <Button
            type="button"
            variant="outline"
            onClick={() => router.back()}
          >
            Cancelar
          </Button>
          <Button
            type="submit"
            loading={loading}
          >
            {mode === 'create' ? 'Crear Usuario' : 'Guardar Cambios'}
          </Button>
        </div>
      </form>
    </div>
  );
};
```

**Dependencias**: Form handling ✅, Auth store ✅
**Specialist**: @frontend-react-specialist

### 2.10 UserActivityMonitor (1.5h)
**Propósito**: Monitor de actividad en tiempo real

```jsx
// frontend/src/components/superuser/UserActivityMonitor.tsx
import { useEffect, useState } from 'react';
import { useRealTimeUpdates } from '../../hooks/useRealTimeUpdates';

const UserActivityMonitor = () => {
  const [activities, setActivities] = useState([]);
  const [filters, setFilters] = useState({
    timeframe: '1h',
    activity_type: 'all',
    user_type: 'all'
  });

  // Real-time updates usando WebSocket o polling
  useRealTimeUpdates('/api/v1/superuser/activities/live', {
    onUpdate: (newActivity) => {
      setActivities(prev => [newActivity, ...prev.slice(0, 99)]);
    }
  });

  return (
    <div className="space-y-6">
      {/* Filtros de tiempo real */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Actividad en Tiempo Real</h2>
          <div className="flex space-x-4">
            <select
              value={filters.timeframe}
              onChange={(e) => setFilters({...filters, timeframe: e.target.value})}
              className="rounded border-gray-300"
            >
              <option value="15m">Últimos 15 min</option>
              <option value="1h">Última hora</option>
              <option value="6h">Últimas 6 horas</option>
              <option value="24h">Último día</option>
            </select>
            <select
              value={filters.activity_type}
              onChange={(e) => setFilters({...filters, activity_type: e.target.value})}
              className="rounded border-gray-300"
            >
              <option value="all">Todas las actividades</option>
              <option value="login">Logins</option>
              <option value="page_view">Navegación</option>
              <option value="action_performed">Acciones</option>
            </select>
          </div>
        </div>
      </div>

      {/* Stream de actividades */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b">
          <h3 className="font-medium">Stream de Actividades</h3>
          <p className="text-sm text-gray-600">
            Actualizaciones en tiempo real de {activities.length} actividades recientes
          </p>
        </div>
        <div className="max-h-96 overflow-y-auto">
          {activities.map((activity) => (
            <ActivityItem
              key={activity.id}
              activity={activity}
              onClick={() => showActivityDetails(activity)}
            />
          ))}
        </div>
      </div>

      {/* Métricas de actividad */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          title="Usuarios Activos"
          value={getActiveUsersCount()}
          icon={Users}
          color="green"
        />
        <MetricCard
          title="Sesiones Concurrentes"
          value={getConcurrentSessions()}
          icon={Monitor}
          color="blue"
        />
        <MetricCard
          title="Acciones/min"
          value={getActionsPerMinute()}
          icon={Activity}
          color="purple"
        />
        <MetricCard
          title="Nuevos Logins"
          value={getNewLogins()}
          icon={LogIn}
          color="orange"
        />
      </div>
    </div>
  );
};

const ActivityItem = ({ activity, onClick }) => {
  const getActivityIcon = (type) => {
    switch (type) {
      case 'login': return <LogIn className="h-4 w-4 text-green-500" />;
      case 'logout': return <LogOut className="h-4 w-4 text-red-500" />;
      case 'page_view': return <Eye className="h-4 w-4 text-blue-500" />;
      case 'action_performed': return <Zap className="h-4 w-4 text-purple-500" />;
      default: return <Circle className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <div
      className="p-4 border-b hover:bg-gray-50 cursor-pointer"
      onClick={onClick}
    >
      <div className="flex items-start space-x-3">
        {getActivityIcon(activity.activity_type)}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900">
            {activity.user_name} - {activity.activity_description}
          </p>
          <p className="text-xs text-gray-500">
            {formatTimeAgo(activity.created_at)} • IP: {activity.ip_address}
          </p>
        </div>
        <div className="text-xs text-gray-400">
          {activity.user_type}
        </div>
      </div>
    </div>
  );
};
```

**Dependencias**: Real-time hooks ✅, WebSocket setup
**Specialist**: @frontend-react-specialist

### 2.11 UserPermissionManager (1.5h)
**Propósito**: Interface para gestión de permisos granulares

```jsx
// frontend/src/components/superuser/UserPermissionManager.tsx
const UserPermissionManager = ({ userId, onClose }) => {
  const [userPermissions, setUserPermissions] = useState([]);
  const [availablePermissions, setAvailablePermissions] = useState([]);
  const [permissionTemplates, setPermissionTemplates] = useState([]);

  return (
    <Modal isOpen onClose={onClose} size="xl">
      <ModalHeader>
        <h2 className="text-xl font-semibold">Gestión de Permisos</h2>
        <p className="text-gray-600">Usuario: {userData.nombres} {userData.apellidos}</p>
      </ModalHeader>

      <ModalBody className="space-y-6">
        {/* Templates rápidos */}
        <div>
          <h3 className="font-medium mb-3">Templates de Permisos</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {permissionTemplates.map(template => (
              <Button
                key={template.id}
                variant="outline"
                size="sm"
                onClick={() => applyTemplate(template)}
                className="text-left"
              >
                <div>
                  <div className="font-medium">{template.name}</div>
                  <div className="text-xs text-gray-500">
                    {template.permissions.length} permisos
                  </div>
                </div>
              </Button>
            ))}
          </div>
        </div>

        {/* Permisos por categoría */}
        <div className="space-y-4">
          {Object.entries(groupPermissionsByCategory(availablePermissions)).map(([category, permissions]) => (
            <PermissionCategory
              key={category}
              title={category}
              permissions={permissions}
              userPermissions={userPermissions}
              onChange={handlePermissionToggle}
            />
          ))}
        </div>

        {/* Permisos temporales */}
        <div className="border-t pt-4">
          <h3 className="font-medium mb-3">Permisos Temporales</h3>
          <div className="bg-yellow-50 p-4 rounded-lg">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={temporaryPermissions.enabled}
                onChange={handleTemporaryToggle}
              />
              <span>Otorgar permisos temporales</span>
            </label>
            {temporaryPermissions.enabled && (
              <div className="mt-3 grid grid-cols-2 gap-3">
                <FormField
                  label="Fecha de expiración"
                  type="datetime-local"
                  value={temporaryPermissions.expires_at}
                  onChange={handleExpirationChange}
                />
                <FormField
                  label="Motivo"
                  value={temporaryPermissions.reason}
                  onChange={handleReasonChange}
                />
              </div>
            )}
          </div>
        </div>
      </ModalBody>

      <ModalFooter>
        <Button variant="outline" onClick={onClose}>
          Cancelar
        </Button>
        <Button onClick={savePermissions}>
          Guardar Permisos
        </Button>
      </ModalFooter>
    </Modal>
  );
};

const PermissionCategory = ({ title, permissions, userPermissions, onChange }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="border rounded-lg">
      <div
        className="p-4 cursor-pointer flex items-center justify-between"
        onClick={() => setExpanded(!expanded)}
      >
        <div>
          <h4 className="font-medium">{title}</h4>
          <p className="text-sm text-gray-600">
            {permissions.filter(p => userPermissions.includes(p.name)).length} de {permissions.length} activos
          </p>
        </div>
        <ChevronDown className={`h-4 w-4 transform ${expanded ? 'rotate-180' : ''}`} />
      </div>

      {expanded && (
        <div className="border-t p-4 space-y-2">
          {permissions.map(permission => (
            <label
              key={permission.id}
              className="flex items-center justify-between p-2 hover:bg-gray-50 rounded"
            >
              <div>
                <div className="font-medium text-sm">{permission.display_name}</div>
                <div className="text-xs text-gray-500">{permission.description}</div>
              </div>
              <input
                type="checkbox"
                checked={userPermissions.includes(permission.name)}
                onChange={() => onChange(permission.name)}
                className="rounded"
              />
            </label>
          ))}
        </div>
      )}
    </div>
  );
};
```

**Dependencias**: Modal components ✅, Permission service
**Specialist**: @frontend-react-specialist

---

## 📊 INTEGRACIÓN CON SISTEMA BASE

### Compatible con TODO_CONFIGURACION_BASE_ENTERPRISE.md:
✅ **Database Architecture**: Extiende User model existente sin breaking changes
✅ **Auth System**: Integra con JWT y RBAC existente, añade permisos granulares
✅ **API Structure**: Sigue convención `/api/v1/` con nuevos endpoints enterprise
✅ **Frontend Architecture**: Usa stores existentes y extiende component architecture
✅ **State Management**: Integra con authStore existente, añade userManagementStore

### APIs que conectan con otros módulos:
- `GET /api/v1/users/{user_id}/orders` → Módulo Orders
- `GET /api/v1/users/{user_id}/products` → Módulo Products
- `POST /api/v1/notifications/users/{user_id}` → Módulo Notifications
- `GET /api/v1/analytics/users/{user_id}` → Módulo Analytics

---

## ✅ TESTING & VALIDATION

### Tests Backend (qa-engineer-pytest):
```python
def test_superuser_can_manage_any_user():
    """SUPERUSER debe poder editar cualquier usuario"""
    pass

def test_admin_can_only_manage_department_users():
    """Admin solo puede gestionar usuarios de su departamento"""
    pass

def test_user_permission_system_works():
    """Sistema de permisos granulares funciona correctamente"""
    pass
```

### Tests Frontend:
```typescript
describe('UserManagementDashboard', () => {
  test('SUPERUSER sees all users', () => {});
  test('Admin sees only department users', () => {});
  test('Permission system works correctly', () => {});
});
```

---

## 🎯 CRITERIOS DE ÉXITO

### Funcionalidades Críticas:
- [ ] SUPERUSER controla todos los usuarios de todos los tipos
- [ ] Sistema de permisos granulares funcional
- [ ] Analytics comportamental operativo
- [ ] Gestión de suspensiones con auditoría
- [ ] Operaciones masivas funcionales
- [ ] Monitor de actividad en tiempo real

### Integration Success:
- [ ] Compatible con auth system existente
- [ ] APIs siguen convenciones enterprise
- [ ] Frontend integrado con architecture base
- [ ] Preparado para futuros agentes IA

---

**🔗 MÓDULO COMPATIBLE CON ENTERPRISE BASE**
**👥 GESTIÓN COMPLETA DE USUARIOS**
**⏱️ 18 HORAS IMPLEMENTACIÓN COORDINADA**