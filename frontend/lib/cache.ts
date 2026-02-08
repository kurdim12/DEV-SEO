/**
 * Simple client-side cache with TTL support
 */

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

class Cache {
  private storage: Map<string, CacheEntry<unknown>> = new Map();

  /**
   * Get cached data if it exists and hasn't expired
   */
  get<T>(key: string): T | null {
    const entry = this.storage.get(key);

    if (!entry) {
      return null;
    }

    const now = Date.now();
    const age = now - entry.timestamp;

    if (age > entry.ttl) {
      // Entry has expired
      this.storage.delete(key);
      return null;
    }

    return entry.data as T;
  }

  /**
   * Set cache data with TTL (time to live in milliseconds)
   */
  set<T>(key: string, data: T, ttl: number = 60000): void {
    this.storage.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });
  }

  /**
   * Manually invalidate cache entry
   */
  invalidate(key: string): void {
    this.storage.delete(key);
  }

  /**
   * Clear all cache entries
   */
  clear(): void {
    this.storage.clear();
  }

  /**
   * Clear expired entries
   */
  cleanup(): void {
    const now = Date.now();
    for (const [key, entry] of this.storage.entries()) {
      const age = now - entry.timestamp;
      if (age > entry.ttl) {
        this.storage.delete(key);
      }
    }
  }
}

// Global cache instance
export const cache = new Cache();

// Run cleanup every 5 minutes
if (typeof window !== 'undefined') {
  setInterval(() => {
    cache.cleanup();
  }, 5 * 60 * 1000);
}

/**
 * Cache key builder for API endpoints
 */
export const CacheKeys = {
  dashboardStats: (userId: string) => `dashboard:stats:${userId}`,
  websites: (userId: string) => `websites:list:${userId}`,
  website: (websiteId: string) => `website:${websiteId}`,
  crawlHistory: (websiteId: string) => `crawl:history:${websiteId}`,
  report: (reportId: string) => `report:${reportId}`,
};

/**
 * Cache TTL constants (in milliseconds)
 */
export const CacheTTL = {
  SHORT: 30 * 1000, // 30 seconds
  MEDIUM: 5 * 60 * 1000, // 5 minutes
  LONG: 30 * 60 * 1000, // 30 minutes
};
