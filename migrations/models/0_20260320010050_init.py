from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "sites" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "code" VARCHAR(50) NOT NULL UNIQUE,
    "address" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "locations" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "code" VARCHAR(50),
    "is_na" BOOL NOT NULL  DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "site_id" INT NOT NULL REFERENCES "sites" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "units" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "code" VARCHAR(50),
    "is_na" BOOL NOT NULL  DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "location_id" INT NOT NULL REFERENCES "locations" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "partitions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "code" VARCHAR(50),
    "is_na" BOOL NOT NULL  DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "unit_id" INT NOT NULL REFERENCES "units" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "companies" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "type" VARCHAR(50) NOT NULL,
    "address" TEXT,
    "contact_email" VARCHAR(255),
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "projects" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "number" VARCHAR(100) NOT NULL UNIQUE,
    "type" VARCHAR(100),
    "start_date" DATE,
    "end_date" DATE,
    "contract_value" DECIMAL(15,2),
    "currency" VARCHAR(10) NOT NULL  DEFAULT 'CAD',
    "client_name" VARCHAR(255),
    "client_contact" VARCHAR(255),
    "contractor_name" VARCHAR(255),
    "contractor_contact" VARCHAR(255),
    "status" VARCHAR(50) NOT NULL  DEFAULT 'planning',
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "company_id" INT NOT NULL REFERENCES "companies" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "project_companies" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "role" VARCHAR(100) NOT NULL,
    "joined_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "company_id" INT NOT NULL REFERENCES "companies" ("id") ON DELETE CASCADE,
    "project_id" INT NOT NULL REFERENCES "projects" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "project_geography_configs" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "level_1_enabled" BOOL NOT NULL  DEFAULT True,
    "level_1_name" VARCHAR(100) NOT NULL  DEFAULT 'Site',
    "level_2_enabled" BOOL NOT NULL  DEFAULT True,
    "level_2_name" VARCHAR(100) NOT NULL  DEFAULT 'Location',
    "level_3_enabled" BOOL NOT NULL  DEFAULT True,
    "level_3_name" VARCHAR(100) NOT NULL  DEFAULT 'Unit',
    "level_4_enabled" BOOL NOT NULL  DEFAULT True,
    "level_4_name" VARCHAR(100) NOT NULL  DEFAULT 'Partition',
    "project_id" INT NOT NULL REFERENCES "projects" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "roles" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "is_system_role" BOOL NOT NULL  DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "project_invitations" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "email" VARCHAR(255) NOT NULL,
    "invited_by" VARCHAR(255) NOT NULL,
    "status" VARCHAR(50) NOT NULL  DEFAULT 'pending',
    "expires_at" TIMESTAMPTZ NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "project_id" INT NOT NULL REFERENCES "projects" ("id") ON DELETE CASCADE,
    "role_id" INT NOT NULL REFERENCES "roles" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "project_members" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "clerk_user_id" VARCHAR(255) NOT NULL,
    "status" VARCHAR(50) NOT NULL  DEFAULT 'active',
    "joined_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "company_id" INT REFERENCES "companies" ("id") ON DELETE CASCADE,
    "project_id" INT NOT NULL REFERENCES "projects" ("id") ON DELETE CASCADE,
    "role_id" INT NOT NULL REFERENCES "roles" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "project_role_permissions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "module" VARCHAR(100) NOT NULL,
    "action" VARCHAR(100) NOT NULL,
    "allowed" BOOL NOT NULL  DEFAULT False,
    "project_id" INT NOT NULL REFERENCES "projects" ("id") ON DELETE CASCADE,
    "role_id" INT NOT NULL REFERENCES "roles" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "role_permissions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "module" VARCHAR(100) NOT NULL,
    "action" VARCHAR(100) NOT NULL,
    "allowed" BOOL NOT NULL  DEFAULT False,
    "role_id" INT NOT NULL REFERENCES "roles" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "documents" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "category" VARCHAR(100) NOT NULL  DEFAULT 'General',
    "drawing_type" VARCHAR(100),
    "status" VARCHAR(50) NOT NULL  DEFAULT 'draft',
    "version" VARCHAR(50) NOT NULL  DEFAULT 'v1.0',
    "description" TEXT,
    "uploaded_by" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "location_id" INT REFERENCES "locations" ("id") ON DELETE CASCADE,
    "partition_id" INT REFERENCES "partitions" ("id") ON DELETE CASCADE,
    "project_id" INT NOT NULL REFERENCES "projects" ("id") ON DELETE CASCADE,
    "site_id" INT REFERENCES "sites" ("id") ON DELETE CASCADE,
    "unit_id" INT REFERENCES "units" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "document_revisions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(50) NOT NULL,
    "file_key" VARCHAR(500) NOT NULL,
    "file_name" VARCHAR(255) NOT NULL,
    "file_size" INT,
    "status" VARCHAR(50) NOT NULL  DEFAULT 'draft',
    "uploaded_by" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "document_id" INT NOT NULL REFERENCES "documents" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "document_approvals" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "approver_id" VARCHAR(255) NOT NULL,
    "decision" VARCHAR(50) NOT NULL,
    "comments" TEXT,
    "approved_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "document_id" INT NOT NULL REFERENCES "documents" ("id") ON DELETE CASCADE,
    "revision_id" INT NOT NULL REFERENCES "document_revisions" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "document_comments" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "user_id" VARCHAR(255) NOT NULL,
    "comment" TEXT NOT NULL,
    "x_percent" DOUBLE PRECISION,
    "y_percent" DOUBLE PRECISION,
    "page_number" INT,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "document_id" INT NOT NULL REFERENCES "documents" ("id") ON DELETE CASCADE,
    "revision_id" INT NOT NULL REFERENCES "document_revisions" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "assets" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "tag" VARCHAR(100) NOT NULL,
    "name" VARCHAR(255),
    "type" VARCHAR(100),
    "status" VARCHAR(50) NOT NULL  DEFAULT 'active',
    "description" TEXT,
    "manufacturer" VARCHAR(255),
    "model" VARCHAR(255),
    "serial_number" VARCHAR(255),
    "supplier" VARCHAR(255),
    "planned_cost" DECIMAL(15,2),
    "actual_cost" DECIMAL(15,2),
    "po_number" VARCHAR(100),
    "delivery_date" DATE,
    "warranty_expiry" DATE,
    "commissioning_status" VARCHAR(50) NOT NULL  DEFAULT 'not_started',
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "location_id" INT REFERENCES "locations" ("id") ON DELETE CASCADE,
    "partition_id" INT REFERENCES "partitions" ("id") ON DELETE CASCADE,
    "project_id" INT NOT NULL REFERENCES "projects" ("id") ON DELETE CASCADE,
    "site_id" INT NOT NULL REFERENCES "sites" ("id") ON DELETE CASCADE,
    "unit_id" INT REFERENCES "units" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_assets_tag_4c1eb1" UNIQUE ("tag", "site_id", "location_id", "unit_id", "partition_id")
);
CREATE TABLE IF NOT EXISTS "drawing_assets" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "tag" VARCHAR(100) NOT NULL,
    "asset_type" VARCHAR(100),
    "description" TEXT,
    "x_percent" DOUBLE PRECISION NOT NULL,
    "y_percent" DOUBLE PRECISION NOT NULL,
    "page_number" INT NOT NULL  DEFAULT 1,
    "status" VARCHAR(50) NOT NULL  DEFAULT 'pending',
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "asset_id" INT REFERENCES "assets" ("id") ON DELETE CASCADE,
    "document_id" INT NOT NULL REFERENCES "documents" ("id") ON DELETE CASCADE,
    "revision_id" INT NOT NULL REFERENCES "document_revisions" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "asset_procurement_lines" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "line_item_number" INT,
    "description" TEXT,
    "amount" DECIMAL(15,2) NOT NULL,
    "mapped_by" VARCHAR(255) NOT NULL,
    "mapped_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "asset_id" INT NOT NULL REFERENCES "assets" ("id") ON DELETE CASCADE,
    "document_id" INT NOT NULL REFERENCES "documents" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "commissioning_records" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "type" VARCHAR(50) NOT NULL  DEFAULT 'individual',
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "assigned_to" VARCHAR(255),
    "witness_id" VARCHAR(255),
    "overall_status" VARCHAR(50) NOT NULL  DEFAULT 'not_started',
    "created_by" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "location_id" INT REFERENCES "locations" ("id") ON DELETE CASCADE,
    "partition_id" INT REFERENCES "partitions" ("id") ON DELETE CASCADE,
    "project_id" INT NOT NULL REFERENCES "projects" ("id") ON DELETE CASCADE,
    "site_id" INT REFERENCES "sites" ("id") ON DELETE CASCADE,
    "unit_id" INT REFERENCES "units" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "commissioning_assets" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "asset_id" INT NOT NULL REFERENCES "assets" ("id") ON DELETE CASCADE,
    "commissioning_record_id" INT NOT NULL REFERENCES "commissioning_records" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "commissioning_stages" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "stage" VARCHAR(100) NOT NULL,
    "status" VARCHAR(50) NOT NULL  DEFAULT 'not_started',
    "completed_by" VARCHAR(255),
    "completed_at" TIMESTAMPTZ,
    "witness_signature" TEXT,
    "signed_at" TIMESTAMPTZ,
    "conditional_acceptance" BOOL NOT NULL  DEFAULT False,
    "conditional_notes" TEXT,
    "commissioning_record_id" INT NOT NULL REFERENCES "commissioning_records" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "commissioning_checklist_items" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "description" TEXT NOT NULL,
    "result" VARCHAR(50),
    "measured_value" VARCHAR(255),
    "specified_value" VARCHAR(255),
    "notes" TEXT,
    "stage_id" INT NOT NULL REFERENCES "commissioning_stages" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "commissioning_evidence" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "type" VARCHAR(100) NOT NULL,
    "file_key" VARCHAR(500),
    "uploaded_by" VARCHAR(255) NOT NULL,
    "uploaded_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "document_id" INT REFERENCES "documents" ("id") ON DELETE CASCADE,
    "stage_id" INT NOT NULL REFERENCES "commissioning_stages" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "punch_items" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "description" TEXT NOT NULL,
    "severity" VARCHAR(50) NOT NULL,
    "status" VARCHAR(50) NOT NULL  DEFAULT 'open',
    "raised_by" VARCHAR(255) NOT NULL,
    "raised_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "closed_by" VARCHAR(255),
    "closed_at" TIMESTAMPTZ,
    "closure_notes" TEXT,
    "commissioning_record_id" INT NOT NULL REFERENCES "commissioning_records" ("id") ON DELETE CASCADE,
    "stage_id" INT REFERENCES "commissioning_stages" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
