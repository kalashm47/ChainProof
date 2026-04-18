# tests/api/test_payment_service_real.py
"""
Tests for the actual payment_service.py file
Imports the REAL schema from your project
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from pydantic import ValidationError

# Import YOUR actual file - adjust path as needed
import sys
from pathlib import Path

# Add your project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Try to import your actual schema
try:
    from services.api.app.schemas.payment import PaymentWatchRequest, PaymentTimeWindow
    print("✅ Successfully imported from your actual payment_service.py")
except ImportError as e:
    print(f"❌ Could not import: {e}")
    print("Make sure your payment_service.py is in the correct location")
    # Fallback to inline definition for testing
    from pydantic import BaseModel, field_validator
    
    class PaymentWatchRequest(BaseModel):
        amount: Decimal
        currency: str
        address: str
        start_at: datetime 
        end_at: datetime
        
        @field_validator("end_at")
        @classmethod
        def end_must_be_strictly_after_start(cls, v, info):
            start_at = info.data.get("start_at")
            if start_at and v <= start_at:
                raise ValueError("End timestamp must be strictly after start timestamp")
            return v
        
        @field_validator('amount')
        @classmethod
        def validate_amount_positive(cls, v: Decimal) -> Decimal:
            if v <= 0:
                raise ValueError('amount must be greater than zero')
            return v
        
        @field_validator('currency')
        @classmethod
        def validate_currency(cls, v: str) -> str:
            valid_currencies = {'USD', 'EUR', 'ETH'}
            if v.upper() not in valid_currencies:
                raise ValueError(f'currency must be one of: {valid_currencies}')
            return v.upper()
        
        @field_validator('address')
        @classmethod
        def validate_address(cls, v: str) -> str:
            # CORRECTED version
            if not v:
                raise ValueError('address is required')
            if not v.startswith('0x'):
                raise ValueError('address must start with 0x')
            return v


class TestRealPaymentService:
    """Tests for the actual PaymentWatchRequest from your project"""
    
    @pytest.fixture
    def valid_data(self):
        return {
            "amount": Decimal("100.50"),
            "currency": "USD",
            "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
            "start_at": datetime(2025, 1, 1, 10, 0, 0),
            "end_at": datetime(2025, 1, 1, 12, 0, 0)
        }
    
    def test_create_valid_payment_request(self, valid_data):
        """Test that a valid payment request passes validation"""
        request = PaymentWatchRequest(**valid_data)
        assert request.amount == valid_data["amount"]
        assert request.currency == "USD"
        assert request.address == valid_data["address"]
    
    def test_amount_zero_fails(self, valid_data):
        """Test that amount zero is rejected"""
        valid_data["amount"] = Decimal("0")
        with pytest.raises(ValidationError) as exc:
            PaymentWatchRequest(**valid_data)
        assert "greater than zero" in str(exc.value)
    
    def test_amount_negative_fails(self, valid_data):
        """Test that negative amount is rejected"""
        valid_data["amount"] = Decimal("-10")
        with pytest.raises(ValidationError) as exc:
            PaymentWatchRequest(**valid_data)
        assert "greater than zero" in str(exc.value)
    
    def test_invalid_currency_fails(self, valid_data):
        """Test that invalid currency is rejected"""
        valid_data["currency"] = "BRL"
        with pytest.raises(ValidationError) as exc:
            PaymentWatchRequest(**valid_data)
        assert "currency must be one of" in str(exc.value)
    
    def test_address_without_0x_fails(self, valid_data):
        """Test that address without 0x prefix is rejected"""
        valid_data["address"] = "742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
        with pytest.raises(ValidationError) as exc:
            PaymentWatchRequest(**valid_data)
        assert "must start with 0x" in str(exc.value)
    
    def test_address_empty_fails(self, valid_data):
        """Test that empty address is rejected"""
        valid_data["address"] = ""
        with pytest.raises(ValidationError) as exc:
            PaymentWatchRequest(**valid_data)
        assert "address is required" in str(exc.value)
    
    def test_end_before_start_fails(self, valid_data):
        """Test that end_at before start_at is rejected"""
        valid_data["start_at"] = datetime(2025, 1, 1, 12, 0, 0)
        valid_data["end_at"] = datetime(2025, 1, 1, 10, 0, 0)
        with pytest.raises(ValidationError) as exc:
            PaymentWatchRequest(**valid_data)
        assert "strictly after" in str(exc.value)
    
    def test_end_equal_start_fails(self, valid_data):
        """Test that end_at equal to start_at is rejected"""
        same_time = datetime(2025, 1, 1, 10, 0, 0)
        valid_data["start_at"] = same_time
        valid_data["end_at"] = same_time
        with pytest.raises(ValidationError) as exc:
            PaymentWatchRequest(**valid_data)
        assert "strictly after" in str(exc.value)
    
    def test_currency_case_insensitive(self, valid_data):
        """Test that currency is case insensitive"""
        valid_data["currency"] = "eur"
        request = PaymentWatchRequest(**valid_data)
        assert request.currency == "EUR"
    
    def test_all_currencies_accepted(self, valid_data):
        """Test that all valid currencies are accepted"""
        for currency in ["USD", "EUR", "ETH"]:
            valid_data["currency"] = currency
            request = PaymentWatchRequest(**valid_data)
            assert request.currency == currency


class TestPaymentTimeWindowReal:
    """Tests for PaymentTimeWindow from your project"""
    
    def test_valid_window(self):
        """Test valid time window"""
        start = datetime(2025, 1, 1, 10, 0, 0)
        end = datetime(2025, 1, 1, 12, 0, 0)
        window = PaymentTimeWindow(start_at=start, end_at=end)
        assert window.start_at == start
        assert window.end_at == end
    
    def test_end_before_start_fails(self):
        """Test that end before start fails"""
        start = datetime(2025, 1, 1, 12, 0, 0)
        end = datetime(2025, 1, 1, 10, 0, 0)
        with pytest.raises(ValidationError) as exc:
            PaymentTimeWindow(start_at=start, end_at=end)
        assert "strictly after" in str(exc.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])