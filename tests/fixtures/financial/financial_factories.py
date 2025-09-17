# tests/fixtures/financial/financial_factories.py
# CRITICAL: Financial Test Data Factories for Commission and Transaction Testing
# PRIORITY: Reliable test data generation for financial calculations

import factory
import logging
import asyncio
from decimal import Decimal
from datetime import datetime, timedelta
from uuid import uuid4
from faker import Faker

fake = Faker()

from sqlalchemy.orm import Session
from app.models.user import User, UserType
from app.models.order import Order, OrderStatus
from app.models.commission import Commission, CommissionStatus, CommissionType
from app.models.transaction import Transaction, EstadoTransaccion, TransactionType, MetodoPago
from app.models.product import Product
from app.models.inventory import Inventory

logger = logging.getLogger(__name__)


class BaseFinancialFactory(factory.Factory):
    """Base factory with common financial test configurations"""

    class Meta:
        abstract = True

    @classmethod
    def _setup_session(cls, session: Session):
        """Setup database session for factory"""
        cls._meta.sqlalchemy_session = session


# User Factories for Financial Testing

class BuyerUserFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating test buyer users"""

    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"

    id = factory.LazyFunction(uuid4)
    email = factory.Sequence(lambda n: f"buyer{n}@mestore-test.com")
    nombre = factory.Faker('first_name')
    apellido = factory.Faker('last_name')
    user_type = UserType.COMPRADOR
    is_active = True
    password_hash = "$2b$12$test.hash.for.financial.testing"
    is_verified = True
    telefono = factory.Faker('phone_number')
    ciudad = factory.Faker('city')
    created_at = factory.LazyFunction(datetime.now)


class VendorUserFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating test vendor users"""

    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"

    id = factory.LazyFunction(uuid4)
    email = factory.Sequence(lambda n: f"vendor{n}@mestore-test.com")
    nombre = factory.Faker('first_name')
    apellido = factory.Faker('last_name')
    user_type = UserType.VENDEDOR
    is_active = True
    password_hash = "$2b$12$test.hash.for.financial.testing"
    is_verified = True
    telefono = factory.Sequence(lambda n: f"300{n:07d}")
    ciudad = factory.Iterator(['Bogotá', 'Medellín', 'Cali', 'Barranquilla'])
    created_at = factory.LazyFunction(datetime.now)


class AdminUserFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating test admin users"""

    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"

    id = factory.LazyFunction(uuid4)
    email = factory.Sequence(lambda n: f"admin{n}@mestore-test.com")
    nombre = factory.Faker('first_name')
    apellido = factory.Faker('last_name')
    user_type = UserType.ADMIN
    is_active = True
    password_hash = "$2b$12$test.hash.for.financial.testing"
    is_verified = True
    created_at = factory.LazyFunction(datetime.now)


# Product and Inventory Factories

class ProductFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating test products"""

    class Meta:
        model = Product
        sqlalchemy_session_persistence = "commit"

    id = factory.LazyFunction(uuid4)
    sku = factory.Sequence(lambda n: f"SKU-{n:06d}")
    name = factory.Faker('word')
    description = factory.Faker('text', max_nb_chars=200)
    precio_venta = factory.LazyFunction(lambda: Decimal(str(fake.random_int(min=1000, max=500000))))
    precio_costo = factory.LazyFunction(lambda: Decimal(str(fake.random_int(min=500, max=400000))))
    categoria = factory.Iterator(['electronics', 'clothing', 'books', 'home', 'sports'])
    created_at = factory.LazyFunction(datetime.now)

    # Will be set by OrderItemFactory
    vendedor_id = None


class InventoryFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating test inventory items"""

    class Meta:
        model = Inventory
        sqlalchemy_session_persistence = "commit"

    id = factory.LazyFunction(uuid4)
    cantidad_disponible = factory.Faker('random_int', min=1, max=50)
    ubicacion = factory.Sequence(lambda n: f"TEST-LOC-{n:03d}")
    estado_calidad = factory.Iterator(['excellent', 'good', 'fair'])
    created_at = factory.LazyFunction(datetime.now)

    # Will be linked to product
    product_id = None


# Order Factories for Financial Testing

class OrderFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating test orders with financial calculations"""

    class Meta:
        model = Order
        sqlalchemy_session_persistence = "commit"

    id = factory.LazyFunction(uuid4)
    order_number = factory.Sequence(lambda n: f"ORD-TEST-{datetime.now().strftime('%Y%m%d')}-{n:04d}")
    status = OrderStatus.CONFIRMED  # Default to confirmed for commission calculation
    shipping_name = factory.Faker('name')
    shipping_phone = factory.Faker('phone_number')
    shipping_email = factory.Faker('email')
    shipping_address = factory.Faker('address')
    shipping_city = factory.Faker('city')
    shipping_state = factory.Faker('state')
    shipping_postal_code = factory.Faker('postcode')
    created_at = factory.LazyFunction(datetime.now)

    # Financial amounts - will be set based on items
    total_amount = factory.LazyFunction(lambda: Decimal("100000.00"))  # Default 100k COP

    # Foreign keys - will be set by tests
    buyer_id = None


