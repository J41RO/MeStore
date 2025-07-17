# Arquitectura Híbrida MeStocker: Fulfillment + Marketplace + Agentes IA

## 🎯 Visión General

La arquitectura híbrida de MeStocker integra tres dominios tecnológicos principales en un ecosistema cohesivo y escalable: **Fulfillment** (operaciones físicas de almacén), **Marketplace** (plataforma comercial digital) y **Agentes IA** (automatización inteligente). Esta arquitectura está diseñada para el mercado colombiano, optimizando la experiencia del usuario, la eficiencia operacional y la toma de decisiones basada en datos.

### Filosofía Arquitectónica:
- **Domain-Driven Design**: Separación clara de responsabilidades por dominio de negocio
- **Event-Driven Architecture**: Comunicación asíncrona y desacoplada entre servicios
- **API-First**: Interfaces bien definidas para integración y extensibilidad
- **Hybrid Cloud**: Balance entre soberanía de datos (local) y capacidades cloud
- **Privacy by Design**: Protección de datos desde el diseño arquitectónico

### Objetivos Clave:

#### 1. Cohesión
- **Unified User Experience**: Experiencia consistente entre vendedores y compradores
- **Shared Data Models**: Modelos de datos coherentes cross-domain
- **Consistent APIs**: Patrones uniformes de diseño de APIs
- **Centralized Authentication**: Sistema único de autenticación y autorización

#### 2. Escalabilidad
- **Horizontal Scaling**: Capacidad de escalar servicios independientemente
- **Load Distribution**: Balanceadores de carga inteligentes por funcionalidad
- **Resource Optimization**: Uso eficiente de recursos computacionales
- **Geographic Distribution**: Soporte para múltiples regiones colombianas

#### 3. Resiliencia
- **Fault Tolerance**: Tolerancia a fallos con degradación gradual
- **Circuit Breakers**: Protección contra cascading failures
- **Redundancy**: Múltiples layers de backup y fallback
- **Health Monitoring**: Monitoreo proactivo de salud del sistema

#### 4. Privacidad
- **Data Sovereignty**: Control completo sobre datos sensibles
- **Local Processing**: Procesamiento local para información confidencial
- **Audit Trail**: Trazabilidad completa de acceso y procesamiento de datos
- **Compliance**: Cumplimiento con GDPR y regulaciones colombianas

## 🏗️ Componentes Principales

### 1. API Gateway (Kong/AWS API Gateway)

**Responsabilidades:**
- **Unified Entry Point**: Punto único de entrada para todas las APIs
- **Authentication & Authorization**: Validación de tokens JWT y OAuth2
- **Rate Limiting**: Protección contra abuse y control de cuotas
- **Request Routing**: Enrutamiento inteligente a microservicios
- **Protocol Translation**: REST to gRPC, HTTP to WebSocket
- **Monitoring & Analytics**: Métricas de uso y performance

### 2. Microservicios Backend

#### 2.1 Fulfillment Service (FastAPI + SQLAlchemy)
**Tech Stack:**
- **Framework**: FastAPI para APIs REST de alta performance
- **ORM**: SQLAlchemy para mapeo objeto-relacional
- **Database**: PostgreSQL para datos transaccionales
- **Cache**: Redis para consultas frecuentes de inventario
- **Message Queue**: Kafka para eventos de stock y movimientos

#### 2.2 Marketplace Service (FastAPI + Pydantic)
**Tech Stack:**
- **Framework**: FastAPI para APIs de e-commerce
- **Validation**: Pydantic para validación de datos robusta
- **Database**: PostgreSQL para productos, órdenes, usuarios
- **Search Engine**: Elasticsearch para búsqueda de productos
- **Payment Gateway**: Integración con PayU, MercadoPago, Nequi

#### 2.3 Agents Orchestrator (FastAPI + LLM Routing)
**Tech Stack:**
- **Framework**: FastAPI para APIs de agentes IA
- **LLM Local**: vLLM/TGI para modelos Llama, Mistral
- **LLM Cloud**: OpenAI GPT-4, Claude Sonnet
- **Vector DB**: ChromaDB para embeddings y RAG
- **ML Pipeline**: TensorFlow/PyTorch para modelos custom

### 3. Event Bus (Apache Kafka + Redis Streams)
#### 3.1 Apache Kafka (High-Throughput Events)
- **Order Events**: `order.created`, `order.paid`, `order.shipped`
- **Inventory Events**: `stock.updated`, `stock.low`, `movement.recorded`
- **User Events**: `user.registered`, `user.verified`, `purchase.completed`
- **Analytics Events**: Stream de eventos para business intelligence

#### 3.2 Redis Streams (Real-time Communication)
- **Chat Messages**: Mensajes de chat en tiempo real
- **Notifications**: Push notifications y alerts
- **Live Updates**: Actualizaciones de estado en dashboard
- **Cache Invalidation**: Invalidación de cache coordinada

