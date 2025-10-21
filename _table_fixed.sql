                                            Table "public.users"
           Column           |            Type             | Collation | Nullable |         Default          
----------------------------+-----------------------------+-----------+----------+--------------------------
 id                         | character varying(36)       |           | not null | 
 banco                      | character varying(100)      |           |          | 
 tipo_cuenta                | character varying(20)       |           |          | 
 numero_cuenta              | character varying(50)       |           |          | 
 reset_token                | character varying(100)      |           |          | 
 reset_token_expires_at     | timestamp with time zone    |           |          | 
 reset_attempts             | integer                     |           | not null | 
 last_reset_request         | timestamp with time zone    |           |          | 
 google_id                  | character varying(100)      |           |          | 
 google_email               | character varying(255)      |           |          | 
 google_name                | character varying(200)      |           |          | 
 google_picture             | character varying(500)      |           |          | 
 google_verified_email      | boolean                     |           | not null | 
 oauth_provider             | character varying(50)       |           |          | 
 oauth_linked_at            | timestamp with time zone    |           |          | 
 email                      | character varying(255)      |           | not null | 
 password_hash              | character varying(255)      |           | not null | 
 nombre                     | character varying(100)      |           |          | 
 apellido                   | character varying(100)      |           |          | 
 user_type                  | usertype                    |           | not null | 
 vendor_status              | vendorstatus                |           |          | 
 is_active                  | boolean                     |           | not null | 
 is_verified                | boolean                     |           | not null | false
 cedula                     | character varying(20)       |           |          | 
 telefono                   | character varying(20)       |           |          | 
 ciudad                     | character varying(100)      |           |          | 
 empresa                    | character varying(200)      |           |          | 
 direccion                  | character varying(300)      |           |          | 
 email_verified             | boolean                     |           | not null | 
 phone_verified             | boolean                     |           | not null | 
 otp_secret                 | character varying(6)        |           |          | 
 otp_expires_at             | timestamp with time zone    |           |          | 
 otp_attempts               | integer                     |           | not null | 
 otp_type                   | character varying(10)       |           |          | 
 last_otp_sent              | timestamp with time zone    |           |          | 
 security_clearance_level   | integer                     |           | not null | 
 department_id              | character varying(100)      |           |          | 
 employee_id                | character varying(50)       |           |          | 
 performance_score          | integer                     |           | not null | 
 failed_login_attempts      | integer                     |           | not null | 
 account_locked_until       | timestamp with time zone    |           |          | 
 force_password_change      | boolean                     |           | not null | 
 last_login                 | timestamp with time zone    |           |          | 
 updated_at                 | timestamp with time zone    |           | not null | now()
 avatar_url                 | character varying(500)      |           |          | 
 business_name              | character varying(200)      |           |          | 
 business_description       | text                        |           |          | 
 website_url                | character varying(500)      |           |          | 
 social_media_links         | json                        |           |          | 
 business_hours             | json                        |           |          | 
 shipping_policy            | text                        |           |          | 
 return_policy              | text                        |           |          | 
 notification_preferences   | json                        |           |          | 
 bank_name                  | character varying(100)      |           |          | 
 account_holder_name        | character varying(200)      |           |          | 
 account_number             | character varying(50)       |           |          | 
 created_at                 | timestamp without time zone |           | not null | CURRENT_TIMESTAMP
 deleted_at                 | timestamp without time zone |           |          | 
 permissions                | json                        |           |          | '[]'::json
 account_status             | accountstatus               |           |          | 'PENDING'::accountstatus
 razon_social               | character varying(200)      |           |          | 
 nombre_comercial           | character varying(200)      |           |          | 
 nit                        | character varying(20)       |           |          | 
 representante_legal        | character varying(100)      |           |          | 
 cedula_representante       | character varying(20)       |           |          | 
 email_representante        | character varying(255)      |           |          | 
 telefono_empresa           | character varying(20)       |           |          | 
 direccion_fiscal           | character varying(300)      |           |          | 
 ciudad_fiscal              | character varying(100)      |           |          | 
 departamento_fiscal        | character varying(100)      |           |          | 
 departamento               | character varying(100)      |           |          | 
 tipo_vendedor              | character varying(20)       |           |          | 
 codigo_postal              | character varying(10)       |           |          | 
 email_verification_token   | character varying(100)      |           |          | 
 email_verification_expires | timestamp without time zone |           |          | 
Indexes:
    "users_pkey" PRIMARY KEY, btree (id)
    "idx_users_email_verification_token" btree (email_verification_token) WHERE email_verification_token IS NOT NULL
    "idx_users_nit" btree (nit) WHERE nit IS NOT NULL
    "idx_users_tipo_vendedor" btree (tipo_vendedor) WHERE tipo_vendedor IS NOT NULL
    "idx_users_vendor_type_status" btree (user_type, vendor_status, tipo_vendedor) WHERE user_type = 'VENDOR'::usertype
    "ix_user_active_created" btree (is_active, created_at)
    "ix_user_created_type" btree (created_at, user_type)
    "ix_user_email_active" btree (email, is_active)
    "ix_user_email_verified" btree (email_verified)
    "ix_user_google_id" btree (google_id)
    "ix_user_oauth_provider" btree (oauth_provider)
    "ix_user_otp_expires" btree (otp_expires_at)
    "ix_user_type_active" btree (user_type, is_active)
    "ix_users_cedula" UNIQUE, btree (cedula)
    "ix_users_email" UNIQUE, btree (email)
    "ix_users_google_id" UNIQUE, btree (google_id)
    "ix_users_id" btree (id)
    "ix_users_reset_token" btree (reset_token)
    "ix_users_reset_token_expires_at" btree (reset_token_expires_at)
    "users_nit_key" UNIQUE CONSTRAINT, btree (nit)
