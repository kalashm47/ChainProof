# tests/api/test_payment_validator.py
"""
Unit tests for payment input validator.
Tests the validation logic for /watch_payment endpoint.
"""

import pytest
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ValidationError, field_validator


# ============================================================================
# VALIDATOR IMPLEMENTATION (move this to your actual schema file later)
# ============================================================================

class PaymentWatchRequest(BaseModel):
    """
    Request schema for POST /watch_payment endpoint.
    Validates all input fields before processing.
    """
    amount: Decimal
    currency: str
    address: str
    
    @field_validator('amount')
    @classmethod
    def validate_amount_positive(cls, v: Decimal) -> Decimal:
        """Amount must be greater than zero."""
        if v <= 0:
            raise ValueError('amount must be greater than zero')
        return v
    
    @field_validator('amount')
    @classmethod
    def validate_amount_decimals(cls, v: Decimal) -> Decimal:
        """Amount cannot have more than 2 decimal places for fiat currencies."""
        exponent = v.as_tuple().exponent
        
        # Check if it's a special value (NaN, Infinity)
        if not isinstance(exponent, int):
            raise ValueError('invalid amount value')
        
        # Now safe to compare with integer
        if exponent < -2:
            raise ValueError('amount cannot have more than 2 decimal places')
        return v
    @field_validator('currency')
    @classmethod
    def validate_currency_code(cls, v: str) -> str:
        """Currency must be a valid ISO 4217 code."""
        valid_currencies = {'BRL', 'USD', 'EUR', 'GBP', 'ETH'}
        v_upper = v.upper()
        if v_upper not in valid_currencies:
            raise ValueError(f'currency must be one of: {", ".join(valid_currencies)}')
        return v_upper
    
    @field_validator('address')
    @classmethod
    def validate_address_not_empty(cls, v: str) -> str:
        """Address cannot be empty or whitespace only."""
        if not v or not v.strip():
            raise ValueError('address is required')
        return v.strip()
    
    @field_validator('address')
    @classmethod
    def validate_ethereum_format(cls, v: str) -> str:
        """
        Validate Ethereum address format.
        Must start with 0x and have exactly 42 characters (0x + 40 hex chars).
        """
        if not v.startswith('0x'):
            raise ValueError('address must start with 0x')
        
        hex_part = v[2:]
        if len(hex_part) != 40:
            raise ValueError('address must have exactly 40 hexadecimal characters after 0x')
        
        try:
            int(hex_part, 16)
        except ValueError:
            raise ValueError('address contains invalid hexadecimal characters')
        
        return v


# ============================================================================
# UNIT TESTS
# ============================================================================

