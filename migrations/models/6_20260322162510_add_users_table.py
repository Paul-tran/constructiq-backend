from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "project_members" ADD "user_id" INT NOT NULL;
        ALTER TABLE "project_members" DROP COLUMN "clerk_user_id";
        CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "hashed_password" VARCHAR(255) NOT NULL,
    "first_name" VARCHAR(100) NOT NULL  DEFAULT '',
    "last_name" VARCHAR(100) NOT NULL  DEFAULT '',
    "avatar_key" VARCHAR(500),
    "is_active" BOOL NOT NULL  DEFAULT True,
    "is_verified" BOOL NOT NULL  DEFAULT False,
    "password_reset_token" VARCHAR(255),
    "password_reset_expires" TIMESTAMPTZ,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
        ALTER TABLE "project_members" ADD CONSTRAINT "fk_project__users_31fc404b" FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "project_members" DROP CONSTRAINT "fk_project__users_31fc404b";
        ALTER TABLE "project_members" ADD "clerk_user_id" VARCHAR(255) NOT NULL;
        ALTER TABLE "project_members" DROP COLUMN "user_id";
        DROP TABLE IF EXISTS "users";"""
