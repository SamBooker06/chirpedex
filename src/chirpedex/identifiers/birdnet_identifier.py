import os
import sys

from contextlib import contextmanager, redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any, Iterator

from chirpedex.identifiers.identifier import BirdIdentifier
from chirpedex.location import Location
from chirpedex.models import BirdPrediction

MIN_CONFIDENCE = 0.25


class BirdNETIdentifier(BirdIdentifier):
    """Bird identification using BirdNET model."""

    @contextmanager
    def _suppress_library_output(self) -> Iterator[None]:
        """Suppress Python and native output emitted by BirdNET."""
        sys.stdout.flush()
        sys.stderr.flush()

        saved_stdout = os.dup(1)
        saved_stderr = os.dup(2)

        try:
            with open(os.devnull, "w", encoding="utf-8") as devnull:
                os.dup2(devnull.fileno(), 1)
                os.dup2(devnull.fileno(), 2)

                with redirect_stdout(devnull), redirect_stderr(devnull):
                    yield
                    sys.stdout.flush()
                    sys.stderr.flush()
        finally:
            os.dup2(saved_stdout, 1)
            os.dup2(saved_stderr, 2)
            os.close(saved_stdout)
            os.close(saved_stderr)

    def __init__(self, minimum_confidence: float = MIN_CONFIDENCE) -> None:
        """Initialise the BirdNET identifier."""
        self.minimum_confidence = minimum_confidence

        try:
            with self._suppress_library_output():
                from birdnetlib import Recording
                from birdnetlib.analyzer import Analyzer
        except ImportError as exc:
            from chirpedex.errors import ModelError

            message = str(exc)
            if "birdnetlib" in message:
                raise ModelError(
                    "birdnetlib is not installed. "
                    "Please install it with: pip install birdnetlib"
                ) from exc
            raise ImportError(
                f"A birdnetlib dependency is missing: {message}"
            ) from exc

        self._recording_class = Recording
        self._analyzer_class = Analyzer

        with self._suppress_library_output():
            self._analyser = self._analyzer_class()

    def identify_from_file(
            self,
            audio_path: Path,
            location: Location | None = None,
    ) -> BirdPrediction:
        """
        Identify a bird species using BirdNET.

        Args:
            audio_path: Path to the audio file.
            location: The location the recording took place

        Returns:
            BirdPrediction: The top prediction. from the model.

        Raises:
            IdentificationError: If identification fails.
        """
        from chirpedex.errors import IdentificationError

        try:
            with self._suppress_library_output():
                latitude = location.latitude if location else None
                longitude = location.longitude if location else None

                recording = self._recording_class(
                    self._analyser,
                    str(audio_path),
                    lat=latitude,
                    lon=longitude,
                    min_conf=self.minimum_confidence,
                )

                recording.analyze()

                results: list[Any] = recording.detection_list

                if not results:
                    raise IdentificationError("No bird species detected.")

                results.sort(key=lambda x: x.confidence, reverse=True)

                # Extract the top result
                top_result = results[0]
                confidence = top_result.confidence
                common_name = top_result.common_name
                scientific_name = top_result.scientific_name

                return BirdPrediction(
                    species_common_name=common_name,
                    species_scientific_name=scientific_name,
                    confidence=float(confidence),
                    source_audio_path=audio_path,
                )

        except IdentificationError:
            raise
        except FileNotFoundError as exc:
            raise IdentificationError(
                f"Could not find the bird species file: {audio_path}"
            ) from exc
        except Exception as e:
            raise IdentificationError(
                f"Failed to identify bird in {audio_path}: {e}"
            ) from e
