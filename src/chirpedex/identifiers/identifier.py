"""Bird identification interface and implementations."""

from abc import ABC, abstractmethod
from pathlib import Path

from chirpedex.location import Location
from chirpedex.models import BirdPrediction


class BirdIdentifier(ABC):
    """Abstract base class for bird identification backends."""

    @abstractmethod
    def identify_from_file(
        self,
        audio_path: Path,
        location: Location | None = None,
    ) -> BirdPrediction:
        """
        Identify a bird species from an audio file.

        Args:
            audio_path: Path to the audio file.
            location: The location the recording took place

        Returns:
            BirdPrediction: A prediction containing species info and confidence.

        Raises:
            IdentificationError: If identification fails.
        """
        raise NotImplementedError
