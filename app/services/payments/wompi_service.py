import httpx
import hashlib
import hmac
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from decimal import Decimal
import os
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class WompiConfig:
    def __init__(self):
        self.public_key = os.getenv("WOMPI_PUBLIC_KEY")
        self.private_key = os.getenv("WOMPI_PRIVATE_KEY")
        self.environment = os.getenv("WOMPI_ENVIRONMENT", "test")
        self.webhook_secret = os.getenv("WOMPI_WEBHOOK_SECRET")
        self.base_url = os.getenv("WOMPI_BASE_URL", "https://sandbox.wompi.co/v1")
        
        # Allow missing keys in test environment
        is_test_env = os.getenv("PYTEST_CURRENT_TEST") is not None or os.getenv("TESTING") == "1"
        
        if not self.public_key or not self.private_key:
            if is_test_env:
                # Use test defaults for testing
                self.public_key = self.public_key or "pub_test_default"
                self.private_key = self.private_key or "prv_test_default"
            else:
                raise ValueError("WOMPI_PUBLIC_KEY and WOMPI_PRIVATE_KEY must be set")

class PaymentSourceCard(BaseModel):
    type: str = "CARD"
    token: str
    installments: int = 1

class PaymentSourcePSE(BaseModel):
    type: str = "PSE"
    user_type: str  # "0" for natural person, "1" for juridical person
    user_legal_id: str
    financial_institution_code: str
    payment_description: str

class PaymentRequest(BaseModel):
    amount_in_cents: int
    currency: str = "COP"
    customer_email: str
    payment_method: Dict[str, Any]
    redirect_url: str
    reference: str
    payment_source_id: Optional[int] = None

class WompiService:
    def __init__(self):
        self.config = WompiConfig()
        self.client = httpx.AsyncClient(
            base_url=self.config.base_url,
            headers={
                "Authorization": f"Bearer {self.config.private_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def _generate_signature(self, data: str) -> str:
        """Generate signature for webhook validation"""
        return hmac.new(
            self.config.webhook_secret.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()

    async def get_acceptance_token(self) -> Dict[str, Any]:
        """Get merchant acceptance token required for payments"""
        try:
            response = await self.client.get("/merchants/{self.config.public_key}")
            response.raise_for_status()
            data = response.json()
            
            return {
                "acceptance_token": data.get("data", {}).get("presigned_acceptance", {}).get("acceptance_token"),
                "permalink": data.get("data", {}).get("presigned_acceptance", {}).get("permalink")
            }
        except httpx.HTTPError as e:
            logger.error(f"Error getting acceptance token: {e}")
            raise Exception("Failed to get acceptance token")

    async def tokenize_card(self, card_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tokenize a credit/debit card"""
        try:
            payload = {
                "number": card_data["number"],
                "exp_month": card_data["exp_month"], 
                "exp_year": card_data["exp_year"],
                "cvc": card_data["cvc"],
                "card_holder": card_data["card_holder"]
            }
            
            # Use public key for tokenization
            headers = {
                "Authorization": f"Bearer {self.config.public_key}",
                "Content-Type": "application/json"
            }
            
            response = await self.client.post(
                "/tokens/cards", 
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"Error tokenizing card: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise Exception("Card tokenization failed")

    async def create_payment_source(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a payment source (card or PSE)"""
        try:
            acceptance_token = await self.get_acceptance_token()
            
            payload = {
                "type": payment_data["type"],
                "acceptance_token": acceptance_token["acceptance_token"],
                "customer_email": payment_data["customer_email"]
            }
            
            if payment_data["type"] == "CARD":
                payload.update({
                    "token": payment_data["token"],
                    "customer_data": {
                        "phone_number": payment_data.get("phone_number", ""),
                        "full_name": payment_data.get("full_name", "")
                    }
                })
            elif payment_data["type"] == "PSE":
                payload.update({
                    "user_type": payment_data["user_type"],
                    "user_legal_id": payment_data["user_legal_id"],
                    "financial_institution_code": payment_data["financial_institution_code"],
                    "payment_description": payment_data["payment_description"]
                })
            
            response = await self.client.post("/payment_sources", json=payload)
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"Error creating payment source: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise Exception("Failed to create payment source")

    async def create_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a payment transaction"""
        try:
            payload = {
                "amount_in_cents": transaction_data["amount_in_cents"],
                "currency": transaction_data.get("currency", "COP"),
                "customer_email": transaction_data["customer_email"],
                "payment_method": transaction_data["payment_method"],
                "reference": transaction_data["reference"],
                "redirect_url": transaction_data["redirect_url"]
            }
            
            if "payment_source_id" in transaction_data:
                payload["payment_source_id"] = transaction_data["payment_source_id"]
                
            response = await self.client.post("/transactions", json=payload)
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"Error creating transaction: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise Exception("Failed to create transaction")

    async def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction details"""
        try:
            response = await self.client.get(f"/transactions/{transaction_id}")
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"Error getting transaction {transaction_id}: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise Exception("Failed to get transaction")

    async def get_pse_banks(self) -> List[Dict[str, Any]]:
        """Get available PSE banks"""
        try:
            response = await self.client.get("/pse/financial_institutions")
            response.raise_for_status()
            
            data = response.json()
            return data.get("data", [])
            
        except httpx.HTTPError as e:
            logger.error(f"Error getting PSE banks: {e}")
            return []

    def validate_webhook_signature(self, payload: str, signature: str) -> bool:
        """Validate webhook signature"""
        try:
            expected_signature = self._generate_signature(payload)
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            logger.error(f"Error validating webhook signature: {e}")
            return False

    async def process_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process webhook event from Wompi"""
        try:
            event = payload.get("event")
            data = payload.get("data", {})
            
            if event == "transaction.updated":
                transaction_id = data.get("id")
                if transaction_id:
                    # Get full transaction details
                    transaction = await self.get_transaction(transaction_id)
                    return {
                        "event": event,
                        "transaction": transaction,
                        "processed": True
                    }
            
            return {
                "event": event,
                "data": data,
                "processed": False
            }
            
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            raise Exception("Webhook processing failed")

    async def void_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Void/cancel a transaction"""
        try:
            response = await self.client.post(f"/transactions/{transaction_id}/void")
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"Error voiding transaction {transaction_id}: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise Exception("Failed to void transaction")

    def amount_to_cents(self, amount: float) -> int:
        """Convert amount to cents for Wompi"""
        return int(Decimal(str(amount)) * 100)

    def cents_to_amount(self, cents: int) -> float:
        """Convert cents to amount"""
        return float(Decimal(cents) / 100)

    def generate_reference(self, order_id: int) -> str:
        """Generate unique reference for transaction"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"ORDER_{order_id}_{timestamp}"

# Singleton instance - lazy loading
_wompi_service = None

def get_wompi_service() -> WompiService:
    """Get or create the Wompi service singleton"""
    global _wompi_service
    if _wompi_service is None:
        _wompi_service = WompiService()
    return _wompi_service

# For backwards compatibility
wompi_service = None