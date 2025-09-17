# 💰 TODO MÓDULO 5: PAYMENT SYSTEM ENTERPRISE

**Base Compatible**: TODO_CONFIGURACION_BASE_ENTERPRISE.md ✅
**Dependencias**: Orders ✅, Users ✅, Database Architecture ✅
**Tiempo Estimado**: 16 horas (10h backend + 6h frontend)
**Prioridad**: 🔴 CRÍTICA - Revenue Critical Module

---

## 🎯 OBJETIVO DEL MÓDULO
Sistema avanzado de pagos con múltiples gateways, comisiones dinámicas, payouts automáticos para vendors, y control total del SUPERUSUARIO sobre todas las transacciones financieras.

---

## 🗄️ BACKEND - DATABASE & MODELS (5 horas)

### 5.1 PaymentGateway Múltiples (2h)
```python
# app/models/payment.py - EXTENDER MODELOS EXISTENTES
class PaymentGateway(BaseModel):
    id: int = Field(primary_key=True)
    name: str  # "wompi", "payu", "stripe", "pse"
    display_name: str
    is_active: bool = Field(default=True)
    config: JSON  # Configuraciones específicas del gateway
    supported_methods: JSON  # ["credit_card", "debit_card", "pse"]
    commission_rate: decimal = Field(default=0.0)
    processing_time: int = Field(default=0)  # minutos

class Payment(BaseModel):
    # CAMPOS EXISTENTES (mantener)
    id: int = Field(primary_key=True)
    order_id: FK to Order
    amount: decimal
    status: PaymentStatus
    created_at: datetime

    # NUEVOS CAMPOS ENTERPRISE
    payment_method: str
    gateway_id: FK to PaymentGateway
    gateway_transaction_id: str = Field(unique=True)
    gateway_response: JSON  # Respuesta completa del gateway

    # Comisiones y Splits
    platform_commission: decimal = Field(default=0.0)
    gateway_commission: decimal = Field(default=0.0)
    vendor_payout: decimal = Field(default=0.0)
    commission_rate_applied: decimal = Field(default=0.0)

    # Control Enterprise
    processed_by: FK to User = Field(nullable=True)
    approved_by: FK to User = Field(nullable=True)  # Para pagos manuales

    # Metadata
    payment_metadata: JSON = Field(default=dict)
```

### 5.2 CommissionCalculator (1.5h)
```python
class Commission(BaseModel):
    id: int = Field(primary_key=True)
    vendor_id: FK to User
    order_id: FK to Order = Field(nullable=True)
    commission_type: str  # "order", "subscription", "manual"
    base_amount: decimal
    commission_rate: decimal
    commission_amount: decimal
    status: str = Field(default="pending")  # pending, calculated, paid
    period_start: date
    period_end: date
    calculated_by: FK to User = Field(nullable=True)
    paid_at: datetime = Field(nullable=True)

class PayoutSchedule(BaseModel):
    id: int = Field(primary_key=True)
    vendor_id: FK to User
    total_amount: decimal
    commission_ids: JSON  # Lista de commission IDs incluidas
    payout_method: str  # "bank_transfer", "digital_wallet"
    bank_details: JSON = Field(nullable=True)
    status: str = Field(default="scheduled")
    scheduled_date: date
    processed_date: date = Field(nullable=True)
    reference_number: str = Field(nullable=True)
```

### 5.3 PaymentDispute (1h)
```python
class PaymentDispute(BaseModel):
    id: int = Field(primary_key=True)
    payment_id: FK to Payment
    dispute_type: str  # "chargeback", "refund_request", "fraud"
    amount_disputed: decimal
    reason: text
    evidence: JSON = Field(default=list)
    status: str = Field(default="open")
    resolution: text = Field(nullable=True)
    resolved_by: FK to User = Field(nullable=True)
    resolved_at: datetime = Field(nullable=True)
```

### 5.4 FinancialReports (0.5h)
```python
class FinancialReport(BaseModel):
    id: int = Field(primary_key=True)
    report_type: str  # "daily_revenue", "vendor_payouts", "commission_summary"
    report_period: str
    report_data: JSON
    generated_by: FK to User
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    file_url: str = Field(nullable=True)
```

---

## 🔌 BACKEND - SERVICES & APIS (5 horas)

### 5.5 PaymentProcessor Service (2.5h)
```python
# app/services/payment_processor_service.py
class PaymentProcessorService:
    def process_payment_enterprise(
        self,
        order: Order,
        payment_method: str,
        gateway: str = "wompi",
        auto_calculate_commission: bool = True
    ):
        """Procesar pago con cálculo automático de comisiones"""

        # Seleccionar gateway óptimo
        gateway_config = self.get_optimal_gateway(payment_method, order.total_amount)

        # Calcular comisiones
        commission_data = self.calculate_commissions(order, gateway_config)

        # Procesar pago
        payment_result = self.process_with_gateway(order, gateway_config, payment_method)

        # Crear registro de pago
        payment = Payment(
            order_id=order.id,
            amount=order.total_amount,
            payment_method=payment_method,
            gateway_id=gateway_config.id,
            gateway_transaction_id=payment_result.transaction_id,
            platform_commission=commission_data.platform_commission,
            gateway_commission=commission_data.gateway_commission,
            vendor_payout=commission_data.vendor_payout,
            commission_rate_applied=commission_data.rate,
            status="completed" if payment_result.success else "failed"
        )

        db.add(payment)

        # Si es exitoso, programar payout
        if payment_result.success and auto_calculate_commission:
            self.schedule_vendor_payout(order.vendor_id, commission_data.vendor_payout)

        db.commit()
        return payment

    def bulk_process_payouts(self, payout_ids: List[int], processed_by: User):
        """SUPERUSER puede procesar payouts masivamente"""
        if processed_by.user_type != UserType.SUPERUSER:
            raise PermissionDenied("Only SUPERUSER can bulk process payouts")

        results = {"success": [], "failed": []}

        for payout_id in payout_ids:
            try:
                result = self.process_vendor_payout(payout_id)
                results["success"].append(result)
            except Exception as e:
                results["failed"].append({"payout_id": payout_id, "error": str(e)})

        return results
```

