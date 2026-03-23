from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional

from app.core.auth import get_current_user
from app.models.user import User
from app.models.billing import Subscription
from app.schemas.billing import SubscriptionOut, CheckoutResponse, PortalResponse
from app.services.stripe_service import (
    create_checkout_session,
    create_portal_session,
    handle_webhook_event,
    simulate_checkout,
)

router = APIRouter(prefix="/billing", tags=["Billing"])

FRONTEND_URL = "http://localhost:3000"  # overridden by ALLOWED_ORIGINS in prod


@router.get("/subscription", response_model=Optional[SubscriptionOut])
async def get_subscription(current_user: User = Depends(get_current_user)):
    """Return the current user's subscription status. None if no subscription exists yet."""
    return await Subscription.get_or_none(clerk_user_id=current_user.user_id)


@router.post("/checkout", response_model=CheckoutResponse)
async def start_checkout(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    Create a Stripe Checkout Session with a 14-day free trial.
    Returns a URL to redirect the user to Stripe's hosted checkout.
    """
    origin = request.headers.get("origin", FRONTEND_URL)
    url = await create_checkout_session(
        clerk_user_id=current_user.user_id,
        email=current_user.email,
        success_url=f"{origin}/dashboard?billing=success",
        cancel_url=f"{origin}/pricing?billing=canceled",
    )
    return CheckoutResponse(url=url)


@router.post("/portal", response_model=PortalResponse)
async def open_portal(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    Create a Stripe Customer Portal session so the user can manage their
    subscription, update payment method, or cancel.
    """
    origin = request.headers.get("origin", FRONTEND_URL)
    url = await create_portal_session(
        clerk_user_id=current_user.user_id,
        return_url=f"{origin}/dashboard/billing",
    )
    return PortalResponse(url=url)


@router.post("/simulate/{scenario}", tags=["Billing (Dev Only)"])
async def simulate_billing(
    scenario: str,
    current_user: User = Depends(get_current_user),
):
    """
    DEV ONLY — simulate a billing state without real Stripe keys.
    scenario: trial | active | past_due | canceled
    """
    import os
    if os.getenv("APP_ENV", "development") != "development":
        raise HTTPException(status_code=403, detail="Simulation only available in development")
    result = await simulate_checkout(current_user.user_id, scenario)
    return result


@router.post("/webhook", status_code=200)
async def stripe_webhook(request: Request):
    """
    Stripe webhook endpoint — must NOT be behind auth middleware.
    Stripe signs each request; we verify the signature.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    await handle_webhook_event(payload, sig_header)
    return {"received": True}
