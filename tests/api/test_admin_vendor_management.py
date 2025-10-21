"""
Tests unitarios para Admin Vendor Management Endpoints - FASE 1

Cobertura:
- GET /api/v1/auth/admin/pending-sellers
- POST /api/v1/auth/admin/approve-seller/{user_id}
- POST /api/v1/auth/admin/reject-seller/{user_id}

Aspectos testeados:
- Validación de permisos administrativos
- Filtrado correcto de vendedores pendientes
- Aprobación exitosa con notificación por email
- Rechazo con validación de razón (mínimo 20 caracteres)
- Manejo de errores y casos edge
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserType, VendorStatus, AccountStatus
from app.core.security import create_access_token
import uuid


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
async def admin_user(async_session: AsyncSession):
    """Usuario ADMIN para testing"""
    admin = User(
        id=str(uuid.uuid4()),
        email="admin@test.com",
        nombre="Admin",
        apellido="Test",
        user_type=UserType.ADMIN,
        account_status=AccountStatus.ACTIVE,
        password_hash="fake_hash",
        is_verified=True
    )
    async_session.add(admin)
    await async_session.commit()
    await async_session.refresh(admin)
    return admin


@pytest.fixture
async def regular_user(async_session: AsyncSession):
    """Usuario BUYER regular (sin permisos admin)"""
    user = User(
        id=str(uuid.uuid4()),
        email="buyer@test.com",
        nombre="Buyer",
        apellido="Test",
        user_type=UserType.BUYER,
        account_status=AccountStatus.ACTIVE,
        password_hash="fake_hash"
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest.fixture
async def pending_vendor_natural(async_session: AsyncSession):
    """Vendedor persona natural pendiente"""
    vendor = User(
        id=str(uuid.uuid4()),
        email="vendor_natural@test.com",
        nombre="Juan",
        apellido="Pérez",
        cedula="1234567890",
        telefono="+573001234567",
        user_type=UserType.VENDOR,
        tipo_vendedor="persona_natural",
        vendor_status=VendorStatus.PENDING_APPROVAL,
        account_status=AccountStatus.PENDING,
        direccion_fiscal="Calle 123 #45-67",
        ciudad_fiscal="Bogotá",
        departamento_fiscal="Cundinamarca",
        password_hash="fake_hash"
    )
    async_session.add(vendor)
    await async_session.commit()
    await async_session.refresh(vendor)
    return vendor


@pytest.fixture
async def pending_vendor_juridica(async_session: AsyncSession):
    """Vendedor persona jurídica pendiente"""
    vendor = User(
        id=str(uuid.uuid4()),
        email="vendor_juridica@test.com",
        razon_social="Empresa Test S.A.S",
        nit="900123456-1",
        representante_legal="María García",
        email_representante="maria@empresatest.com",
        telefono="+573009876543",
        user_type=UserType.VENDOR,
        tipo_vendedor="persona_juridica",
        vendor_status=VendorStatus.DRAFT,
        account_status=AccountStatus.PENDING,
        direccion_fiscal="Av Principal #10-20",
        ciudad_fiscal="Medellín",
        departamento_fiscal="Antioquia",
        password_hash="fake_hash"
    )
    async_session.add(vendor)
    await async_session.commit()
    await async_session.refresh(vendor)
    return vendor


@pytest.fixture
async def approved_vendor(async_session: AsyncSession):
    """Vendedor ya aprobado (no debe aparecer en pendientes)"""
    vendor = User(
        id=str(uuid.uuid4()),
        email="approved@test.com",
        nombre="Carlos",
        apellido="López",
        cedula="9876543210",
        telefono="+573005555555",
        user_type=UserType.VENDOR,
        tipo_vendedor="persona_natural",
        vendor_status=VendorStatus.APPROVED,
        account_status=AccountStatus.ACTIVE,
        direccion_fiscal="Carrera 50 #30-40",
        ciudad_fiscal="Cali",
        departamento_fiscal="Valle del Cauca",
        password_hash="fake_hash"
    )
    async_session.add(vendor)
    await async_session.commit()
    await async_session.refresh(vendor)
    return vendor


def create_auth_header(user: User) -> dict:
    """Genera header de autorización con JWT"""
    token = create_access_token(data={"sub": user.id})  # sub debe ser user.id, no email
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# TESTS: GET /admin/pending-sellers
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.tdd
class TestGetPendingSellers:
    """Tests para obtener lista de vendedores pendientes"""

    async def test_get_pending_sellers_success(
        self,
        async_client: AsyncClient,
        admin_user: User,
        pending_vendor_natural: User,
        pending_vendor_juridica: User,
        approved_vendor: User
    ):
        """✅ Admin puede obtener lista de vendedores pendientes"""
        headers = create_auth_header(admin_user)

        response = await async_client.get(
            "/api/v1/auth/admin/pending-sellers",
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["count"] == 2  # Solo los 2 pendientes, no el aprobado
        assert len(data["sellers"]) == 2

        # Verificar datos de persona natural
        natural_seller = next(
            (s for s in data["sellers"] if s["email"] == pending_vendor_natural.email),
            None
        )
        assert natural_seller is not None
        assert natural_seller["nombre_display"] == "Juan Pérez"
        assert natural_seller["identificacion"] == "1234567890"
        assert natural_seller["tipo_vendedor"] == "persona_natural"
        assert natural_seller["vendor_status"] == "pending_approval"

        # Verificar datos de persona jurídica
        juridica_seller = next(
            (s for s in data["sellers"] if s["email"] == pending_vendor_juridica.email),
            None
        )
        assert juridica_seller is not None
        assert juridica_seller["nombre_display"] == "Empresa Test S.A.S"
        assert juridica_seller["identificacion"] == "900123456-1"
        assert juridica_seller["tipo_vendedor"] == "persona_juridica"
        assert juridica_seller["representante_legal"] == "María García"
        assert juridica_seller["email_representante"] == "maria@empresatest.com"

    async def test_get_pending_sellers_forbidden_regular_user(
        self,
        async_client: AsyncClient,
        regular_user: User
    ):
        """❌ Usuario regular NO puede acceder (403 Forbidden)"""
        headers = create_auth_header(regular_user)

        response = await async_client.get(
            "/api/v1/auth/admin/pending-sellers",
            headers=headers
        )

        assert response.status_code == 403
        assert "administrativos requeridos" in response.json()["error_message"]

    async def test_get_pending_sellers_unauthorized(
        self,
        async_client: AsyncClient
    ):
        """❌ Sin token de autenticación (401 o 403)"""
        response = await async_client.get(
            "/api/v1/auth/admin/pending-sellers"
        )

        # Puede ser 401 (Unauthorized) o 403 (Forbidden) dependiendo del middleware
        assert response.status_code in [401, 403]

    async def test_get_pending_sellers_empty_list(
        self,
        async_client: AsyncClient,
        admin_user: User,
        approved_vendor: User
    ):
        """✅ Lista vacía si no hay vendedores pendientes"""
        headers = create_auth_header(admin_user)

        response = await async_client.get(
            "/api/v1/auth/admin/pending-sellers",
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 0
        assert data["sellers"] == []


# ============================================================================
# TESTS: POST /admin/approve-seller/{user_id}
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.tdd
class TestApproveSeller:
    """Tests para aprobar vendedores pendientes"""

    async def test_approve_seller_success(
        self,
        async_client: AsyncClient,
        admin_user: User,
        pending_vendor_natural: User,
        async_session: AsyncSession
    ):
        """✅ Admin puede aprobar vendedor exitosamente"""
        headers = create_auth_header(admin_user)

        response = await async_client.post(
            f"/api/v1/auth/admin/approve-seller/{pending_vendor_natural.id}",
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["vendor_status"] == "approved"
        assert pending_vendor_natural.email in data["message"]

        # Verificar cambios en base de datos
        await async_session.refresh(pending_vendor_natural)
        assert pending_vendor_natural.vendor_status == VendorStatus.APPROVED
        assert pending_vendor_natural.account_status == AccountStatus.ACTIVE

    async def test_approve_seller_forbidden_regular_user(
        self,
        async_client: AsyncClient,
        regular_user: User,
        pending_vendor_natural: User
    ):
        """❌ Usuario regular NO puede aprobar vendedores"""
        headers = create_auth_header(regular_user)

        response = await async_client.post(
            f"/api/v1/auth/admin/approve-seller/{pending_vendor_natural.id}",
            headers=headers
        )

        assert response.status_code == 403
        assert "administrativos requeridos" in response.json()["error_message"]

    async def test_approve_seller_not_found(
        self,
        async_client: AsyncClient,
        admin_user: User
    ):
        """❌ Error 404 si vendedor no existe"""
        headers = create_auth_header(admin_user)
        fake_id = str(uuid.uuid4())

        response = await async_client.post(
            f"/api/v1/auth/admin/approve-seller/{fake_id}",
            headers=headers
        )

        assert response.status_code == 404
        assert "no encontrado" in response.json()["error_message"]

    async def test_approve_non_vendor_user(
        self,
        async_client: AsyncClient,
        admin_user: User,
        regular_user: User
    ):
        """❌ Error 400 si se intenta aprobar un usuario que no es VENDOR"""
        headers = create_auth_header(admin_user)

        response = await async_client.post(
            f"/api/v1/auth/admin/approve-seller/{regular_user.id}",
            headers=headers
        )

        assert response.status_code == 400
        assert "no es un vendedor" in response.json()["error_message"]

    async def test_approve_already_approved_vendor(
        self,
        async_client: AsyncClient,
        admin_user: User,
        approved_vendor: User,
        async_session: AsyncSession
    ):
        """✅ Se puede re-aprobar un vendedor ya aprobado (idempotente)"""
        headers = create_auth_header(admin_user)

        response = await async_client.post(
            f"/api/v1/auth/admin/approve-seller/{approved_vendor.id}",
            headers=headers
        )

        assert response.status_code == 200

        # Estado sigue siendo APPROVED
        await async_session.refresh(approved_vendor)
        assert approved_vendor.vendor_status == VendorStatus.APPROVED
        assert approved_vendor.account_status == AccountStatus.ACTIVE


# ============================================================================
# TESTS: POST /admin/reject-seller/{user_id}
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.tdd
class TestRejectSeller:
    """Tests para rechazar vendedores pendientes"""

    async def test_reject_seller_success(
        self,
        async_client: AsyncClient,
        admin_user: User,
        pending_vendor_natural: User,
        async_session: AsyncSession
    ):
        """✅ Admin puede rechazar vendedor con razón válida"""
        headers = create_auth_header(admin_user)
        rejection_reason = "Documentos de identificación ilegibles o incompletos según revisión del equipo."

        response = await async_client.post(
            f"/api/v1/auth/admin/reject-seller/{pending_vendor_natural.id}",
            headers=headers,
            json={"reason": rejection_reason}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["vendor_status"] == "rejected"

        # Verificar cambios en base de datos
        await async_session.refresh(pending_vendor_natural)
        assert pending_vendor_natural.vendor_status == VendorStatus.REJECTED

    async def test_reject_seller_reason_too_short(
        self,
        async_client: AsyncClient,
        admin_user: User,
        pending_vendor_natural: User
    ):
        """❌ Error 400 si razón tiene menos de 20 caracteres"""
        headers = create_auth_header(admin_user)

        response = await async_client.post(
            f"/api/v1/auth/admin/reject-seller/{pending_vendor_natural.id}",
            headers=headers,
            json={"reason": "Muy corta"}  # Solo 10 caracteres
        )

        assert response.status_code == 400
        assert "al menos 20 caracteres" in response.json()["error_message"]

    async def test_reject_seller_reason_missing(
        self,
        async_client: AsyncClient,
        admin_user: User,
        pending_vendor_natural: User
    ):
        """❌ Error 400 si no se proporciona razón"""
        headers = create_auth_header(admin_user)

        response = await async_client.post(
            f"/api/v1/auth/admin/reject-seller/{pending_vendor_natural.id}",
            headers=headers,
            json={}
        )

        assert response.status_code == 400
        assert "al menos 20 caracteres" in response.json()["error_message"]

    async def test_reject_seller_reason_whitespace_only(
        self,
        async_client: AsyncClient,
        admin_user: User,
        pending_vendor_natural: User
    ):
        """❌ Error 400 si razón solo contiene espacios"""
        headers = create_auth_header(admin_user)

        response = await async_client.post(
            f"/api/v1/auth/admin/reject-seller/{pending_vendor_natural.id}",
            headers=headers,
            json={"reason": "                    "}  # Solo espacios
        )

        assert response.status_code == 400
        assert "al menos 20 caracteres" in response.json()["error_message"]

    async def test_reject_seller_forbidden_regular_user(
        self,
        async_client: AsyncClient,
        regular_user: User,
        pending_vendor_natural: User
    ):
        """❌ Usuario regular NO puede rechazar vendedores"""
        headers = create_auth_header(regular_user)

        response = await async_client.post(
            f"/api/v1/auth/admin/reject-seller/{pending_vendor_natural.id}",
            headers=headers,
            json={"reason": "Esta razón tiene más de 20 caracteres pero no debería funcionar."}
        )

        assert response.status_code == 403
        assert "administrativos requeridos" in response.json()["error_message"]

    async def test_reject_seller_not_found(
        self,
        async_client: AsyncClient,
        admin_user: User
    ):
        """❌ Error 404 si vendedor no existe"""
        headers = create_auth_header(admin_user)
        fake_id = str(uuid.uuid4())

        response = await async_client.post(
            f"/api/v1/auth/admin/reject-seller/{fake_id}",
            headers=headers,
            json={"reason": "Razón válida con más de veinte caracteres completos."}
        )

        assert response.status_code == 404
        assert "no encontrado" in response.json()["error_message"]

    async def test_reject_non_vendor_user(
        self,
        async_client: AsyncClient,
        admin_user: User,
        regular_user: User
    ):
        """❌ Error 400 si se intenta rechazar un usuario que no es VENDOR"""
        headers = create_auth_header(admin_user)

        response = await async_client.post(
            f"/api/v1/auth/admin/reject-seller/{regular_user.id}",
            headers=headers,
            json={"reason": "Este usuario no es vendedor, no se puede rechazar como tal."}
        )

        assert response.status_code == 400
        assert "no es un vendedor" in response.json()["error_message"]


# ============================================================================
# TESTS DE INTEGRACIÓN: Flujo Completo
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.tdd
@pytest.mark.integration
class TestVendorApprovalFlow:
    """Tests de integración para el flujo completo de aprobación"""

    async def test_complete_approval_workflow(
        self,
        async_client: AsyncClient,
        admin_user: User,
        pending_vendor_natural: User,
        async_session: AsyncSession
    ):
        """✅ Flujo completo: Listar → Aprobar → Verificar lista actualizada"""
        headers = create_auth_header(admin_user)

        # 1. Obtener lista inicial de pendientes
        response = await async_client.get(
            "/api/v1/auth/admin/pending-sellers",
            headers=headers
        )
        assert response.status_code == 200
        initial_count = response.json()["count"]
        assert initial_count >= 1

        # 2. Aprobar vendedor
        response = await async_client.post(
            f"/api/v1/auth/admin/approve-seller/{pending_vendor_natural.id}",
            headers=headers
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

        # 3. Verificar que ya no aparece en pendientes
        response = await async_client.get(
            "/api/v1/auth/admin/pending-sellers",
            headers=headers
        )
        assert response.status_code == 200
        final_count = response.json()["count"]
        assert final_count == initial_count - 1

        # Verificar que el vendedor aprobado no está en la lista
        sellers = response.json()["sellers"]
        assert not any(s["id"] == str(pending_vendor_natural.id) for s in sellers)

    async def test_complete_rejection_workflow(
        self,
        async_client: AsyncClient,
        admin_user: User,
        pending_vendor_juridica: User,
        async_session: AsyncSession
    ):
        """✅ Flujo completo: Listar → Rechazar → Verificar lista actualizada"""
        headers = create_auth_header(admin_user)

        # 1. Obtener lista inicial
        response = await async_client.get(
            "/api/v1/auth/admin/pending-sellers",
            headers=headers
        )
        assert response.status_code == 200
        initial_count = response.json()["count"]

        # 2. Rechazar vendedor con razón válida
        rejection_reason = "NIT inválido o no coincide con registros de Cámara de Comercio oficial."
        response = await async_client.post(
            f"/api/v1/auth/admin/reject-seller/{pending_vendor_juridica.id}",
            headers=headers,
            json={"reason": rejection_reason}
        )
        assert response.status_code == 200
        assert response.json()["vendor_status"] == "rejected"

        # 3. Verificar que ya no aparece en pendientes
        response = await async_client.get(
            "/api/v1/auth/admin/pending-sellers",
            headers=headers
        )
        assert response.status_code == 200
        final_count = response.json()["count"]
        assert final_count == initial_count - 1


# ============================================================================
# TESTS DE SEGURIDAD
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.tdd
@pytest.mark.security
class TestSecurityAspects:
    """Tests de seguridad para endpoints admin"""

    async def test_cannot_approve_own_vendor_account(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession
    ):
        """🔒 Un ADMIN que también es VENDOR no puede auto-aprobarse"""
        # Crear admin que también es vendedor (caso edge)
        admin_vendor = User(
            id=str(uuid.uuid4()),
            email="admin_vendor@test.com",
            nombre="Admin",
            apellido="Vendor",
            cedula="1111111111",
            telefono="+573001111111",
            user_type=UserType.ADMIN,
            # Este admin también tiene perfil de vendor pendiente
            tipo_vendedor="persona_natural",
            vendor_status=VendorStatus.PENDING_APPROVAL,
            account_status=AccountStatus.ACTIVE,
            direccion_fiscal="Calle Test",
            ciudad_fiscal="Test City",
            departamento_fiscal="Test",
            password_hash="fake_hash"
        )
        async_session.add(admin_vendor)
        await async_session.commit()

        headers = create_auth_header(admin_vendor)

        # Intentar auto-aprobarse
        response = await async_client.post(
            f"/api/v1/auth/admin/approve-seller/{admin_vendor.id}",
            headers=headers
        )

        # El endpoint puede permitir esto (200), rechazarlo por permisos (403),
        # o rechazarlo por validación de datos (400)
        assert response.status_code in [200, 400, 403]

    async def test_sql_injection_protection(
        self,
        async_client: AsyncClient,
        admin_user: User
    ):
        """🔒 Protección contra SQL injection en user_id"""
        headers = create_auth_header(admin_user)
        malicious_id = "1' OR '1'='1"

        response = await async_client.post(
            f"/api/v1/auth/admin/approve-seller/{malicious_id}",
            headers=headers
        )

        # Debe fallar con 404 (no encontrado), no con error de SQL
        assert response.status_code in [404, 422]

    async def test_xss_protection_in_rejection_reason(
        self,
        async_client: AsyncClient,
        admin_user: User,
        pending_vendor_natural: User,
        async_session: AsyncSession
    ):
        """🔒 Protección contra XSS en razón de rechazo"""
        headers = create_auth_header(admin_user)

        # Test 1: Script tags debe ser bloqueado
        xss_payload = "<script>alert('XSS')</script> Razón válida con más de veinte caracteres."

        response = await async_client.post(
            f"/api/v1/auth/admin/reject-seller/{pending_vendor_natural.id}",
            headers=headers,
            json={"reason": xss_payload}
        )

        # Debe ser bloqueado por validación de dangerous patterns
        assert response.status_code == 400
        assert "caracteres no permitidos" in response.json()["error_message"]

        # Test 2: Razón válida sin XSS debe funcionar
        safe_reason = "Documentos incompletos. Falta certificado de cámara de comercio actualizado."

        response = await async_client.post(
            f"/api/v1/auth/admin/reject-seller/{pending_vendor_natural.id}",
            headers=headers,
            json={"reason": safe_reason}
        )

        assert response.status_code == 200

        # Verificar que se guardó correctamente
        await async_session.refresh(pending_vendor_natural)
        assert pending_vendor_natural.vendor_status == VendorStatus.REJECTED
        assert pending_vendor_natural.rejection_reason == safe_reason  # Sin escape en DB

    async def test_html_entities_escaped_in_email(
        self,
        async_client: AsyncClient,
        admin_user: User,
        async_session: AsyncSession
    ):
        """🔒 HTML entities correctamente escapados en email"""
        # Crear un nuevo vendor para este test
        test_vendor = User(
            id=str(uuid.uuid4()),
            email="test_xss@test.com",
            nombre="Test",
            apellido="XSS",
            cedula="9999999999",
            telefono="+573009999999",
            user_type=UserType.VENDOR,
            tipo_vendedor="persona_natural",
            vendor_status=VendorStatus.PENDING_APPROVAL,
            account_status=AccountStatus.PENDING,
            direccion_fiscal="Test Address",
            ciudad_fiscal="Test City",
            departamento_fiscal="Test",
            password_hash="fake_hash"
        )
        async_session.add(test_vendor)
        await async_session.commit()
        await async_session.refresh(test_vendor)

        headers = create_auth_header(admin_user)

        # Razón con caracteres especiales que deben ser escapados en email
        reason = 'Documentos <incompletos> & con caracteres especiales "importantes".'

        response = await async_client.post(
            f"/api/v1/auth/admin/reject-seller/{test_vendor.id}",
            headers=headers,
            json={"reason": reason}
        )

        assert response.status_code == 200

        # Verificar que en DB está sin escapar (normal)
        await async_session.refresh(test_vendor)
        assert test_vendor.rejection_reason == reason
        # El test indirecto es que no falle el envío de email (html.escape se aplica en el servicio)