class TestPaymentWatchValidator:
    """Test suite for PaymentWatchRequest validator."""
    
    # ------------------------------------------------------------------------
    # AMOUNT VALIDATION TESTS
    # ------------------------------------------------------------------------
    
    def test_amount_positive_valid(self):
        """Should accept amount greater than zero."""
        request = PaymentWatchRequest(
            amount=Decimal("100.50"),
            currency="BRL",
            address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
        )
        assert request.amount == Decimal("100.50")
    
    def test_amount_zero_invalid(self):
        """Should reject amount equal to zero."""
        with pytest.raises(ValidationError) as exc_info:
            PaymentWatchRequest(
                amount=Decimal("0"),
                currency="BRL",
                address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
            )
        errors = exc_info.value.errors()
        assert any('greater than zero' in str(error['msg']) for error in errors)
    
    def test_amount_negative_invalid(self):
        """Should reject negative amount."""
        with pytest.raises(ValidationError) as exc_info:
            PaymentWatchRequest(
                amount=Decimal("-50.00"),
                currency="BRL",
                address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
            )
        errors = exc_info.value.errors()
        assert any('greater than zero' in str(error['msg']) for error in errors)
    
    def test_amount_too_many_decimals_invalid(self):
        """Should reject amount with more than 2 decimal places."""
        with pytest.raises(ValidationError) as exc_info:
            PaymentWatchRequest(
                amount=Decimal("100.123"),
                currency="BRL",
                address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
            )
        errors = exc_info.value.errors()
        assert any('2 decimal places' in str(error['msg']) for error in errors)
    
    # ------------------------------------------------------------------------
    # CURRENCY VALIDATION TESTS
    # ------------------------------------------------------------------------
    
    def test_currency_brl_valid(self):
        """Should accept BRL currency."""
        request = PaymentWatchRequest(
            amount=Decimal("100.00"),
            currency="BRL",
            address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
        )
        assert request.currency == "BRL"
    
    def test_currency_usd_valid(self):
        """Should accept USD currency."""
        request = PaymentWatchRequest(
            amount=Decimal("100.00"),
            currency="usd",  # lowercase should work
            address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
        )
        assert request.currency == "USD"
    
    def test_currency_eth_valid(self):
        """Should accept ETH for cryptocurrency payments."""
        request = PaymentWatchRequest(
            amount=Decimal("0.05"),
            currency="ETH",
            address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
        )
        assert request.currency == "ETH"
    
    def test_currency_invalid_code(self):
        """Should reject invalid currency code."""
        with pytest.raises(ValidationError) as exc_info:
            PaymentWatchRequest(
                amount=Decimal("100.00"),
                currency="XYZ",
                address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
            )
        errors = exc_info.value.errors()
        assert any('currency must be one of' in str(error['msg']) for error in errors)
    
    def test_currency_empty_string_invalid(self):
        """Should reject empty currency string."""
        with pytest.raises(ValidationError) as exc_info:
            PaymentWatchRequest(
                amount=Decimal("100.00"),
                currency="",
                address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
            )
        errors = exc_info.value.errors()
        assert any('currency must be one of' in str(error['msg']) for error in errors)
    
    # ------------------------------------------------------------------------
    # ADDRESS VALIDATION TESTS
    # ------------------------------------------------------------------------
    
    def test_address_valid_ethereum_format(self):
        """Should accept valid Ethereum address with checksum."""
        request = PaymentWatchRequest(
            amount=Decimal("100.00"),
            currency="BRL",
            address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
        )
        assert request.address == "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
    
    def test_address_lowercase_valid(self):
        """Should accept lowercase Ethereum address."""
        request = PaymentWatchRequest(
            amount=Decimal("100.00"),
            currency="BRL",
            address="0x742d35cc6634c0532925a3b844bc9e7595f0beb0"
        )
        assert request.address == "0x742d35cc6634c0532925a3b844bc9e7595f0beb0"
    
    def test_address_empty_string_invalid(self):
        """Should reject empty address."""
        with pytest.raises(ValidationError) as exc_info:
            PaymentWatchRequest(
                amount=Decimal("100.00"),
                currency="BRL",
                address=""
            )
        errors = exc_info.value.errors()
        assert any('address is required' in str(error['msg']) for error in errors)
    
    def test_address_whitespace_only_invalid(self):
        """Should reject whitespace-only address."""
        with pytest.raises(ValidationError) as exc_info:
            PaymentWatchRequest(
                amount=Decimal("100.00"),
                currency="BRL",
                address="   "
            )
        errors = exc_info.value.errors()
        assert any('address is required' in str(error['msg']) for error in errors)
    
    def test_address_no_0x_prefix_invalid(self):
        """Should reject address without 0x prefix."""
        with pytest.raises(ValidationError) as exc_info:
            PaymentWatchRequest(
                amount=Decimal("100.00"),
                currency="BRL",
                address="742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
            )
        errors = exc_info.value.errors()
        assert any('must start with 0x' in str(error['msg']) for error in errors)
    
    def test_address_wrong_length_invalid(self):
        """Should reject address with wrong length."""
        with pytest.raises(ValidationError) as exc_info:
            PaymentWatchRequest(
                amount=Decimal("100.00"),
                currency="BRL",
                address="0x742d35Cc6634C0532925a3b844Bc9e"
            )
        errors = exc_info.value.errors()
        assert any('exactly 40 hexadecimal characters' in str(error['msg']) for error in errors)
    
    def test_address_invalid_hex_characters_invalid(self):
        """Should reject address with invalid hex characters."""
        with pytest.raises(ValidationError) as exc_info:
            PaymentWatchRequest(
                amount=Decimal("100.00"),
                currency="BRL",
                address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bGg0"
            )
        errors = exc_info.value.errors()
        assert any('invalid hexadecimal characters' in str(error['msg']) for error in errors)
    
    # ------------------------------------------------------------------------
    # MULTIPLE FIELDS VALIDATION TESTS
    # ------------------------------------------------------------------------
    
    def test_all_fields_valid(self):
        """Should accept when all fields are valid."""
        request = PaymentWatchRequest(
            amount=Decimal("150.75"),
            currency="EUR",
            address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
        )
        assert request.amount == Decimal("150.75")
        assert request.currency == "EUR"
        assert request.address == "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
    
    def test_multiple_validation_errors(self):
        """Should collect multiple validation errors when several fields are invalid."""
        with pytest.raises(ValidationError) as exc_info:
            PaymentWatchRequest(
                amount=Decimal("-10"),
                currency="INVALID",
                address="wrong_format"
            )
        
        errors = exc_info.value.errors()
        error_messages = [str(error['msg']) for error in errors]
        
        # Should have at least 3 different validation errors
        assert any('greater than zero' in msg for msg in error_messages)
        assert any('currency must be one of' in msg for msg in error_messages)
        assert any('must start with 0x' in msg for msg in error_messages)


# ============================================================================
# RUN TESTS
# ============================================================================
# Run with: pytest tests/api/test_payment_validator.py -v
# Or: python -m pytest tests/api/test_payment_validator.py -v