Referenced by:
    TABLE "admin_activity_logs" CONSTRAINT "admin_activity_logs_admin_user_id_fkey" FOREIGN KEY (admin_user_id) REFERENCES users(id) ON DELETE SET NULL
    TABLE "admin_user_permissions" CONSTRAINT "admin_user_permissions_granted_by_id_fkey" FOREIGN KEY (granted_by_id) REFERENCES users(id)
    TABLE "admin_user_permissions" CONSTRAINT "admin_user_permissions_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id)
    TABLE "commission_disputes" CONSTRAINT "commission_disputes_usuario_id_fkey" FOREIGN KEY (usuario_id) REFERENCES users(id)
    TABLE "commissions" CONSTRAINT "commissions_approved_by_id_fkey" FOREIGN KEY (approved_by_id) REFERENCES users(id)
    TABLE "commissions" CONSTRAINT "commissions_vendor_id_fkey" FOREIGN KEY (vendor_id) REFERENCES users(id) ON DELETE CASCADE
    TABLE "discrepancy_reports" CONSTRAINT "discrepancy_reports_generated_by_id_fkey" FOREIGN KEY (generated_by_id) REFERENCES users(id)
    TABLE "incoming_product_queue" CONSTRAINT "incoming_product_queue_assigned_to_fkey" FOREIGN KEY (assigned_to) REFERENCES users(id)
    TABLE "incoming_product_queue" CONSTRAINT "incoming_product_queue_vendor_id_fkey" FOREIGN KEY (vendor_id) REFERENCES users(id)
    TABLE "inventory_audits" CONSTRAINT "inventory_audits_auditor_id_fkey" FOREIGN KEY (auditor_id) REFERENCES users(id)
    TABLE "inventory" CONSTRAINT "inventory_updated_by_id_fkey" FOREIGN KEY (updated_by_id) REFERENCES users(id)
    TABLE "movement_tracker" CONSTRAINT "movement_tracker_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id)
    TABLE "movimientos_stock" CONSTRAINT "movimientos_stock_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id)
    TABLE "orders" CONSTRAINT "orders_buyer_id_fkey" FOREIGN KEY (buyer_id) REFERENCES users(id)
    TABLE "payment_methods" CONSTRAINT "payment_methods_buyer_id_fkey" FOREIGN KEY (buyer_id) REFERENCES users(id)
    TABLE "payout_history" CONSTRAINT "payout_history_usuario_responsable_fkey" FOREIGN KEY (usuario_responsable) REFERENCES users(id)
    TABLE "payout_requests" CONSTRAINT "payout_requests_vendedor_id_fkey" FOREIGN KEY (vendedor_id) REFERENCES users(id)
    TABLE "product_categories" CONSTRAINT "product_categories_assigned_by_id_fkey" FOREIGN KEY (assigned_by_id) REFERENCES users(id)
    TABLE "products" CONSTRAINT "products_created_by_id_fkey" FOREIGN KEY (created_by_id) REFERENCES users(id)
    TABLE "products" CONSTRAINT "products_updated_by_id_fkey" FOREIGN KEY (updated_by_id) REFERENCES users(id)
    TABLE "products" CONSTRAINT "products_vendedor_id_fkey" FOREIGN KEY (vendedor_id) REFERENCES users(id)
    TABLE "storages" CONSTRAINT "storages_vendedor_id_fkey" FOREIGN KEY (vendedor_id) REFERENCES users(id)
    TABLE "transactions" CONSTRAINT "transactions_comprador_id_fkey" FOREIGN KEY (comprador_id) REFERENCES users(id)
    TABLE "transactions" CONSTRAINT "transactions_vendedor_id_fkey" FOREIGN KEY (vendedor_id) REFERENCES users(id)
    TABLE "vendor_audit_logs" CONSTRAINT "vendor_audit_logs_admin_id_fkey" FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE
    TABLE "vendor_audit_logs" CONSTRAINT "vendor_audit_logs_vendor_id_fkey" FOREIGN KEY (vendor_id) REFERENCES users(id) ON DELETE CASCADE
    TABLE "vendor_documents" CONSTRAINT "vendor_documents_vendor_id_fkey" FOREIGN KEY (vendor_id) REFERENCES users(id)
    TABLE "vendor_documents" CONSTRAINT "vendor_documents_verified_by_fkey" FOREIGN KEY (verified_by) REFERENCES users(id)
    TABLE "vendor_notes" CONSTRAINT "vendor_notes_admin_id_fkey" FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE
    TABLE "vendor_notes" CONSTRAINT "vendor_notes_vendor_id_fkey" FOREIGN KEY (vendor_id) REFERENCES users(id) ON DELETE CASCADE

