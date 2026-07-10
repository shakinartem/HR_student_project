from __future__ import annotations

from app.services.cache import CacheService
from app.services.memory_cache import MemoryCacheService

cache_service: CacheService = MemoryCacheService()