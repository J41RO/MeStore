# ============================================================================
# ENDPOINT MULTI-TIPO: BUYER, VENDOR NATURAL, VENDOR JURÍDICA
# ============================================================================
# Este archivo contiene el endpoint /register-multi-type para registro
# condicional basado en tipo de usuario.
# Agregar al final de auth.py después de línea 1568
# ============================================================================

"""
@router.post("/register-multi-type", response_model=MultiTypeRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_multi_type(
    user_data: Union[BuyerRegistrationData, VendorNaturalRegistrationData, VendorJuridicaRegistrationData],
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> MultiTypeRegistrationResponse:
    '''
    Registro multi-tipo para BUYER, VENDOR Natural y VENDOR Jurídica.

    Detecta automáticamente el tipo de usuario basado en campos presentes:
    - Si tiene `nit` → VENDOR Persona Jurídica
    - Si tiene `cedula` y `direccion_fiscal` → VENDOR Persona Natural
    - Si no tiene campos de vendor → BUYER

    Flujos por tipo:

    BUYER:
    - user_type: BUYER
    - account_status: PENDING → ACTIVE (después de verificar email + SMS)
    - vendor_status: None
    - Activación inmediata después de verificación

    VENDOR Persona Natural:
    - user_type: VENDOR
    - account_status: PENDING
    - vendor_status: DRAFT (requiere aprobación admin)
    - tipo_vendedor: "persona_natural"
    - Requiere verificación email/SMS + aprobación administrativa

    VENDOR Persona Jurídica:
    - user_type: VENDOR
    - account_status: PENDING
    - vendor_status: PENDING_DOCUMENTS (requiere documentos)
    - tipo_vendedor: "persona_juridica"
    - Requiere verificación email/SMS + documentos + aprobación

    Returns:
        MultiTypeRegistrationResponse con user_id, estados, y next_steps
    '''

    try:
        # ========================================================================
        # 1. DETECTAR TIPO DE USUARIO
        # ========================================================================
        logger.info(f"🔄 Inicio de registro multi-tipo")
        logger.info(f"📝 Datos recibidos: email={user_data.email}")

        # Detectar tipo basado en campos presentes
        is_juridica = hasattr(user_data, 'nit') and user_data.nit
        is_natural = hasattr(user_data, 'cedula') and user_data.cedula and hasattr(user_data, 'direccion_fiscal')
        is_buyer = not is_juridica and not is_natural

        if is_juridica:
            user_type = UserType.VENDOR
            vendor_type = "persona_juridica"
            logger.info(f"🏢 Tipo detectado: VENDOR Persona Jurídica")
        elif is_natural:
            user_type = UserType.VENDOR
            vendor_type = "persona_natural"
            logger.info(f"👤 Tipo detectado: VENDOR Persona Natural")
        else:
            user_type = UserType.BUYER
            vendor_type = None
            logger.info(f"🛒 Tipo detectado: BUYER")

        # ========================================================================
        # 2. VALIDAR UNICIDAD DE EMAIL Y TELÉFONO
        # ========================================================================
        logger.info(f"🔍 Verificando unicidad de email: {user_data.email}")
        existing_user = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if existing_user.scalar_one_or_none():
            logger.warning(f"⚠️ Email ya registrado: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está registrado. Por favor usa otro correo o inicia sesión."
            )
        logger.info(f"✅ Email disponible")

        # Obtener teléfono del schema correcto
        telefono = getattr(user_data, 'telefono', None) or getattr(user_data, 'telefono_empresa', None)

        if telefono:
            logger.info(f"🔍 Verificando unicidad de teléfono")
            existing_phone = await db.execute(
                select(User).where(User.telefono == telefono)
            )
            if existing_phone.scalar_one_or_none():
                logger.warning(f"⚠️ Teléfono ya registrado")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El teléfono ya está registrado. Por favor usa otro número."
                )
            logger.info(f"✅ Teléfono disponible")

        # ========================================================================
        # 3. VALIDAR NIT ÚNICO (SOLO PERSONA JURÍDICA)
        # ========================================================================
        if is_juridica:
            logger.info(f"🔍 Verificando unicidad de NIT")
            existing_nit = await db.execute(
                select(User).where(User.nit == user_data.nit)
            )
            if existing_nit.scalar_one_or_none():
                logger.warning(f"⚠️ NIT ya registrado")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El NIT ya está registrado. Por favor verifica o inicia sesión."
                )
            logger.info(f"✅ NIT disponible")

        # ========================================================================
        # 4. CREAR USUARIO CON CAMPOS SEGÚN TIPO
        # ========================================================================
        logger.info(f"🔐 Generando hash de contraseña")
        password_hash = await get_password_hash(user_data.password)

        # Determinar estados según tipo
        if user_type == UserType.BUYER:
            account_status = AccountStatus.PENDING  # Se activa al verificar
            vendor_status = None
        else:  # VENDOR
            account_status = AccountStatus.PENDING
            vendor_status = VendorStatus.DRAFT if is_natural else VendorStatus.PENDING_DOCUMENTS

        logger.info(f"👤 Creando usuario con estados: account_status={account_status}, vendor_status={vendor_status}")

        # Crear usuario base
        new_user = User(
            email=user_data.email,
            password_hash=password_hash,
            user_type=user_type,
            account_status=account_status,
            vendor_status=vendor_status,
            tipo_vendedor=vendor_type,
            is_active=True,
            email_verified=False,
            phone_verified=False
        )

        # Agregar campos según tipo
        if is_buyer:
            # BUYER: campos básicos
            new_user.nombre = user_data.nombre
            new_user.apellido = getattr(user_data, 'apellido', None)
            new_user.telefono = user_data.telefono
            new_user.cedula = getattr(user_data, 'cedula', None)
            new_user.direccion = getattr(user_data, 'direccion', None)
            new_user.ciudad = getattr(user_data, 'ciudad', None)
            new_user.departamento = getattr(user_data, 'departamento', None)
            new_user.codigo_postal = getattr(user_data, 'codigo_postal', None)

        elif is_natural:
            # VENDOR NATURAL: persona física + fiscal
            new_user.nombre = user_data.nombre
            new_user.apellido = user_data.apellido
            new_user.telefono = user_data.telefono
            new_user.cedula = user_data.cedula
            new_user.direccion = user_data.direccion
            new_user.ciudad = user_data.ciudad
            new_user.departamento = user_data.departamento
            new_user.codigo_postal = getattr(user_data, 'codigo_postal', None)
            new_user.direccion_fiscal = user_data.direccion_fiscal
            new_user.ciudad_fiscal = user_data.ciudad_fiscal
            new_user.departamento_fiscal = user_data.departamento_fiscal

        else:  # is_juridica
            # VENDOR JURÍDICA: datos empresa + representante
            new_user.razon_social = user_data.razon_social
            new_user.nombre_comercial = user_data.nombre_comercial
            new_user.nit = user_data.nit
            new_user.representante_legal = user_data.representante_legal
            new_user.cedula_representante = user_data.cedula_representante
            new_user.email_representante = user_data.email_representante
            new_user.telefono = user_data.telefono_empresa
            new_user.telefono_empresa = user_data.telefono_empresa
            new_user.direccion_fiscal = user_data.direccion_fiscal
            new_user.ciudad_fiscal = user_data.ciudad_fiscal
            new_user.departamento_fiscal = user_data.departamento_fiscal
            new_user.codigo_postal = getattr(user_data, 'codigo_postal', None)
            # Nombre para display
            new_user.nombre = user_data.nombre_comercial

        db.add(new_user)
        logger.info(f"💾 Usuario agregado a sesión DB, ejecutando flush")
        await db.flush()
        logger.info(f"✅ Flush completado, user_id obtenido: {new_user.id}")

        # ========================================================================
        # 5. GENERAR TOKEN DE VERIFICACIÓN EMAIL (LINK)
        # ========================================================================
        logger.info(f"🎲 Generando token de verificación de email")
        email_token = secrets.token_urlsafe(32)
        new_user.email_verification_token = email_token
        new_user.email_verification_expires = datetime.utcnow() + timedelta(hours=24)
        logger.info(f"✅ Token generado (expira en 24h)")

        # ========================================================================
        # 6. COMMIT A BASE DE DATOS
        # ========================================================================
        logger.info(f"💾 Ejecutando commit a base de datos")
        await db.commit()
        await db.refresh(new_user)
        logger.info(f"✅ Usuario creado exitosamente", user_id=str(new_user.id))

        # ========================================================================
        # 7. ENVIAR EMAIL VERIFICACIÓN CON LINK (BACKGROUND)
        # ========================================================================
        logger.info(f"📧 Programando email de verificación con link")
        from app.core.config import settings
        verification_link = f"{settings.FRONTEND_URL}/verify-email?token={email_token}"

        background_tasks.add_task(
            send_verification_email,
            new_user.email,
            email_token,
            new_user.nombre or new_user.razon_social,
            verification_link
        )
        logger.info(f"✅ Email programado")

        # ========================================================================
        # 8. ENVIAR SMS VERIFICACIÓN (TWILIO VERIFY)
        # ========================================================================
        if telefono:
            try:
                logger.info(f"📱 Enviando SMS verification con Twilio")
                sms_service = SMSService()
                sms_result = await sms_service.send_verification_code(
                    phone_number=telefono,
                    channel="sms"
                )
                logger.info(f"✅ SMS enviado", status=sms_result.get('status'))
            except Exception as sms_error:
                logger.error(f"❌ Error SMS: {str(sms_error)}", exc_info=True)
                # No fallar registro si SMS falla

        # ========================================================================
        # 9. PREPARAR NEXT_STEPS SEGÚN TIPO
        # ========================================================================
        if user_type == UserType.BUYER:
            next_steps = [
                "Verifica tu email haciendo clic en el enlace enviado",
                "Ingresa el código SMS de 6 dígitos",
                "¡Empieza a comprar! Tu cuenta se activará automáticamente"
            ]
        elif vendor_type == "persona_natural":
            next_steps = [
                "Verifica tu email haciendo clic en el enlace enviado",
                "Ingresa el código SMS de 6 dígitos",
                "Tu solicitud será revisada por nuestro equipo",
                "Recibirás notificación de aprobación en 24-48 horas"
            ]
        else:  # persona_juridica
            next_steps = [
                "Verifica tu email haciendo clic en el enlace enviado",
                "Ingresa el código SMS de 6 dígitos",
                "Sube los documentos requeridos (Cámara de Comercio, RUT)",
                "Espera la revisión y aprobación de tu cuenta empresarial"
            ]

        # ========================================================================
        # 10. RETORNAR RESPUESTA
        # ========================================================================
        logger.info(f"✅ Registro completado exitosamente")

        return MultiTypeRegistrationResponse(
            success=True,
            message=f"Registro exitoso como {vendor_type or 'comprador'}. Por favor verifica tu email y teléfono.",
            user_id=str(new_user.id),
            email=new_user.email,
            user_type=user_type.value,
            vendor_type=vendor_type,
            account_status=account_status.value,
            vendor_status=vendor_status.value if vendor_status else None,
            requires_approval=(user_type == UserType.VENDOR),
            next_steps=next_steps
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ ERROR CRÍTICO en register_multi_type: {str(e)}", exc_info=True)

        # Rollback
        try:
            await db.rollback()
            logger.info(f"✅ Rollback completado")
        except Exception as rollback_error:
            logger.error(f"❌ Error en rollback: {str(rollback_error)}", exc_info=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando registro: {type(e).__name__} - {str(e)}"
        )
"""
