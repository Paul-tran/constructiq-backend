from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "assets" ADD COLUMN IF NOT EXISTS "parent_id" INT REFERENCES "assets" ("id") ON DELETE SET NULL;
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "assets" DROP COLUMN IF EXISTS "parent_id";
    """
