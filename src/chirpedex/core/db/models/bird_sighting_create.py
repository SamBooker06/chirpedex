from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from chirpedex.core.location import Location


class BirdSightingCreate(BaseModel):
    scientific_name: str
    common_name: str
    location: Optional[Location] = None
    timestamp: datetime