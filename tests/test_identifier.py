"""Tests for identifier module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from chirpedex.errors import IdentificationError, ModelError
from chirpedex.models import BirdPrediction


class TestBirdNETIdentifier:
    """Test the BirdNETIdentifier class."""

    def test_identifier_init_no_birdnetlib(self) -> None:
        """Test that ModelError is raised if birdnetlib is not available."""
        with patch("chirpedex.identifier.birdnetlib", side_effect=ImportError):
            with pytest.raises(ModelError):
                from chirpedex.identifier import BirdNETIdentifier

                BirdNETIdentifier()

    @patch("chirpedex.identifier.Analyzer")
    @patch("chirpedex.identifier.Recording")
    def test_identify_success(self, mock_recording_class, mock_analyzer_class) -> None:
        """Test successful identification."""
        # Setup mocks
        mock_recording = MagicMock()
        mock_recording_class.return_value = mock_recording

        mock_analyzer = MagicMock()
        mock_analyzer_class.return_value = mock_analyzer
        mock_analyzer.get_results.return_value = [
            {
                "confidence": 0.95,
                "common_name": "European Robin",
                "scientific_name": "Erithacus rubecula",
            }
        ]

        # Mock the import
        with patch.dict(
            "sys.modules",
            {"birdnetlib": MagicMock(), "birdnetlib.analyzer": MagicMock()},
        ):
            from chirpedex.identifier import BirdNETIdentifier

            identifier = BirdNETIdentifier()
            result = identifier.identify(Path("test.wav"))

            assert isinstance(result, BirdPrediction)
            assert result.species_common_name == "European Robin"
            assert result.species_scientific_name == "Erithacus rubecula"
            assert result.confidence == 0.95

    @patch("chirpedex.identifier.Analyzer")
    @patch("chirpedex.identifier.Recording")
    def test_identify_no_results(
        self, mock_recording_class, mock_analyzer_class
    ) -> None:
        """Test identification with no results."""
        # Setup mocks
        mock_recording = MagicMock()
        mock_recording_class.return_value = mock_recording

        mock_analyzer = MagicMock()
        mock_analyzer_class.return_value = mock_analyzer
        mock_analyzer.get_results.return_value = []

        # Mock the import
        with patch.dict(
            "sys.modules",
            {"birdnetlib": MagicMock(), "birdnetlib.analyzer": MagicMock()},
        ):
            from chirpedex.identifier import BirdNETIdentifier

            identifier = BirdNETIdentifier()

            with pytest.raises(IdentificationError):
                identifier.identify(Path("test.wav"))

    @patch("chirpedex.identifier.Analyzer")
    @patch("chirpedex.identifier.Recording")
    def test_identify_exception_handling(
        self, mock_recording_class, mock_analyzer_class
    ) -> None:
        """Test that exceptions are caught and wrapped."""
        # Setup mocks to raise an exception
        mock_recording_class.side_effect = RuntimeError("Test error")

        # Mock the import
        with patch.dict(
            "sys.modules",
            {"birdnetlib": MagicMock(), "birdnetlib.analyzer": MagicMock()},
        ):
            from chirpedex.identifier import BirdNETIdentifier

            identifier = BirdNETIdentifier()

            with pytest.raises(IdentificationError):
                identifier.identify(Path("test.wav"))

