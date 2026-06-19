from typing import List

from chirpedex.core.db import ChirpedexRepository, BirdSightingCreate, BirdSighting


class NoRepo(ChirpedexRepository):
    def get_sightings_by_scientific_name(self, scientific_name: str) -> List[BirdSighting]:
        return []

    def get_sightings_by_common_name(self, common_name: str) -> List[BirdSighting]:
        return []

    def add_sighting(self, bird_sighting: BirdSightingCreate) -> None:
        pass