### 4. Data Stores
- **PostgreSQL**: Datos transaccionales (inventario, productos, órdenes, usuarios)
- **Redis**: Cache, sesiones, pub/sub, rate limiting
- **ChromaDB**: Vector embeddings para recomendaciones y RAG
- **Elasticsearch**: Búsqueda de productos y analytics

### 5. Edge LLM Layer
- **Local LLMs**: vLLM/TGI con Llama, Mistral para datos sensibles
- **Cloud LLMs**: OpenAI GPT-4, Claude para razonamiento complejo
- **Routing Inteligente**: Decisiones automáticas por privacidad y performance

## 🔄 Flujos de Datos y Eventos

### 1. Inbound Pedido
**Cliente** → **Marketplace** valida carrito → emite `order.created` → **Fulfillment** recibe evento → reserva stock → emite `stock.reserved` → **Marketplace** actualiza estado → **Agents** notifica confirmación

### 2. Consulta Vendedor/Cliente
**Usuario** → **Agents Orchestrator** clasifica consulta → decide ruta (Local LLM para datos sensibles, Cloud LLM para razonamiento complejo) → procesa respuesta → entrega resultado contextualizado

### 3. Reorden Automático
**Inventory Agent** monitorea niveles → predice stock bajo → emite `stock.low_predicted` → **Fulfillment** calcula cantidad reorden → genera PO automático → emite `reorder.initiated`

### 4. Checkout
**Marketplace** valida inventario → procesa pago con gateway → emite `payment.success` → **Fulfillment** inicia despacho → **Agents** envía tracking

## 🔐 Políticas de Integración y Seguridad

### 1. Autenticación (OAuth2/JWT)
- **JWT Tokens**: Con scopes granulares por servicio
- **Multi-Factor**: MFA obligatorio para administradores
- **Token Refresh**: Refresh automático para sesiones largas
- **Service-to-Service**: Client credentials para comunicación interna

### 2. Autorización (RBAC)
- **Roles**: superuser, admin, cliente, comprador
- **Scopes**: Permisos granulares por recurso y operación
- **API Gateway**: Validación centralizada de permisos
- **Resource Ownership**: Validación de propiedad de recursos

### 3. Cifrado
- **TLS Everywhere**: TLS 1.3 para tráfico externo, mTLS interno
- **Data at Rest**: AES-256 para datos sensibles en base de datos
- **E2E Messaging**: Encriptación para mensajes de chat
- **Key Management**: Rotación automática de claves cada 90 días

### 4. Privacidad
- **Data Classification**: Público, interno, sensible, confidencial
- **Local Processing**: Datos sensibles solo en LLMs locales
- **Audit Trail**: Registro completo en `llm_routing_logs`
- **GDPR Compliance**: Derecho al olvido y portabilidad

## 📊 Diagramas

### Diagrama de Alto Nivel
[Clients] → [API Gateway] → [Microservices: Marketplace|Fulfillment|Agents]
↓
[Event Bus: Kafka + Redis]
↓
[Data Stores: PostgreSQL|Redis|ChromaDB|Elasticsearch]
↓
[LLM Layer: Local + Cloud]

### Flujo de Eventos
[Order Created] → [Stock Reserved] → [Payment Processed] → [Fulfillment Started] → [Shipped] → [Delivered]
↓              ↓                   ↓                     ↓               ↓           ↓
[Analytics]    [Inventory]        [Finance]           [Logistics]      [Tracking]  [Reviews]

## 🚀 Escalabilidad y Despliegue

### 1. Contenedores (Docker Compose)
- **Development**: Docker Compose para desarrollo local
- **Services**: Un contenedor por microservicio
- **Dependencies**: PostgreSQL, Redis, Kafka, ChromaDB containerizados
- **Volumes**: Persistencia para desarrollo y testing

### 2. Orquestación (Kubernetes + Helm)
- **Production**: Clusters Kubernetes en múltiples regiones
- **Auto-scaling**: HPA basado en CPU, memoria y métricas custom
- **Load Balancing**: Ingress controllers con distribución inteligente
- **Service Mesh**: Istio para comunicación segura entre servicios

### 3. Health Checks
- **Liveness Probes**: Verificación básica de que el servicio responde
- **Readiness Probes**: Verificación completa de dependencias
- **Custom Metrics**: Métricas específicas por dominio de negocio
- **Monitoring**: Prometheus + Grafana para observabilidad completa

### 4. Geographic Distribution
- **Multi-Region**: Clusters en Bogotá, Medellín, Barranquilla
- **Data Locality**: Datos cerca de usuarios para menor latencia
- **Disaster Recovery**: Backup automático cross-region
- **CDN Integration**: CloudFlare para contenido estático

---

**Documento creado**: 2025-07-17  
**Versión**: 1.0  
**Autor**: Equipo MeStocker  
**Próxima revisión**: Tras implementación inicial de arquitectura
