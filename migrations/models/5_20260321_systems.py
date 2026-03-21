from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "system_level_configs" (
            "id" SERIAL PRIMARY KEY,
            "project_id" INT NOT NULL UNIQUE,
            "level1_name" VARCHAR(100) NOT NULL DEFAULT 'Discipline',
            "level2_name" VARCHAR(100) NOT NULL DEFAULT 'System',
            "level3_name" VARCHAR(100) NOT NULL DEFAULT 'Subsystem'
        );

        CREATE TABLE IF NOT EXISTS "system_disciplines" (
            "id" SERIAL PRIMARY KEY,
            "project_id" INT NOT NULL,
            "name" VARCHAR(200) NOT NULL,
            "code" VARCHAR(50) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS "system_groups" (
            "id" SERIAL PRIMARY KEY,
            "discipline_id" INT NOT NULL REFERENCES "system_disciplines" ("id") ON DELETE CASCADE,
            "name" VARCHAR(200) NOT NULL,
            "code" VARCHAR(50) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS "system_subgroups" (
            "id" SERIAL PRIMARY KEY,
            "group_id" INT NOT NULL REFERENCES "system_groups" ("id") ON DELETE CASCADE,
            "name" VARCHAR(200) NOT NULL,
            "code" VARCHAR(50) NOT NULL
        );

        ALTER TABLE "assets"
            ADD COLUMN IF NOT EXISTS "subgroup_id" INT REFERENCES "system_subgroups" ("id") ON DELETE SET NULL;
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "assets" DROP COLUMN IF EXISTS "subgroup_id";
        DROP TABLE IF EXISTS "system_subgroups";
        DROP TABLE IF EXISTS "system_groups";
        DROP TABLE IF EXISTS "system_disciplines";
        DROP TABLE IF EXISTS "system_level_configs";
    """
