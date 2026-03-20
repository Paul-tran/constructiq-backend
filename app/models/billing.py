from tortoise import fields
from tortoise.models import Model


class Subscription(Model):
    id = fields.IntField(pk=True)
    clerk_user_id = fields.CharField(max_length=255, unique=True)
    stripe_customer_id = fields.CharField(max_length=255, null=True)
    stripe_subscription_id = fields.CharField(max_length=255, null=True)
    # trialing / active / past_due / canceled / unpaid
    status = fields.CharField(max_length=50, default="trialing")
    trial_ends_at = fields.DatetimeField(null=True)
    current_period_end = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "subscriptions"

    def __str__(self):
        return f"{self.clerk_user_id} — {self.status}"
