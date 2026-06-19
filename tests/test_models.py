"""Tests for models module."""

from datetime import datetime
from pathlib import Path

from chirpedex.core.models import BirdPrediction


def test_bird_prediction_basic() -> None:
    """Test creating a basic BirdPrediction."""
    pred = BirdPrediction(
        species_common_name="European Robin",
        species_scientific_name="Erithacus rubecula",
        confidence=0.95,
    )

    assert pred.species_common_name == "European Robin"
    assert pred.species_scientific_name == "Erithacus rubecula"
    assert pred.confidence == 0.95


def test_bird_prediction_with_path() -> None:
    """Test BirdPrediction with audio path."""
    test_path = Path("robin.wav")
    pred = BirdPrediction(
        species_common_name="Great Tit",
        species_scientific_name="Parus major",
        confidence=0.87,
        source_audio_path=test_path,
    )

    assert pred.source_audio_path == test_path


def test_bird_prediction_default_timestamp() -> None:
    """Test that timestamp defaults to current time."""
    before = datetime.now()
    pred = BirdPrediction(
        species_common_name="Blackbird",
        species_scientific_name="Turdus merula",
    )
    after = datetime.now()

    assert before <= pred.timestamp <= after


def test_bird_prediction_custom_timestamp() -> None:
    """Test BirdPrediction with custom timestamp."""
    custom_time = datetime(2024, 1, 1, 12, 0, 0)
    pred = BirdPrediction(
        species_common_name="Sparrow",
        species_scientific_name="Passer domesticus",
        confidence=0.75,
        timestamp=custom_time,
    )

    assert pred.timestamp == custom_time


def test_bird_prediction() -> None:
    """Test string representation with scientific name."""
    pred = BirdPrediction(
        species_common_name="European Robin",
        species_scientific_name="Erithacus rubecula",
        confidence=0.92,
    )

    output = str(pred)
    assert "Species: European Robin" in output
    assert "Scientific name: Erithacus rubecula" in output
    assert "Confidence: 0.92" in output



