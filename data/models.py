from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class CrimeIncident(BaseModel):
    lat: float
    long: float
    offense: str
    category: Optional[str] = None
    reportedDate: Optional[datetime] = None
    neighborhood: Optional[str] = None
    address: Optional[str] = None
    precinct: Optional[str] = None

    @field_validator("lat", "long")
    @classmethod
    def coords_must_be_nonzero(cls, v: float) -> float:
        if v == 0:
            raise ValueError("Coordinate cannot be zero")
        return v