### 5.6 CommissionService (1.5h)
```python
class CommissionService:
    def calculate_dynamic_commission(
        self,
        vendor: User,
        order_amount: decimal,
        product_category: str = None
    ):
        """Calcular comisión dinámica basada en múltiples factores"""

        base_rate = 0.10  # 10% base

        # Factores de ajuste
        volume_discount = self.get_volume_discount(vendor.id)
        category_adjustment = self.get_category_adjustment(product_category)
        performance_bonus = self.get_performance_bonus(vendor.id)

        final_rate = base_rate - volume_discount + category_adjustment - performance_bonus
        final_rate = max(0.05, min(0.15, final_rate))  # Entre 5% y 15%

        return {
            "rate": final_rate,
            "base_rate": base_rate,
            "adjustments": {
                "volume_discount": volume_discount,
                "category_adjustment": category_adjustment,
                "performance_bonus": performance_bonus
            },
            "commission_amount": order_amount * final_rate
        }

    def get_vendor_earnings_report(self, vendor_id: int, period: str = "30d"):
        """Reporte de ganancias del vendor"""
        return {
            "total_sales": self.calculate_vendor_sales(vendor_id, period),
            "total_commissions": self.calculate_vendor_commissions(vendor_id, period),
            "pending_payouts": self.get_pending_payouts(vendor_id),
            "paid_out": self.get_paid_amounts(vendor_id, period),
            "projected_earnings": self.calculate_projected_earnings(vendor_id)
        }
```

### 5.7 Payment APIs Enterprise (1h)
```python
# app/api/v1/endpoints/payments.py
@router.get("/superuser/payments/all")
@require_role([UserType.SUPERUSER])
async def get_all_payments():
    """SUPERUSER ve todos los pagos"""
    pass

@router.post("/superuser/payments/bulk-process")
@require_role([UserType.SUPERUSER])
async def bulk_process_payments():
    """Procesamiento masivo de pagos"""
    pass

@router.get("/superuser/finances/dashboard")
@require_role([UserType.SUPERUSER])
async def get_financial_dashboard():
    """Dashboard financiero completo"""
    pass

@router.get("/vendor/earnings")
@require_role([UserType.VENDOR])
async def get_vendor_earnings():
    """Earnings del vendor"""
    pass
```

---

## ⚛️ FRONTEND - COMPONENTS & INTERFACES (6 horas)

### 5.8 PaymentDashboard SUPERUSER (2.5h)
```jsx
// frontend/src/components/superuser/PaymentDashboard.tsx
const PaymentDashboard = () => {
  return (
    <div className="space-y-6">
      {/* Métricas financieras */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <FinancialMetricCard
          title="Revenue Hoy"
          value={formatCurrency(revenueToday)}
          change={revenueChange}
          icon={DollarSign}
        />
        <FinancialMetricCard
          title="Comisiones Generadas"
          value={formatCurrency(commissionsToday)}
          change={commissionChange}
          icon={Percent}
        />
        <FinancialMetricCard
          title="Payouts Pendientes"
          value={formatCurrency(pendingPayouts)}
          change={payoutChange}
          icon={Clock}
        />
        <FinancialMetricCard
          title="Disputas Activas"
          value={activeDisputes}
          change={disputeChange}
          icon={AlertCircle}
        />
      </div>

      {/* Gráficos financieros */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RevenueChart data={revenueData} />
        <CommissionChart data={commissionData} />
      </div>

      {/* Tablas de transacciones */}
      <PaymentTransactionTable />
      <PendingPayoutsTable />
    </div>
  );
};
```

### 5.9 VendorEarningsInterface (2h)
```jsx
// frontend/src/components/vendor/VendorEarningsInterface.tsx
const VendorEarningsInterface = () => {
  return (
    <div className="space-y-6">
      {/* Resumen de earnings */}
      <EarningsSummaryCard />

      {/* Historial de comisiones */}
      <CommissionHistoryTable />

      {/* Próximos payouts */}
      <UpcomingPayoutsCard />

      {/* Gráfico de earnings */}
      <EarningsChart />
    </div>
  );
};
```

### 5.10 PaymentMethodManager (1.5h)
```jsx
// frontend/src/components/ui/PaymentMethodManager.tsx
const PaymentMethodManager = ({ userRole }) => {
  if (userRole === 'SUPERUSER') {
    return <SuperuserPaymentConfig />;
  }

  return <UserPaymentMethods />;
};
```

---

## 📊 INTEGRACIÓN CON SISTEMA BASE

### Compatible con TODO_CONFIGURACION_BASE_ENTERPRISE.md:
✅ **Database Architecture**: Extiende payment models existentes
✅ **API Structure**: Sigue convenciones enterprise
✅ **Security**: Manejo seguro de datos financieros
✅ **Error Handling**: Compatible con error system

### Conecta con módulos:
- Orders → Processing de pagos de órdenes
- Users → Gestión de métodos de pago de usuarios
- Analytics → Métricas financieras y reportes
- Notifications → Alertas de pagos y comisiones

---

**🔗 MÓDULO COMPATIBLE CON ENTERPRISE BASE**
**💰 SISTEMA COMPLETO DE PAGOS ENTERPRISE**
**⏱️ 16 HORAS IMPLEMENTACIÓN COORDINADA**