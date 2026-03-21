from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "work_orders" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,
    "work_type" VARCHAR(50) NOT NULL  DEFAULT 'corrective',
    "priority" VARCHAR(20) NOT NULL  DEFAULT 'medium',
    "status" VARCHAR(30) NOT NULL  DEFAULT 'open',
    "assigned_to" VARCHAR(255),
    "scheduled_date" DATE,
    "completed_date" DATE,
    "labour_hours" DECIMAL(6,2),
    "notes" TEXT NOT NULL,
    "created_by" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "asset_id" INT REFERENCES "assets" ("id") ON DELETE CASCADE,
    "project_id" INT NOT NULL REFERENCES "projects" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "work_orders";"""
