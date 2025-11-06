/**
 * Sistema de caché simple en memoria para reducir llamadas API
 * OPTIMIZADO con deduplicación de requests
 */

interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

class SimpleCache {
  private cache: Map<string, CacheEntry<any>> = new Map();
  private ttl: number = 5 * 60 * 1000; // 5 minutos por defecto
  private pendingRequests: Map<string, Promise<any>> = new Map(); // Para deduplicación

  set<T>(key: string, data: T, customTtl?: number): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
    });
  }

  get<T>(key: string): T | null {
    const entry = this.cache.get(key);

    if (!entry) {
      return null;
    }

    // Verificar si expiró
    if (Date.now() - entry.timestamp > this.ttl) {
      this.cache.delete(key);
      return null;
    }

    return entry.data as T;
  }

  has(key: string): boolean {
    const entry = this.cache.get(key);
    if (!entry) return false;

    // Verificar si expiró
    if (Date.now() - entry.timestamp > this.ttl) {
      this.cache.delete(key);
      return false;
    }

    return true;
  }

  invalidate(key: string): void {
    this.cache.delete(key);
  }

  invalidatePattern(pattern: string): void {
    const keys = Array.from(this.cache.keys());
    keys.forEach(key => {
      if (key.includes(pattern)) {
        this.cache.delete(key);
      }
    });
  }

  clear(): void {
    this.cache.clear();
  }

  setTtl(ttl: number): void {
    this.ttl = ttl;
  }

  /**
   * OPTIMIZACIÓN: Deduplicación de requests
   * Si múltiples componentes solicitan el mismo dato simultáneamente,
   * solo se hace una llamada real al API
   */
  async fetch<T>(
    key: string,
    fetcher: () => Promise<T>,
    customTtl?: number
  ): Promise<T> {
    // 1. Verificar caché primero
    const cached = this.get<T>(key);
    if (cached !== null) {
      return cached;
    }

    // 2. Si ya hay una request pendiente para esta key, esperar esa
    const pending = this.pendingRequests.get(key);
    if (pending) {
      return pending as Promise<T>;
    }

    // 3. Hacer la request y cachearla
    const promise = fetcher()
      .then(data => {
        this.set(key, data, customTtl);
        this.pendingRequests.delete(key);
        return data;
      })
      .catch(error => {
        this.pendingRequests.delete(key);
        throw error;
      });

    this.pendingRequests.set(key, promise);
    return promise;
  }
}

export const apiCache = new SimpleCache();
