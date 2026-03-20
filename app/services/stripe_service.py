import os
import asyncio
from datetime import datetime, timezone
from typing import Optional

import stripe
from fastapi import HTTPException

from app.models.billing import Subscription


def _get_stripe():
    key = os.getenv("STRIPE_SECRET_KEY")
    if not key or key == "your-stripe-secret-key":
        raise HTTPException(status_code=500, detail="Stripe is not configured")
    stripe.api_key = key
    return stripe


# --- Customer ---

async def get_or_create_customer(clerk_user_id: str, email: Optional[str] = None) -> str:
    """Return existing Stripe customer ID or create a new one."""
    sub = await Subscription.get_or_none(clerk_user_id=clerk_user_id)
    if sub and sub.stripe_customer_id:
        return sub.stripe_customer_id

    s = _get_stripe()
    customer = await asyncio.to_thread(
        s.Customer.create,
        email=email,
        metadata={"clerk_user_id": clerk_user_id},
    )

    if sub:
        sub.stripe_customer_id = customer.id
        await sub.save()
    else:
        await Subscription.create(
            clerk_user_id=clerk_user_id,
            stripe_customer_id=customer.id,
            status="trialing",
        )

    return customer.id


# --- Checkout ---

async def create_checkout_session(
    clerk_user_id: str,
    email: Optional[str],
    success_url: str,
    cancel_url: str,
) -> str:
    """Create a Stripe Checkout Session with 14-day trial. Returns the session URL."""
    price_id = os.getenv("STRIPE_PRICE_ID")
    if not price_id:
        raise HTTPException(status_code=500, detail="STRIPE_PRICE_ID is not configured")

    s = _get_stripe()
    customer_id = await get_or_create_customer(clerk_user_id, email)

    session = await asyncio.to_thread(
        s.checkout.Session.create,
        customer=customer_id,
        mode="subscription",
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        subscription_data={"trial_period_days": 14},
        allow_promotion_codes=True,
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session.url


# --- Customer Portal ---

async def create_portal_session(clerk_user_id: str, return_url: str) -> str:
    """Create a Stripe Customer Portal session so users can manage their subscription."""
    sub = await Subscription.get_or_none(clerk_user_id=clerk_user_id)
    if not sub or not sub.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No billing account found")

    s = _get_stripe()
    session = await asyncio.to_thread(
        s.billing_portal.Session.create,
        customer=sub.stripe_customer_id,
        return_url=return_url,
    )
    return session.url


# --- Webhook event handler ---

async def handle_webhook_event(payload: bytes, sig_header: str) -> None:
    """Verify and process a Stripe webhook event."""
    secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not secret or secret == "your-stripe-webhook-secret":
        raise HTTPException(status_code=500, detail="Webhook secret not configured")

    s = _get_stripe()
    try:
        event = s.Webhook.construct_event(payload, sig_header, secret)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        await _on_checkout_completed(data)

    elif event_type in ("customer.subscription.updated", "customer.subscription.created"):
        await _on_subscription_updated(data)

    elif event_type == "customer.subscription.deleted":
        await _on_subscription_deleted(data)

    elif event_type == "invoice.payment_failed":
        await _on_payment_failed(data)

    elif event_type == "invoice.payment_succeeded":
        await _on_payment_succeeded(data)


# --- Private event handlers ---

async def _on_checkout_completed(session: dict) -> None:
    customer_id = session.get("customer")
    subscription_id = session.get("subscription")
    if not customer_id:
        return

    sub = await Subscription.get_or_none(stripe_customer_id=customer_id)
    if sub:
        sub.stripe_subscription_id = subscription_id
        sub.status = "trialing"
        await sub.save()


async def _on_subscription_updated(stripe_sub: dict) -> None:
    customer_id = stripe_sub.get("customer")
    sub = await Subscription.get_or_none(stripe_customer_id=customer_id)
    if not sub:
        return

    sub.stripe_subscription_id = stripe_sub["id"]
    sub.status = stripe_sub["status"]  # trialing / active / past_due / etc.

    trial_end = stripe_sub.get("trial_end")
    if trial_end:
        sub.trial_ends_at = datetime.fromtimestamp(trial_end, tz=timezone.utc)

    period_end = stripe_sub.get("current_period_end")
    if period_end:
        sub.current_period_end = datetime.fromtimestamp(period_end, tz=timezone.utc)

    await sub.save()


async def _on_subscription_deleted(stripe_sub: dict) -> None:
    customer_id = stripe_sub.get("customer")
    sub = await Subscription.get_or_none(stripe_customer_id=customer_id)
    if sub:
        sub.status = "canceled"
        await sub.save()


async def _on_payment_failed(invoice: dict) -> None:
    customer_id = invoice.get("customer")
    sub = await Subscription.get_or_none(stripe_customer_id=customer_id)
    if sub:
        sub.status = "past_due"
        await sub.save()


async def _on_payment_succeeded(invoice: dict) -> None:
    customer_id = invoice.get("customer")
    sub = await Subscription.get_or_none(stripe_customer_id=customer_id)
    if sub and sub.status == "past_due":
        sub.status = "active"
        await sub.save()