class SmallOrderFactory(OrderFactory):
    """Factory for small value orders (< 50k COP)"""
    total_amount = factory.LazyFunction(lambda: Decimal(str(fake.random_int(min=10000, max=49999))))


class MediumOrderFactory(OrderFactory):
    """Factory for medium value orders (50k - 200k COP)"""
    total_amount = factory.LazyFunction(lambda: Decimal(str(fake.random_int(min=50000, max=200000))))


class LargeOrderFactory(OrderFactory):
    """Factory for large value orders (> 200k COP)"""
    total_amount = factory.LazyFunction(lambda: Decimal(str(fake.random_int(min=200001, max=2000000))))


class PendingOrderFactory(OrderFactory):
    """Factory for pending orders (not eligible for commission)"""
    status = OrderStatus.PENDING


class CancelledOrderFactory(OrderFactory):
    """Factory for cancelled orders"""
    status = OrderStatus.CANCELLED


# Commission Factories for Financial Testing

class CommissionFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating test commissions"""

    class Meta:
        model = Commission
        sqlalchemy_session_persistence = "commit"

    id = factory.LazyFunction(uuid4)
    commission_number = factory.Sequence(lambda n: f"COM-TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}-{n:03d}")
    commission_type = CommissionType.STANDARD
    status = CommissionStatus.PENDING
    currency = "COP"
    calculation_method = "automatic"

    # Financial calculations - will be computed based on order_amount and rate
    commission_rate = factory.LazyFunction(lambda: Decimal("0.05"))  # 5% default
    order_amount = factory.LazyFunction(lambda: Decimal("100000.00"))  # 100k COP default

    @factory.lazy_attribute
    def commission_amount(self):
        return self.order_amount * self.commission_rate

    @factory.lazy_attribute
    def vendor_amount(self):
        return self.order_amount - self.commission_amount

    @factory.lazy_attribute
    def platform_amount(self):
        return self.commission_amount

    notes = factory.LazyAttribute(lambda obj: f"Auto-generated test commission for order amount {obj.order_amount}")
    calculated_at = factory.LazyFunction(datetime.now)
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)

    # Foreign keys - will be set by tests
    order_id = None
    vendor_id = None
    transaction_id = None


class StandardCommissionFactory(CommissionFactory):
    """Factory for standard commission (5% rate)"""
    commission_type = CommissionType.STANDARD
    commission_rate = Decimal("0.05")


class PremiumCommissionFactory(CommissionFactory):
    """Factory for premium commission (3% rate)"""
    commission_type = CommissionType.PREMIUM
    commission_rate = Decimal("0.03")


class CategoryBasedCommissionFactory(CommissionFactory):
    """Factory for category-based commission (2% rate)"""
    commission_type = CommissionType.CATEGORY_BASED
    commission_rate = Decimal("0.02")


class ApprovedCommissionFactory(CommissionFactory):
    """Factory for approved commissions ready for payment"""
    status = CommissionStatus.APPROVED
    approved_at = factory.LazyFunction(datetime.now)
    approved_by = factory.LazyFunction(uuid4)


class PaidCommissionFactory(ApprovedCommissionFactory):
    """Factory for paid commissions"""
    status = CommissionStatus.PAID
    paid_at = factory.LazyFunction(datetime.now)


# Transaction Factories for Financial Testing

class TransactionFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating test transactions"""

    class Meta:
        model = Transaction
        sqlalchemy_session_persistence = "commit"

    id = factory.LazyFunction(uuid4)
    monto = factory.LazyFunction(lambda: Decimal(str(factory.Faker('random_int', min=1000, max=500000).generate())))
    metodo_pago = factory.Iterator([
        MetodoPago.EFECTIVO,
        MetodoPago.TARJETA_CREDITO,
        MetodoPago.TARJETA_DEBITO,
        MetodoPago.PSE
    ])
    estado = EstadoTransaccion.PENDIENTE
    transaction_type = TransactionType.COMISION
    referencia_externa = factory.Sequence(lambda n: f"TXN-TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}-{n:04d}")
    observaciones = "Test transaction generated by factory"
    created_at = factory.LazyFunction(datetime.now)

    # Financial amounts
    porcentaje_mestocker = factory.LazyFunction(lambda: Decimal("5.00"))  # 5% default

    @factory.lazy_attribute
    def monto_vendedor(self):
        return self.monto * (Decimal("100") - self.porcentaje_mestocker) / Decimal("100")

    # Foreign keys
    comprador_id = None
    vendedor_id = None
    inventory_id = None


