from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "subscriptions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "clerk_user_id" VARCHAR(255) NOT NULL UNIQUE,
    "stripe_customer_id" VARCHAR(255),
    "stripe_subscription_id" VARCHAR(255),
    "status" VARCHAR(50) NOT NULL  DEFAULT 'trialing',
    "trial_ends_at" TIMESTAMPTZ,
    "current_period_end" TIMESTAMPTZ,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "subscriptions";"""
