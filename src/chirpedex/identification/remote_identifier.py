"""
This will allow cli to run on a separate device than that which is responsible for processing the audio
"""
import io
from typing import Optional

import httpx

from chirpedex.api import DEFAULT_API_PORT
from chirpedex.identification.identifier import BirdIdentifier
from chirpedex.location import Location
from chirpedex.models import BirdPrediction


class RemoteIdentifier(BirdIdentifier):
    def __init__(self, host: str, port: int = DEFAULT_API_PORT):
        self.host = host
        self.port = port

    def identify_from_buffer(self, stream: io.BytesIO, location: Optional[Location] = None):
        raise NotImplementedError("PCM streaming not yet implemented.")

    async def identify_from_file(self, audio_file: io.BytesIO, location: Location | None = None) -> BirdPrediction:
        async with httpx.AsyncClient() as session:
            response = await session.post(f"{self.host}:{self.port}/identify", files={"audio_file": audio_file})
            data = await response.aread()