class PendingTransactionFactory(TransactionFactory):
    """Factory for pending transactions"""
    estado = EstadoTransaccion.PENDIENTE


class ProcessingTransactionFactory(TransactionFactory):
    """Factory for processing transactions"""
    estado = EstadoTransaccion.PROCESANDO


class CompletedTransactionFactory(TransactionFactory):
    """Factory for completed transactions"""
    estado = EstadoTransaccion.COMPLETADA
    fecha_pago = factory.LazyFunction(datetime.now)
    referencia_pago = factory.Sequence(lambda n: f"PAY-TEST-{n:08d}")


class FailedTransactionFactory(TransactionFactory):
    """Factory for failed transactions"""
    estado = EstadoTransaccion.FALLIDA
    observaciones = "Transaction failed during processing - test scenario"


# Composite Factories for Complete Financial Scenarios

class FinancialScenarioFactory:
    """Factory for creating complete financial test scenarios"""

    def __init__(self, session):
        self.session = session
        self.is_async = hasattr(session, 'commit') and asyncio.iscoroutinefunction(session.commit)
        # Configure all factories to use this session
        BuyerUserFactory._meta.sqlalchemy_session = session
        VendorUserFactory._meta.sqlalchemy_session = session
        AdminUserFactory._meta.sqlalchemy_session = session
        OrderFactory._meta.sqlalchemy_session = session
        CommissionFactory._meta.sqlalchemy_session = session
        TransactionFactory._meta.sqlalchemy_session = session
        ProductFactory._meta.sqlalchemy_session = session

    async def _commit_session(self):
        """Async-safe commit method"""
        if self.is_async:
            await self.session.commit()
        else:
            self.session.commit()

    async def create_basic_order_scenario(self, order_amount: Decimal = None) -> dict:
        """Create a complete scenario with buyer, vendor, and confirmed order"""
        from app.models.user import User, UserType
        from app.models.order import Order, OrderStatus
        from app.models.product import Product
        from datetime import datetime

        # Add to session first to let database auto-generate IDs
        buyer = User(
            email=f"test_buyer_{uuid4().hex[:8]}@mestore-test.com",
            nombre=fake.first_name(),
            apellido=fake.last_name(),
            user_type=UserType.COMPRADOR,
            is_active=True,
            password_hash="$2b$12$test.hash.for.testing",
            is_verified=True,
            telefono=fake.phone_number(),
            ciudad=fake.city(),
            created_at=datetime.now()
        )

        vendor = User(
            email=f"test_vendor_{uuid4().hex[:8]}@mestore-test.com",
            nombre=fake.first_name(),
            apellido=fake.last_name(),
            user_type=UserType.VENDEDOR,
            is_active=True,
            password_hash="$2b$12$test.hash.for.testing",
            is_verified=True,
            telefono=f"300{fake.random_int(min=1000000, max=9999999)}",
            ciudad=fake.city(),
            created_at=datetime.now()
        )

        # Add users first and commit to get their IDs
        self.session.add(buyer)
        self.session.add(vendor)
        await self._commit_session()

        # Now create dependent objects with proper foreign keys
        product = Product(
            sku=f"SKU-{fake.random_int(min=100000, max=999999)}",
            name=fake.word(),
            description=fake.text(max_nb_chars=200),
            precio_venta=Decimal(str(fake.random_int(min=1000, max=500000))),
            precio_costo=Decimal(str(fake.random_int(min=500, max=400000))),
            categoria=fake.random_element(['electronics', 'clothing', 'books', 'home', 'sports']),
            vendedor_id=vendor.id,
            created_at=datetime.now()
        )

        order = Order(
            order_number=f"ORD-TEST-{datetime.now().strftime('%Y%m%d')}-{fake.random_int(min=1000, max=9999):04d}",
            buyer_id=hash(str(buyer.id)) % 2147483647,  # Convert UUID to int for FK compatibility
            total_amount=order_amount or Decimal("100000.00"),
            status=OrderStatus.CONFIRMED,
            shipping_name=fake.name(),
            shipping_phone=fake.phone_number(),
            shipping_email=fake.email(),
            shipping_address=fake.address(),
            shipping_city=fake.city(),
            shipping_state=fake.state(),
            shipping_postal_code=fake.postcode(),
            created_at=datetime.now()
        )

        # Add remaining objects
        self.session.add(product)
        self.session.add(order)
        await self._commit_session()

        return {
            'buyer': buyer,
            'vendor': vendor,
            'product': product,
            'order': order
        }

    async def create_commission_scenario(
        self,
        commission_type: CommissionType = CommissionType.STANDARD,
        order_amount: Decimal = None
    ) -> dict:
        """Create a complete commission scenario"""
        base_scenario = await self.create_basic_order_scenario(order_amount)

        from app.models.commission import Commission, CommissionStatus, CommissionType
        from datetime import datetime

        # Create commission manually for async compatibility
        commission_rate = Decimal("0.05")  # 5% default
        order_amount_decimal = base_scenario['order'].total_amount
        commission_amount = order_amount_decimal * commission_rate
        vendor_amount = order_amount_decimal - commission_amount

        commission = Commission(
            commission_number=f"COM-TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}-{fake.random_int(min=100, max=999):03d}",
            order_id=base_scenario['order'].id,
            vendor_id=base_scenario['vendor'].id,
            order_amount=order_amount_decimal,
            commission_rate=commission_rate,
            commission_amount=commission_amount,
            vendor_amount=vendor_amount,
            platform_amount=commission_amount,
            commission_type=commission_type,
            status=CommissionStatus.PENDING,
            currency="COP",
            calculation_method="automatic",
            calculated_at=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.session.add(commission)
        await self._commit_session()

        return {
            **base_scenario,
            'commission': commission
        }

    async def create_transaction_scenario(self) -> dict:
        """Create a complete transaction scenario with commission"""
        commission_scenario = await self.create_commission_scenario()

        # Approve the commission first
        commission = commission_scenario['commission']
        commission.status = CommissionStatus.APPROVED
        commission.approved_by = AdminUserFactory.create().id
        commission.approved_at = datetime.now()
        await self._commit_session()

        transaction = TransactionFactory.create(
            comprador_id=commission_scenario['buyer'].id,
            vendedor_id=commission_scenario['vendor'].id,
            monto=commission.vendor_amount,
            monto_vendedor=commission.vendor_amount,
            transaction_type=TransactionType.COMISION
        )

        # Link commission to transaction
        commission.transaction_id = transaction.id
        await self._commit_session()

        return {
            **commission_scenario,
            'transaction': transaction
        }

    def create_multi_vendor_scenario(self, vendor_count: int = 3) -> dict:
        """Create scenario with multiple vendors and orders"""
        buyer = BuyerUserFactory.create()
        vendors = [VendorUserFactory.create() for _ in range(vendor_count)]

        orders = []
        commissions = []

        for vendor in vendors:
            product = ProductFactory.create(vendedor_id=vendor.id)
            order = OrderFactory.create(
                buyer_id=buyer.id,
                status=OrderStatus.CONFIRMED
            )
            commission = CommissionFactory.create(
                order_id=order.id,
                vendor_id=vendor.id,
                order_amount=order.total_amount
            )

            orders.append(order)
            commissions.append(commission)

        return {
            'buyer': buyer,
            'vendors': vendors,
            'orders': orders,
            'commissions': commissions
        }

    def create_performance_test_data(self, count: int = 100) -> dict:
        """Create large dataset for performance testing"""
        logger.info(f"Creating performance test data: {count} records")

        buyers = [BuyerUserFactory.create() for _ in range(min(10, count // 10))]
        vendors = [VendorUserFactory.create() for _ in range(min(20, count // 5))]

        orders = []
        commissions = []

        for i in range(count):
            buyer = factory.random.randgen.choice(buyers)
            vendor = factory.random.randgen.choice(vendors)

            product = ProductFactory.create(vendedor_id=vendor.id)
            order = OrderFactory.create(
                buyer_id=buyer.id,
                status=OrderStatus.CONFIRMED,
                total_amount=Decimal(str(factory.Faker('random_int', min=10000, max=1000000).generate()))
            )
            commission = CommissionFactory.create(
                order_id=order.id,
                vendor_id=vendor.id,
                order_amount=order.total_amount
            )

            orders.append(order)
            commissions.append(commission)

        logger.info(f"Performance test data created: {len(orders)} orders, {len(commissions)} commissions")

        return {
            'buyers': buyers,
            'vendors': vendors,
            'orders': orders,
            'commissions': commissions
        }


# Validation Factories for Edge Cases

class EdgeCaseFinancialFactory:
    """Factory for creating edge case financial scenarios"""

    def __init__(self, session: Session):
        self.session = session

    def create_zero_commission_scenario(self) -> dict:
        """Create scenario with zero commission (enterprise tier)"""
        scenario_factory = FinancialScenarioFactory(self.session)
        scenario = scenario_factory.create_basic_order_scenario()

        commission = CommissionFactory.create(
            order_id=scenario['order'].id,
            vendor_id=scenario['vendor'].id,
            order_amount=scenario['order'].total_amount,
            commission_rate=Decimal("0.00"),  # 0% commission
            commission_amount=Decimal("0.00"),
            vendor_amount=scenario['order'].total_amount,
            platform_amount=Decimal("0.00")
        )

        return {**scenario, 'commission': commission}

    def create_high_precision_scenario(self) -> dict:
        """Create scenario with high decimal precision requirements"""
        scenario_factory = FinancialScenarioFactory(self.session)
        scenario = scenario_factory.create_basic_order_scenario(
            order_amount=Decimal("33333.33")  # Requires precise decimal handling
        )

        commission = CommissionFactory.create(
            order_id=scenario['order'].id,
            vendor_id=scenario['vendor'].id,
            order_amount=scenario['order'].total_amount,
            commission_rate=Decimal("0.0333"),  # 3.33% - creates precision challenges
        )

        return {**scenario, 'commission': commission}

    def create_large_amount_scenario(self) -> dict:
        """Create scenario with very large financial amounts"""
        scenario_factory = FinancialScenarioFactory(self.session)
        large_amount = Decimal("9999999.99")  # Near maximum amount

        scenario = scenario_factory.create_basic_order_scenario(order_amount=large_amount)

        commission = CommissionFactory.create(
            order_id=scenario['order'].id,
            vendor_id=scenario['vendor'].id,
            order_amount=large_amount,
            commission_type=CommissionType.STANDARD
        )

        return {**scenario, 'commission': commission}


# Financial Test Data Utilities

class FinancialDataValidator:
    """Utility class for validating financial test data integrity"""

    @staticmethod
    def validate_commission_calculations(commission: Commission) -> bool:
        """Validate commission financial calculations"""
        calculated_total = commission.vendor_amount + commission.platform_amount
        return abs(calculated_total - commission.order_amount) < Decimal('0.01')

    @staticmethod
    def validate_transaction_amounts(transaction: Transaction, commission: Commission) -> bool:
        """Validate transaction amounts match commission"""
        return abs(transaction.monto_vendedor - commission.vendor_amount) < Decimal('0.01')

    @staticmethod
    def validate_financial_constraints(obj) -> list:
        """Validate object meets financial constraints"""
        errors = []

        if isinstance(obj, Commission):
            if obj.order_amount <= 0:
                errors.append("Order amount must be positive")
            if obj.commission_rate < 0 or obj.commission_rate > 1:
                errors.append("Commission rate must be between 0 and 1")
            if not FinancialDataValidator.validate_commission_calculations(obj):
                errors.append("Commission calculations do not balance")

        elif isinstance(obj, Transaction):
            if obj.monto <= 0:
                errors.append("Transaction amount must be positive")
            if obj.porcentaje_mestocker < 0 or obj.porcentaje_mestocker > 100:
                errors.append("Commission percentage must be between 0 and 100")

        return errors


# Export main factories for easy import
__all__ = [
    'BuyerUserFactory',
    'VendorUserFactory',
    'AdminUserFactory',
    'OrderFactory',
    'SmallOrderFactory',
    'MediumOrderFactory',
    'LargeOrderFactory',
    'CommissionFactory',
    'StandardCommissionFactory',
    'PremiumCommissionFactory',
    'ApprovedCommissionFactory',
    'PaidCommissionFactory',
    'TransactionFactory',
    'CompletedTransactionFactory',
    'FinancialScenarioFactory',
    'EdgeCaseFinancialFactory',
    'FinancialDataValidator'
]