"""Bird identification interface and implementations."""

from abc import ABC, abstractmethod
from typing import IO

from chirpedex.location import Location
from chirpedex.models import BirdPrediction


class BirdIdentifier(ABC):
    """Abstract base class for bird identification backends."""

    @abstractmethod
    def identify_from_file(
        self,
        audio_file: IO[bytes],
        location: Location | None = None,
    ) -> BirdPrediction:
        """
        Identify a bird species from an audio file.

        Args:
            audio_file: Binary audio file object.
            location: The location the recording took place

        Returns:
            BirdPrediction: A prediction containing species info and confidence.

        Raises:
            IdentificationError: If identification fails.
        """
        raise NotImplementedError
