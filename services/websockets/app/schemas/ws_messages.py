from typing import Literal, Optional
from pydantic import BaseModel, Field


class EditorInitMessage(BaseModel):
    type: Literal["editor.init"] = "editor.init"
    room_id: str
    role: Literal["candidate", "interviewer"]
    read_only: bool
    code_body: str
    version: int


class EditorUpdateMessage(BaseModel):
    type: Literal["editor.update"] = "editor.update"
    room_id: str
    code_body: str = Field(default="")
    client_version: Optional[int] = None


class EditorSyncedMessage(BaseModel):
    type: Literal["editor.synced"] = "editor.synced"
    room_id: str
    code_body: str
    version: int
    updated_by: str


class ErrorMessage(BaseModel):
    type: Literal["error"] = "error"
    code: str
    message: str


class PresenceMessage(BaseModel):
    type: Literal["presence"] = "presence"
    room_id: str
    online_count: int