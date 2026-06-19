from abc import ABC, abstractmethod
from typing import List

from chirpedex.core.db.models.bird_sighting import BirdSighting
from chirpedex.core.db.models.bird_sighting_create import BirdSightingCreate


class ChirpedexRepository(ABC):
    @abstractmethod
    def get_sightings_by_scientific_name(self, scientific_name: str) -> List[BirdSighting]:
        raise NotImplementedError

    @abstractmethod
    def get_sightings_by_common_name(self, common_name: str) -> List[BirdSighting]:
        raise NotImplementedError

    @abstractmethod
    def add_sighting(self, bird_sighting: BirdSightingCreate) -> None:
        raise NotImplementedError
