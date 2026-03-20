from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SubscriptionOut(BaseModel):
    id: int
    clerk_user_id: str
    stripe_customer_id: Optional[str]
    stripe_subscription_id: Optional[str]
    status: str
    trial_ends_at: Optional[datetime]
    current_period_end: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CheckoutResponse(BaseModel):
    url: str


class PortalResponse(BaseModel):
    url: str
