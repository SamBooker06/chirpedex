"""Tests for identifier module."""

import builtins
import io
import os
import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest

from chirpedex.errors import IdentificationError, ModelError
from chirpedex.models import BirdPrediction


def create_identifier():
    """Create an identifier without importing the real BirdNET dependency."""
    birdnetlib = ModuleType("birdnetlib")
    birdnetlib.RecordingFileObject = MagicMock()
    analyzer_module = ModuleType("birdnetlib.analyzer")
    analyzer_module.Analyzer = MagicMock()

    with patch.dict(
            "sys.modules",
            {
                "birdnetlib": birdnetlib,
                "birdnetlib.analyzer": analyzer_module,
            },
    ):
        from chirpedex.identifiers.birdnet_identifier import BirdNETIdentifier

        return BirdNETIdentifier()


class TestBirdNETIdentifier:
    """Test the BirdNETIdentifier class."""

    def test_identifier_init_no_birdnetlib(self) -> None:
        """Test that ModelError is raised if birdnetlib is not available."""
        real_import = builtins.__import__

        def import_without_birdnetlib(name, *args, **kwargs):
            if name == "birdnetlib" or name.startswith("birdnetlib."):
                raise ImportError("No module named 'birdnetlib'")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=import_without_birdnetlib):
            with pytest.raises(ModelError):
                from chirpedex.identifiers.birdnet_identifier import BirdNETIdentifier

                BirdNETIdentifier()

    def test_identify_success(self) -> None:
        """Test successful identification."""
        mock_recording = MagicMock()
        mock_recording.detection_list = [
            MagicMock(
                confidence=0.95,
                common_name="European Robin",
                scientific_name="Erithacus rubecula",
            )
        ]

        identifier = create_identifier()
        identifier._recording_class = MagicMock(return_value=mock_recording)
        result = identifier.identify_from_file(io.BytesIO(b"audio"))

        assert isinstance(result, BirdPrediction)
        assert result.species_common_name == "European Robin"
        assert result.species_scientific_name == "Erithacus rubecula"
        assert result.confidence == 0.95

    def test_identify_no_results(self) -> None:
        """Test identification with no results."""
        mock_recording = MagicMock()
        mock_recording.detection_list = []

        identifier = create_identifier()
        identifier._recording_class = MagicMock(return_value=mock_recording)

        with pytest.raises(IdentificationError, match="No bird species detected"):
            identifier.identify_from_file(io.BytesIO(b"audio"))

    def test_identify_exception_handling(self) -> None:
        """Test that exceptions are caught and wrapped."""
        identifier = create_identifier()
        identifier._recording_class = MagicMock(side_effect=RuntimeError("Test error"))

        with pytest.raises(IdentificationError, match="Test error"):
            identifier.identify_from_file(io.BytesIO(b"audio"))

    def test_suppresses_python_and_native_output(self, capfd) -> None:
        """Test BirdNET output does not leak to stdout or stderr."""
        def noisy_analyzer():
            print("analyzer stdout")
            print("analyzer stderr", file=sys.stderr)
            os.write(1, b"native analyzer stdout\n")
            os.write(2, b"native analyzer stderr\n")
            return MagicMock()

        birdnetlib = ModuleType("birdnetlib")
        analyzer_module = ModuleType("birdnetlib.analyzer")
        birdnetlib.RecordingFileObject = MagicMock()
        analyzer_module.Analyzer = noisy_analyzer

        with patch.dict(
            "sys.modules",
            {
                "birdnetlib": birdnetlib,
                "birdnetlib.analyzer": analyzer_module,
            },
        ):
            from chirpedex.identifiers.birdnet_identifier import BirdNETIdentifier

            identifier = BirdNETIdentifier()

        mock_recording = MagicMock()
        mock_recording.detection_list = [
            MagicMock(
                confidence=0.95,
                common_name="European Robin",
                scientific_name="Erithacus rubecula",
            )
        ]

        def noisy_analyze() -> None:
            print("analysis stdout")
            print("analysis stderr", file=sys.stderr)
            os.write(1, b"native analysis stdout\n")
            os.write(2, b"native analysis stderr\n")

        mock_recording.analyze.side_effect = noisy_analyze
        identifier._recording_class = MagicMock(return_value=mock_recording)
        identifier.identify_from_file(io.BytesIO(b"audio"))

        captured = capfd.readouterr()
        assert captured.out == ""
        assert captured.err == ""
