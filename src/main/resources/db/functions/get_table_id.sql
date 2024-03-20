--
--
--
CREATE OR REPLACE FUNCTION get_table_id(schema_name_p VARCHAR, table_name_p VARCHAR) RETURNS VARCHAR
AS
$$
SELECT '0000' || lpad(to_hex(d.oid::int), 4, '0') || '00003000800000000000' || lpad(to_hex(c.oid::int), 4, '0') tableid
FROM pg_class c,
     pg_namespace n,
     pg_database d
WHERE n.nspname = $1
  AND c.relname = $2
  AND d.datname = current_database();
$$ LANGUAGE SQL;