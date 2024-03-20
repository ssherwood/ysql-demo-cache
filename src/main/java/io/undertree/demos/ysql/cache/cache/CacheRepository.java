package io.undertree.demos.ysql.cache.cache;

import io.micrometer.core.annotation.Timed;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.jdbc.support.GeneratedKeyHolder;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public class CacheRepository {
    private static final Logger LOG = LoggerFactory.getLogger(CacheRepository.class);

    private final JdbcClient jdbcClient;

    public CacheRepository(JdbcClient jdbcClient) {
        this.jdbcClient = jdbcClient;
    }

    /**
     * A simple finder by the cache entity key (UUID).  This does not affect
     * the time to live (TTL) of the existing entity.  If an LRU-style cache
     * strategy is desired, then use the findWithTTL finder as it will touch
     * the `expires_at` column.
     * <p>
     * NOTE: this finder will not return any cache entries that are past their
     * `expires_at` date even if they have not yet been purged from the
     * database.
     *
     * @param key the UUID of the cache entry
     * @return Optional of the JSON cache entity
     */
    @Timed(value = "ysql.cache.find", description = "time to retrieve cache entry", percentiles = {0.5, 0.9, 0.99})
    public Optional<String> find(UUID key) {
        return jdbcClient.sql("""
                        SELECT value
                          FROM ysql_cache
                         WHERE id = ?
                           AND expires_at > NOW()
                        """)
                .param(key)
                .query(String.class)
                .optional();
    }

    /**
     * This finder touches the `expires_at` column to keep the element "alive"
     * in the cache for an additional period (TTL).  Use this finder to have
     * the elements in the cache behave more like an LRU-style cache.
     *
     * @param key        the UUID of the cache entry
     * @param timeToLive number of minutes to extend the entry's TTL
     * @return Optional of the JSON cache entity
     */
    @Timed(value = "ysql.cache.findWithTTL", description = "time to retrieve cache entry and update ttl", percentiles = {0.5, 0.9, 0.99})
    public Optional<String> findWithTTL(UUID key, int timeToLive) {
        var keyHolder = new GeneratedKeyHolder();
        jdbcClient.sql("""
                           UPDATE ysql_cache
                              SET expires_at = NOW() + (? || ' minutes')::interval
                            WHERE id = ?
                              AND expires_at > NOW()
                        RETURNING value::text
                        """)
                .params(timeToLive, key)
                .update(keyHolder, "value");
        return Optional.ofNullable(keyHolder.getKeyAs(String.class));
    }

    /**
     * @param json
     * @param timeToLive
     * @return
     */
    @Timed(value = "ysql.cache.insert", description = "time to retrieve cache entry and update ttl", percentiles = {0.5, 0.9, 0.99})
    public UUID insert(String json, int timeToLive) {
        var keyHolder = new GeneratedKeyHolder();
        jdbcClient.sql("""
                        INSERT INTO ysql_cache(value, expires_at)
                             VALUES(?::jsonb, NOW() + (? || ' minutes')::interval)
                        """)
                .params(json, timeToLive)
                .update(keyHolder, "id");
        return keyHolder.getKeyAs(UUID.class);
    }

    /**
     * @param key
     * @param json
     * @param timeToLive
     * @return
     */
    @Timed(value = "ysql.cache.update", description = "time to retrieve cache entry and update ttl", percentiles = {0.5, 0.9, 0.99})
    public int update(UUID key, String json, int timeToLive) {
        return jdbcClient.sql("""
                        UPDATE ysql_cache
                           SET value = ?::jsonb,
                               expires_at = NOW() + (? || ' minutes')::interval
                         WHERE id = ?
                        """)
                .params(json, timeToLive, key)
                .update();
    }

    /**
     * @param key the UUID of the cache entry to delete
     * @return count of the number of deleted (this normally usually be 1)
     */
    @Timed(value = "ysql.cache.delete", description = "time to retrieve cache entry and update ttl", percentiles = {0.5, 0.9, 0.99})
    public int delete(UUID key) {
        return jdbcClient.sql("""
                        DELETE FROM ysql_cache
                              WHERE id = ?
                        """)
                .param(key)
                .update();
    }
}
