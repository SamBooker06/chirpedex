"""Bird identification interface and implementations."""
import io
from abc import ABC, abstractmethod, ABCMeta
from typing import IO, Optional

from chirpedex.location import Location
from chirpedex.models import BirdPrediction


class BirdIdentifier(ABC, metaclass=ABCMeta):
    """Abstract base class for bird identification backends."""

    MinimumConfidence = 0.25

    @abstractmethod
    def identify_from_file(
        self,
        audio_file: io.BytesIO,
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

    @abstractmethod
    def identify_from_buffer(self, stream: io.BytesIO, location: Optional[Location] = None):
        pass
