import os
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from collections import OrderedDict
import threading

class ContentCache:
    def __init__(self, max_size: int = 100, ttl_seconds: int = 300, max_file_size_mb: float = 10.0):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self._cache: OrderedDict = OrderedDict()
        self._access_times: Dict[str, float] = {}
        self._file_hashes: Dict[str, str] = {}
        self._lock = threading.Lock()
    
    def _generate_key(self, file_path: str, operation: str = 'read') -> str:
        """Generar clave única para cache"""
        abs_path = str(Path(file_path).resolve())
        return f"{operation}:{abs_path}"

    def _is_expired(self, key: str) -> bool:
        """Verificar si entrada cache expiró"""
        if key not in self._access_times:
            return True
        return (time.time() - self._access_times[key]) > self.ttl_seconds

    def _evict_lru(self) -> None:
        """Eliminar entrada menos recientemente usada"""
        if len(self._cache) >= self.max_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            self._access_times.pop(oldest_key, None)
            self._file_hashes.pop(oldest_key, None)

    def put(self, file_path: str, content: Any, operation: str = 'read') -> bool:
        """Almacenar contenido en cache"""
        key = self._generate_key(file_path, operation)
        with self._lock:
            self._evict_lru()
            self._cache[key] = content
            self._access_times[key] = time.time()
            return True

    def get(self, file_path: str, operation: str = 'read') -> Optional[Any]:
        """Recuperar contenido de cache"""
        key = self._generate_key(file_path, operation)
        with self._lock:
            if key in self._cache and not self._is_expired(key):
                # Move to end (mark as recently used)
                self._cache.move_to_end(key)
                self._access_times[key] = time.time()
                return self._cache[key]
        return None
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calcular hash archivo para detección cambios"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return str(time.time())  # Fallback timestamp

    def should_cache_file(self, file_path: str) -> bool:
        """Determinar si archivo debe cachearse"""
        try:
            file_size = Path(file_path).stat().st_size
            return file_size <= self.max_file_size_bytes
        except Exception:
            return False

    def get_cached_content(self, file_path: str, operation: str = 'read') -> Optional[Dict]:
        """Recuperar contenido con validación integridad"""
        if not self.should_cache_file(file_path):
            return None
        
        key = self._generate_key(file_path, operation)
        cached_data = self.get(file_path, operation)
        
        if cached_data:
            # Verificar si archivo cambió
            current_hash = self._calculate_file_hash(file_path)
            cached_hash = self._file_hashes.get(key)
            
            if cached_hash == current_hash:
                return cached_data
            else:
                # Archivo cambió, invalidar cache
                self.invalidate(file_path, operation)
        
        return None

    def cache_content(self, file_path: str, content: Dict, operation: str = 'read') -> bool:
        """Cachear contenido con hash integridad"""
        if not self.should_cache_file(file_path):
            return False
        
        key = self._generate_key(file_path, operation)
        file_hash = self._calculate_file_hash(file_path)
        
        self.put(file_path, content, operation)
        self._file_hashes[key] = file_hash
        return True

    def invalidate(self, file_path: str, operation: str = 'read') -> bool:
        """Invalidar entrada cache"""
        key = self._generate_key(file_path, operation)
        with self._lock:
            self._cache.pop(key, None)
            self._access_times.pop(key, None)
            self._file_hashes.pop(key, None)
            return True
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas cache"""
        with self._lock:
            total_entries = len(self._cache)
            expired_count = sum(1 for key in self._cache if self._is_expired(key))
            
            return {
                'total_entries': total_entries,
                'expired_entries': expired_count,
                'active_entries': total_entries - expired_count,
                'max_size': self.max_size,
                'ttl_seconds': self.ttl_seconds,
                'max_file_size_mb': self.max_file_size_bytes / (1024 * 1024)
            }

    def clear_expired(self) -> int:
        """Limpiar entradas expiradas"""
        removed = 0
        with self._lock:
            expired_keys = [key for key in self._cache if self._is_expired(key)]
            for key in expired_keys:
                del self._cache[key]
                self._access_times.pop(key, None)
                self._file_hashes.pop(key, None)
                removed += 1
        return removed

    def clear_all(self) -> None:
        """Limpiar todo el cache"""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
            self._file_hashes.clear()
    
    
    