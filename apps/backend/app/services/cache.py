from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class BalanceCacheEntry:
    balance: Decimal
    currency: str


class CacheBackend(Protocol):
    async def aget(self, key: str) -> bytes | None: ...
    async def aset(self, key: str, value: bytes, ttl: int | None = None) -> None: ...
    async def adelete(self, key: str) -> None: ...


class CacheService(ABC):
    @abstractmethod
    async def get_balance(self, *, user_id: str) -> BalanceCacheEntry | None: ...

    @abstractmethod
    async def set_balance(self, *, user_id: str, entry: BalanceCacheEntry, ttl: int | None = None) -> None: ...

    @abstractmethod
    async def delete_balance(self, *, user_id: str) -> None: ...