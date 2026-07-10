from __future__ import annotations

import threading
from decimal import Decimal
from typing import Optional

from app.services.cache import BalanceCacheEntry, CacheBackend, CacheService


class _MemoryCacheBackend:
    def __init__(self) -> None:
        self._store: dict[str, tuple[bytes, Optional[int]]] = {}
        self._lock = threading.Lock()

    async def aget(self, key: str) -> bytes | None:
        with self._lock:
            item = self._store.get(key)
            if item is None:
                return None
            return item[0]

    async def aset(self, key: str, value: bytes, ttl: int | None = None) -> None:
        with self._lock:
            self._store[key] = (value, ttl)

    async def adelete(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)


def _encode_entry(entry: BalanceCacheEntry) -> bytes:
    return f"{entry.balance}:{entry.currency}".encode()


def _decode_entry(raw: bytes) -> BalanceCacheEntry:
    balance_str, currency = raw.split(b":", 1)
    return BalanceCacheEntry(balance=Decimal(balance_str.decode()), currency=currency.decode())


class MemoryCacheService(CacheService):
    def __init__(self) -> None:
        self._backend = _MemoryCacheBackend()

    async def get_balance(self, *, user_id: str) -> BalanceCacheEntry | None:
        raw = await self._backend.aget(f"balance:{user_id}")
        if raw is None:
            return None
        return _decode_entry(raw)

    async def set_balance(self, *, user_id: str, entry: BalanceCacheEntry, ttl: int | None = None) -> None:
        await self._backend.aset(f"balance:{user_id}", _encode_entry(entry), ttl=ttl)

    async def delete_balance(self, *, user_id: str) -> None:
        await self._backend.adelete(f"balance:{user_id}")