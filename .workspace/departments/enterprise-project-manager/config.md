# 🎯 CONFIGURACIÓN DEL PROYECTO - MANAGER UNIVERSAL

## 📋 DATOS GENERALES DEL PROYECTO

```yaml
# Configuración del Proyecto
project_name: "MeStore"
project_code: "MeStocker"
description: "Sistema completo de marketplace que permite a usuarios vender y comprar productos de manera eficiente y segura"
version: "1.0.0"
environment: "development"
```

## 🛠️ STACK TECNOLÓGICO

```yaml
technology_stack:
  backend: 
    framework: "FastAPI"
    language: "Python 3.11+"
    orm: "SQLAlchemy"
    validation: "Pydantic"
    testing: "pytest"
  
  frontend:
    framework: "React 18"
    language: "TypeScript"
    build_tool: "Vite"
    css: "Tailwind CSS"
    testing: "Jest + Testing Library"
    
  database:
    primary: "PostgreSQL"
    cache: "Redis"
    
  tools:
    containerization: "Docker + Docker Compose"
    version_control: "Git"
    api_docs: "OpenAPI/Swagger"
```

## 🌐 CONFIGURACIÓN DE SERVIDORES

```yaml
server_config:
  backend:
    url: "http://192.168.1.137:8000"
    docs: "http://192.168.1.137:8000/docs"
    redoc: "http://192.168.1.137:8000/redoc"
    health: "http://192.168.1.137:8000/health"
    
  frontend:
    url: "http://192.168.1.137:5173"
    dev_command: "npm run dev"
    build_command: "npm run build"
    
  database:
    url: "postgresql+asyncpg://mestocker_user:mestocker_pass@localhost/mestocker_dev"
    host: "localhost"
    port: 5432
    name: "mestocker_dev"
    
  redis:
    host: "localhost"
    port: 6379
    db: 0
```

## 🌍 ENTORNOS DISPONIBLES

```yaml
environments:
  development:
    server: "192.168.1.137"
    backend_port: 8000
    frontend_port: 5173
    debug: true
    log_level: "DEBUG"
    
  staging:
    server: "TBD"
    status: "not_configured"
    
  production:
    server: "TBD"
    status: "not_configured"
    migrations_validation: "strict"
```

## 🔐 CREDENCIALES DE PRUEBA

```yaml
test_credentials:
  admin:
    email: "super@mestore.com"
    password: "123456"
    role: "administrator"
    
  vendor:
    email: "vendor@mestore.com"
    password: "123456"
    role: "vendor"
    
  buyer:
    email: "buyer@mestore.com"
    password: "123456"
    role: "buyer"
```

## 📁 ESTRUCTURA DE DIRECTORIOS

```yaml
key_directories:
  project_root: "/home/admin-jairo/MeStore"
  backend: "/home/admin-jairo/MeStore"
  frontend: "/home/admin-jairo/MeStore/frontend"
  docs: "/home/admin-jairo/MeStore/docs"
  logs: "/home/admin-jairo/MeStore/logs"
  uploads: "/home/admin-jairo/MeStore/uploads"
  workspace: "/home/admin-jairo/MeStore/.workspace"
  
  backend_structure:
    models: "app/models/"
    services: "app/services/"
    api: "app/api/v1/"
    schemas: "app/schemas/"
    core: "app/core/"
    tests: "tests/"
    
  frontend_structure:
    components: "frontend/src/components/"
    pages: "frontend/src/pages/"
    hooks: "frontend/src/hooks/"
    utils: "frontend/src/utils/"
    stores: "frontend/src/stores/"
    services: "frontend/src/services/"
```

## ⚙️ VARIABLES DE ENTORNO

```yaml
environment_files:
  development: ".env"
  production: ".env.production"
  test: ".env.test"
  template: ".env.template"
  
key_variables:
  database: "DATABASE_URL"
  cors: "CORS_ORIGINS"
  logging: "LOG_LEVEL"
  environment: "ENVIRONMENT"
  redis: "REDIS_HOST, REDIS_PORT, REDIS_DB"
  rate_limiting: "RATE_LIMIT_AUTHENTICATED_PER_MINUTE"
  security: "SUSPICIOUS_IPS, ENABLE_IP_BLACKLIST"
```

