from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "wo_types" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "category" VARCHAR(30) NOT NULL,
    "asset_required" BOOL NOT NULL  DEFAULT False,
    "geography_required" BOOL NOT NULL  DEFAULT True,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "project_id" INT NOT NULL REFERENCES "projects" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "wo_types" IS 'Admin-defined work order types per project.';
        ALTER TABLE "work_orders" ADD "site_id" INT;
        ALTER TABLE "work_orders" ADD "due_date" DATE;
        ALTER TABLE "work_orders" ADD "partition_id" INT;
        ALTER TABLE "work_orders" ADD "location_id" INT;
        ALTER TABLE "work_orders" ADD "unit_id" INT;
        ALTER TABLE "work_orders" ADD "wo_type_id" INT REFERENCES "wo_types" ("id") ON DELETE CASCADE;
        ALTER TABLE "work_orders" DROP COLUMN "work_type";
        ALTER TABLE "work_orders" ADD CONSTRAINT "fk_work_ord_sites_f23c5988" FOREIGN KEY ("site_id") REFERENCES "sites" ("id") ON DELETE CASCADE;
        ALTER TABLE "work_orders" ADD CONSTRAINT "fk_work_ord_partitio_3dcbd05d" FOREIGN KEY ("partition_id") REFERENCES "partitions" ("id") ON DELETE CASCADE;
        ALTER TABLE "work_orders" ADD CONSTRAINT "fk_work_ord_units_21778000" FOREIGN KEY ("unit_id") REFERENCES "units" ("id") ON DELETE CASCADE;
        ALTER TABLE "work_orders" ADD CONSTRAINT "fk_work_ord_location_e71445fe" FOREIGN KEY ("location_id") REFERENCES "locations" ("id") ON DELETE CASCADE;
        CREATE TABLE IF NOT EXISTS "work_order_comments" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "author" VARCHAR(255) NOT NULL,
    "body" TEXT NOT NULL,
    "is_system" BOOL NOT NULL  DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "work_order_id" INT NOT NULL REFERENCES "work_orders" ("id") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "wo_corrective_details" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "fault_description" TEXT NOT NULL,
    "failure_cause" VARCHAR(50) NOT NULL  DEFAULT 'unknown',
    "resolution" TEXT NOT NULL,
    "work_order_id" INT NOT NULL UNIQUE REFERENCES "work_orders" ("id") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "wo_pm_details" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "recurrence" VARCHAR(20) NOT NULL  DEFAULT 'one_off',
    "last_serviced_date" DATE,
    "work_order_id" INT NOT NULL UNIQUE REFERENCES "work_orders" ("id") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "wo_pm_checklist_items" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "description" VARCHAR(500) NOT NULL,
    "is_checked" BOOL NOT NULL  DEFAULT False,
    "order_index" INT NOT NULL  DEFAULT 0,
    "pm_detail_id" INT NOT NULL REFERENCES "wo_pm_details" ("id") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "wo_inspection_details" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "condition_rating" INT,
    "signed_off_by" VARCHAR(255),
    "work_order_id" INT NOT NULL UNIQUE REFERENCES "work_orders" ("id") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "wo_inspection_checklist_items" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "description" VARCHAR(500) NOT NULL,
    "result" VARCHAR(10) NOT NULL  DEFAULT 'na',
    "order_index" INT NOT NULL  DEFAULT 0,
    "inspection_detail_id" INT NOT NULL REFERENCES "wo_inspection_details" ("id") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "wo_operations_details" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "shift_start" TIMETZ,
    "shift_end" TIMETZ,
    "work_order_id" INT NOT NULL UNIQUE REFERENCES "work_orders" ("id") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "wo_operations_steps" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "description" VARCHAR(500) NOT NULL,
    "is_completed" BOOL NOT NULL  DEFAULT False,
    "order_index" INT NOT NULL  DEFAULT 0,
    "operations_detail_id" INT NOT NULL REFERENCES "wo_operations_details" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "work_orders" DROP CONSTRAINT IF EXISTS "fk_work_ord_location_e71445fe";
        ALTER TABLE "work_orders" DROP CONSTRAINT IF EXISTS "fk_work_ord_units_21778000";
        ALTER TABLE "work_orders" DROP CONSTRAINT IF EXISTS "fk_work_ord_partitio_3dcbd05d";
        ALTER TABLE "work_orders" DROP CONSTRAINT IF EXISTS "fk_work_ord_sites_f23c5988";
        ALTER TABLE "work_orders" ADD "work_type" VARCHAR(50) NOT NULL  DEFAULT 'corrective';
        ALTER TABLE "work_orders" DROP COLUMN IF EXISTS "site_id";
        ALTER TABLE "work_orders" DROP COLUMN IF EXISTS "due_date";
        ALTER TABLE "work_orders" DROP COLUMN IF EXISTS "partition_id";
        ALTER TABLE "work_orders" DROP COLUMN IF EXISTS "wo_type_id";
        ALTER TABLE "work_orders" DROP COLUMN IF EXISTS "location_id";
        ALTER TABLE "work_orders" DROP COLUMN IF EXISTS "unit_id";
        DROP TABLE IF EXISTS "wo_operations_steps";
        DROP TABLE IF EXISTS "wo_operations_details";
        DROP TABLE IF EXISTS "wo_inspection_checklist_items";
        DROP TABLE IF EXISTS "wo_inspection_details";
        DROP TABLE IF EXISTS "wo_pm_checklist_items";
        DROP TABLE IF EXISTS "wo_pm_details";
        DROP TABLE IF EXISTS "wo_corrective_details";
        DROP TABLE IF EXISTS "work_order_comments";
        DROP TABLE IF EXISTS "wo_types";"""
