import asyncio
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RoomState:
    room_id: str
    code_body: str = ""
    version: int = 0
    last_persisted_version: int = 0
    save_task: Optional[asyncio.Task] = None
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)