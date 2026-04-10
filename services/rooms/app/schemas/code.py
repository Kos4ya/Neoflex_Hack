from pydantic import BaseModel

class CurrentCodeResponse(BaseModel):
    room_id: str
    code_body: str
    version: int


class UpdateCurrentCodeRequest(BaseModel):
    code_body: str = ""
    version: int | None = None