from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "pm_schedules" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "project_id" INT NOT NULL REFERENCES "projects" ("id") ON DELETE CASCADE,
            "name" VARCHAR(255) NOT NULL,
            "asset_id" INT,
            "site_id" INT,
            "location_id" INT,
            "unit_id" INT,
            "partition_id" INT,
            "assigned_to" VARCHAR(255),
            "lead_days" INT NOT NULL DEFAULT 7,
            "start_date" DATE NOT NULL,
            "is_active" BOOL NOT NULL DEFAULT TRUE,
            "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            "updated_at" TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS "pm_activities" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "schedule_id" INT NOT NULL REFERENCES "pm_schedules" ("id") ON DELETE CASCADE,
            "wo_type_id" INT REFERENCES "wo_types" ("id") ON DELETE SET NULL,
            "name" VARCHAR(255) NOT NULL,
            "frequency" VARCHAR(50) NOT NULL,
            "interval_days" INT,
            "end_date" DATE,
            "description" TEXT NOT NULL DEFAULT '',
            "next_due_date" DATE,
            "last_generated_date" DATE,
            "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            "updated_at" TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        ALTER TABLE "work_orders"
            ADD COLUMN IF NOT EXISTS "pm_activity_id" INT REFERENCES "pm_activities" ("id") ON DELETE SET NULL;
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "work_orders" DROP COLUMN IF EXISTS "pm_activity_id";
        DROP TABLE IF EXISTS "pm_activities";
        DROP TABLE IF EXISTS "pm_schedules";
    """
