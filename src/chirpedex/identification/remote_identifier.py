"""
This will allow cli to run on a separate device than that which is responsible for processing the audio
"""
import io
import json
from typing import Optional

import httpx

from chirpedex.api import DEFAULT_API_PORT
from chirpedex.errors import IdentificationError
from chirpedex.identification.identifier import BirdIdentifier
from chirpedex.location import Location
from chirpedex.models import BirdPrediction


class RemoteIdentifier(BirdIdentifier):
    def __init__(self, host: str, port: int = DEFAULT_API_PORT):
        self.host = host
        self.port = port

    def identify_from_buffer(self, stream: io.BytesIO, location: Optional[Location] = None):
        raise NotImplementedError("PCM streaming not yet implemented.")

    def identify_from_file(self, audio_file: io.BytesIO, location: Location | None = None) -> BirdPrediction:
        with httpx.Client() as session:
            response = session.post(f"{self.host}:{self.port}/identify", files={"audio_file": audio_file})
            decoded_data = response.read().decode("utf-8")

            try:
                loaded_data = json.loads(decoded_data)
                return BirdPrediction.model_validate_json(loaded_data)
            except Exception as e:
                raise IdentificationError(f"Failed to parse JSON response: {e}") from e
