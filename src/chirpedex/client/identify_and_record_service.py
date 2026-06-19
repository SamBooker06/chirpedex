from io import BytesIO

from chirpedex.core.db import ChirpedexRepository, BirdSighting
from chirpedex.core.db.models.bird_sighting_create import BirdSightingCreate
from chirpedex.core.identification import BirdIdentifier
from chirpedex.core.location import Location
from chirpedex.core.models import BirdPrediction


class IdentifyAndRecordService:
    def __init__(self, identifier: BirdIdentifier, repository: ChirpedexRepository):
        self._identifier = identifier
        self._repo = repository

    def identify_from_file(self, audio_file: BytesIO, location: Location | None = None) -> BirdPrediction:
        prediction = self._identifier.identify_from_file(audio_file, location)

        sighting = BirdSightingCreate(scientific_name=prediction.species_scientific_name,
                                      common_name=prediction.species_common_name, location=location,
                                      timestamp=prediction.timestamp)

        self._repo.add_sighting(sighting)

        return prediction
