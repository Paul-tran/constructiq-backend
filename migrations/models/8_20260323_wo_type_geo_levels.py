from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE wo_types ADD COLUMN geography_levels_required JSONB NOT NULL DEFAULT '[]';
        UPDATE wo_types SET geography_levels_required = '["site"]' WHERE geography_required = true;
        ALTER TABLE wo_types DROP COLUMN geography_required;
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE wo_types ADD COLUMN geography_required BOOLEAN NOT NULL DEFAULT true;
        UPDATE wo_types SET geography_required = (geography_levels_required @> '["site"]');
        ALTER TABLE wo_types DROP COLUMN geography_levels_required;
    """
