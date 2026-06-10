"""Bird identification interface and implementations."""

from abc import ABC, abstractmethod
from pathlib import Path

from chirpedex.models import BirdPrediction


class BirdIdentifier(ABC):
    """Abstract base class for bird identification backends."""

    @abstractmethod
    def identify(self, audio_path: Path) -> BirdPrediction:
        """
        Identify a bird species from an audio file.

        Args:
            audio_path: Path to the audio file.

        Returns:
            BirdPrediction: A prediction containing species info and confidence.

        Raises:
            IdentificationError: If identification fails.
        """
        pass


class BirdNETIdentifier(BirdIdentifier):
    """Bird identification using BirdNET model."""

    def __init__(self) -> None:
        """Initialize the BirdNET identifier."""
        try:
            from birdnetlib import Recording
            from birdnetlib.analyzer import Analyzer
        except ImportError as e:
            from chirpedex.errors import ModelError

            raise ModelError(
                "birdnetlib is not installed. "
                "Please install it with: pip install birdnetlib"
            ) from e

        self._Recording = Recording
        self._Analyzer = Analyzer

    def identify(self, audio_path: Path) -> BirdPrediction:
        """
        Identify a bird species using BirdNET.

        Args:
            audio_path: Path to the audio file.

        Returns:
            BirdPrediction: The top prediction. from the model.

        Raises:
            IdentificationError: If identification fails.
        """
        from chirpedex.errors import IdentificationError

        try:
            # Create a Recording object
            recording = self._Recording(str(audio_path))

            # Run the analyzer
            analyzer = self._Analyzer()
            analyzer.process_recording(recording)

            # Get the results
            results = analyzer.get_results()

            if not results:
                raise IdentificationError(
                    f"No bird predictions returned for {audio_path}"
                )

            # Extract the top result
            top_result = results[0]
            confidence = top_result.get("confidence", 0.0)
            common_name = top_result.get("common_name", "Unknown")
            scientific_name = top_result.get("scientific_name")

            return BirdPrediction(
                species_common_name=common_name,
                species_scientific_name=scientific_name,
                confidence=float(confidence),
                source_audio_path=audio_path,
            )

        except IdentificationError:
            raise
        except Exception as e:
            raise IdentificationError(
                f"Failed to identify bird in {audio_path}: {e}"
            ) from e