## 🧪 COMANDOS DE DESARROLLO

```yaml
backend_commands:
  start: "uvicorn app.main:app --reload"
  test: "pytest"
  test_coverage: "pytest --cov=app"
  lint: "ruff check ."
  format: "black ."
  migrations_create: "alembic revision --autogenerate -m"
  migrations_upgrade: "alembic upgrade head"
  migrations_current: "alembic current"
  
frontend_commands:
  start: "npm run dev"
  build: "npm run build"
  test: "npm test"
  test_watch: "npm run test:watch"
  test_coverage: "npm run test:coverage"
  lint: "npm run lint"
  format: "npm run format"
  
docker_commands:
  start_all: "docker-compose up -d"
  build: "docker-compose build"
  logs: "docker-compose logs -f"
  stop: "docker-compose down"
```

## 📊 ESTADO ACTUAL DEL PROYECTO

```yaml
project_status:
  overall: "functional"
  backend:
    status: "operational"
    api_endpoints: "working"
    database: "connected"
    authentication: "implemented"
    testing: "partial"
    
  frontend:
    status: "operational"
    ui_components: "implemented"
    routing: "working"
    state_management: "zustand"
    testing: "configured"
    
  features_implemented:
    - "User authentication system"
    - "User management (CRUD)"
    - "Role-based access control"
    - "Product management"
    - "Order system"
    - "Transaction tracking"
    - "Commission system"
    - "Payment integration (Wompi)"
    - "Dashboard for different user types"
    
  features_in_progress:
    - "Advanced testing coverage"
    - "Performance optimization"
    - "Security hardening"
    
  known_issues:
    - "Some TypeScript errors pending"
    - "Test coverage incomplete"
    - "Production deployment not configured"
```

## 🔧 CONFIGURACIÓN DE HERRAMIENTAS

```yaml
git_configuration:
  current_branch: "test/pipeline-validation-0.2.5.6"
  main_branch: "main"
  recent_commits:
    - "96433720: fix: Complete error correction"
    - "0b3bbbc9: feat: Complete enterprise order management"
    - "a7a82816: fix: Complete backend error correction"
    
development_tools:
  ide_recommended: "VS Code"
  extensions:
    - "Python extension"
    - "TypeScript extension"  
    - "ES7+ React snippets"
    - "Prettier"
    - "ESLint"
    
quality_tools:
  backend:
    linting: "ruff"
    formatting: "black"
    testing: "pytest"
    coverage: "pytest-cov"
    
  frontend:
    linting: "ESLint"
    formatting: "Prettier"
    testing: "Jest + Testing Library"
    bundling: "Vite"
```

## 🚀 ESPECIALISTAS REQUERIDOS

```yaml
specialists_needed:
  priority_high:
    - name: "Backend Senior Developer"
      expertise: ["FastAPI", "Python", "SQLAlchemy", "PostgreSQL"]
      department: "backend"
      
    - name: "Frontend React Specialist"
      expertise: ["React", "TypeScript", "Vite", "Tailwind"]
      department: "frontend"
      
  priority_medium:
    - name: "Database Expert"
      expertise: ["PostgreSQL", "Migrations", "Performance"]
      department: "backend"
      
    - name: "DevOps Engineer"
      expertise: ["Docker", "Deployment", "CI/CD"]
      department: "devops"
      
  priority_low:
    - name: "QA Engineer"
      expertise: ["Testing", "Quality Assurance", "Automation"]
      department: "qa"
      
    - name: "Security Specialist"
      expertise: ["Security", "Authentication", "Vulnerabilities"]
      department: "security"
```

## 📈 MÉTRICAS Y OBJETIVOS

```yaml
performance_targets:
  backend:
    response_time: "<200ms"
    throughput: ">1000 req/min"
    uptime: ">99.9%"
    
  frontend:
    load_time: "<3s"
    first_paint: "<1s"
    bundle_size: "<1MB"
    
quality_targets:
  test_coverage: ">80%"
  code_quality: "A grade"
  security_score: ">90%"
  accessibility: "WCAG 2.1 AA"
```

---

**📅 Última actualización:** 2025-09-13  
**🔧 Configurado por:** Manager Universal  
**📋 Estado:** Operacional - Listo para delegación de tareas