--
-- Assumptions:
-- The target database already exists.
-- Flyway will create the schema in the target database (see spring.flyway.default-schema)
--
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS ysql_cache
(
    id         uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    value      JSONB       NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT current_timestamp,
    expires_at timestamptz NOT NULL DEFAULT current_timestamp + (30 || ' minutes')::interval
);