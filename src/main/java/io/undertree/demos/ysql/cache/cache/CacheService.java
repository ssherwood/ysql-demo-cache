package io.undertree.demos.ysql.cache.cache;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;
import java.util.UUID;

@Service
public class CacheService {
    private final CacheRepository cacheRepository;
    private final ObjectMapper objectMapper;

    public CacheService(CacheRepository cacheRepository, ObjectMapper objectMapper) {
        this.cacheRepository = cacheRepository;
        this.objectMapper = objectMapper;
    }

    @Transactional(readOnly = true)
    public Optional<String> find(UUID key) {
        return cacheRepository.find(key);
    }

    @Transactional
    public Optional<String> findWithTTL(UUID key, int timeToLive) {
        validateTTL(timeToLive);
        return cacheRepository.findWithTTL(key, timeToLive);
    }

    @Transactional
    public UUID insert(String json, int timeToLive) {
        validateJson(json);
        validateTTL(timeToLive);
        return cacheRepository.insert(json, timeToLive);
    }

    @Transactional
    public int update(UUID key, String json, int timeToLive) {
        validateJson(json);
        validateTTL(timeToLive);
        return cacheRepository.update(key, json, timeToLive);
    }

    @Transactional
    public int delete(UUID key) {
        return cacheRepository.delete(key);
    }

    private void validateJson(String json) {
        try {
            objectMapper.readTree(json);
        } catch (JsonProcessingException e) {
            throw new IllegalArgumentException("Invalid JSON", e);
        }
    }

    private void validateTTL(int timeToLive) {
        if (timeToLive < 1) {
            throw new IllegalArgumentException("Invalid TTL");
        }
    }
}
