from decimal import Decimal
from datetime import datetime
from fastapi import  FastAPI
from pydantic import BaseModel, field_validator
from web3 import Web3

app = FastAPI()

class PaymentWatchRequest(BaseModel):
    amount: Decimal
    start_at: datetime 
    end_at: datetime
                        
    @field_validator("end_at")
    def end_must_be_strictly_after_start(cls, v, values):
        if "start_at" in values and v <= values["start_at"]:
            raise ValueError("End timestamp must be strictly after start timestamp")
        return v
    
    @field_validator('amount')
    @classmethod
    def validate_amount_positive(cls, v: Decimal) -> Decimal:
        if v <=0:
          raise ValueError('amount must be greater than zero')
        return v
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls,v: str) -> str:
        valid_currencies = {'USD', 'EUR', 'ETH'}
        if v.upper() not in valid_currencies:
             raise ValueError(f'currency must be one of: {valid_currencies}')
         
        return v.upper()
    
    @field_validator('address')
    @classmethod
    def validate_address(cls, v: str) -> str:
        if not v or v.startswith('0x'):
            raise ValueError('address must start with 0x')
        return v
    
    
class PaymentTimeWindow(BaseModel):
    start_at: datetime
    end_at: datetime
    
    @field_validator("end_at")
    @classmethod
    def end_must_be_strictly_after_start(cls, v, info):
        start_at = info.data.get("start_at")
        if start_at and v <= start_at:
            raise ValueError("End timestamp must be strictly after start timestamp")
        return v
    
    """""                   
    @app.post("/watch_payment")
    async def watch_payment(self, amount, currency: str, addres: str):
        errors = []

        try:
            amount_decimal = Decimal(str(amount))
        except Exception as e:
                return {"error": True, "status": 400, "errors": ["amount must be greater than 0"]}
        
        if amount_decimal <=0: 
                return {"error": True, "status": 400, "errors": ["amount must be greater than 0"]}
        try:
            self.amount = Web3.to_wei(amount_decimal, "ether")
        except Exception as e:
                return {"error": True, "status": 400, "errors": ["amount must be greater than 0"]}
        
        return {"error": False, "status": 200, "message": "Payment watched successfully", "amount_wei": self.amount}
    """
    async def payment_register():
        pass