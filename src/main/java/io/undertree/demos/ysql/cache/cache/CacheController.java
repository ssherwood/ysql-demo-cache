package io.undertree.demos.ysql.cache.cache;

import org.springframework.http.CacheControl;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

import java.util.UUID;
import java.util.concurrent.TimeUnit;

@RestController
@RequestMapping("/api/cache")
public class CacheController {
    private final CacheService cacheService;

    public CacheController(CacheService cacheService) {
        this.cacheService = cacheService;
    }

    @GetMapping(value = "/{key}", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<String> find(@PathVariable UUID key) {
        return ResponseEntity.of(cacheService.find(key));
    }

    /**
     * Alternate cache finder with the side effect of touching the entry's time
     * to live (ttl).  This technically makes the GET non-idempotent.
     *
     * @param key
     * @param timeToLive
     * @return
     */
    @GetMapping(value = "/alt/{key}", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<String> find(@PathVariable UUID key, @RequestParam(value = "ttl", defaultValue = "30") int timeToLive) {
        return cacheService.findWithTTL(key, timeToLive)
                .map(response -> ResponseEntity
                        .status(HttpStatus.OK)
                        //.cacheControl(CacheControl.maxAge(timeToLive, TimeUnit.MINUTES))
                        .body(response))
                .orElseGet(() -> ResponseEntity.notFound().build());
    }

    @PostMapping()
    public ResponseEntity<UUID> insert(@RequestBody String json, @RequestParam(value = "ttl", defaultValue = "30") int timeToLive) {
        var key = cacheService.insert(json, timeToLive);
        return ResponseEntity
                .created(ServletUriComponentsBuilder.fromCurrentRequest().path("/{id}").buildAndExpand(key).toUri())
                .body(key);
    }

    @PutMapping("/{key}")
    public ResponseEntity<Void> update(@PathVariable UUID key, @RequestBody String json, @RequestParam(value = "ttl", defaultValue = "30") int timeToLive) {
        if (cacheService.update(key, json, timeToLive) == 1) {
            return ResponseEntity.noContent().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    @DeleteMapping("/{key}")
    public ResponseEntity<Void> delete(@PathVariable UUID key) {
        if (cacheService.delete(key) == 1) {
            return ResponseEntity.noContent().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }
}
