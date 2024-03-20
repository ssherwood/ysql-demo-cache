---
--- https://www.postgresql.org/docs/current/errcodes-appendix.html
---
CREATE FUNCTION raise_error(errcode text default 'raise_exception',
                            message text default 'Generic exception') RETURNS boolean
    LANGUAGE plpgsql AS
$$
BEGIN
    RAISE EXCEPTION USING
        errcode = coalesce(errcode, 'raise_exception'),
        message = coalesce(message, 'Generic exception');
    RETURN true;
END;
$$;