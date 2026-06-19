from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from chirpedex.core.location import Location


class BirdSighting(BaseModel):
    bird_id: int
    timestamp: datetime
    location: Optional[Location]
    species_common_name: str
    species_scientific_name: str
