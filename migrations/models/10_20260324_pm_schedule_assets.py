from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "pm_schedule_assets" (
            "schedule_id" INT NOT NULL REFERENCES "pm_schedules" ("id") ON DELETE CASCADE,
            "asset_id"    INT NOT NULL REFERENCES "assets" ("id") ON DELETE CASCADE,
            PRIMARY KEY ("schedule_id", "asset_id")
        );
        -- Migrate any existing single asset_id values into the join table
        INSERT INTO "pm_schedule_assets" ("schedule_id", "asset_id")
        SELECT "id", "asset_id" FROM "pm_schedules" WHERE "asset_id" IS NOT NULL;
        ALTER TABLE "pm_schedules" DROP COLUMN IF EXISTS "asset_id";
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "pm_schedules" ADD COLUMN IF NOT EXISTS "asset_id" INT;
        DROP TABLE IF EXISTS "pm_schedule_assets";
    """
