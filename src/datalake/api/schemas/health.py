from typing import Literal

from pydantic import BaseModel


class LivenessResponse(BaseModel):
    status: Literal["alive"]
    service: str
    version: str


class ReadinessResponse(BaseModel):
    status: Literal["ready"]
    database: Literal["available"]