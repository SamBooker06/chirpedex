"""Tests for audio module."""

from pathlib import Path

import pytest

from chirpedex.audio import validate_audio_file, SUPPORTED_FORMATS
from chirpedex.errors import FileNotFoundError_, InvalidAudioFormatError


def test_supported_formats() -> None:
    """Test that supported formats are defined."""
    assert SUPPORTED_FORMATS
    assert ".wav" in SUPPORTED_FORMATS
    assert ".mp3" in SUPPORTED_FORMATS


def test_validate_audio_file_not_found() -> None:
    """Test validation with non-existent file."""
    with pytest.raises(FileNotFoundError_):
        validate_audio_file("nonexistent_file.wav")


def test_validate_audio_file_invalid_format(tmp_path) -> None:
    """Test validation with unsupported format."""
    # Create a temporary file with unsupported extension
    test_file = tmp_path / "test.txt"
    test_file.touch()

    with pytest.raises(InvalidAudioFormatError):
        validate_audio_file(test_file)


def test_validate_audio_file_valid_wav(tmp_path) -> None:
    """Test validation with valid WAV file."""
    test_file = tmp_path / "test.wav"
    test_file.touch()

    result = validate_audio_file(test_file)
    assert result == test_file


def test_validate_audio_file_valid_mp3(tmp_path) -> None:
    """Test validation with valid MP3 file."""
    test_file = tmp_path / "test.mp3"
    test_file.touch()

    result = validate_audio_file(test_file)
    assert result == test_file


def test_validate_audio_file_case_insensitive(tmp_path) -> None:
    """Test that format validation is case insensitive."""
    test_file = tmp_path / "test.WAV"
    test_file.touch()

    result = validate_audio_file(test_file)
    assert result == test_file


def test_validate_audio_file_accepts_string() -> None:
    """Test that validate_audio_file accepts both Path and string."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        test_file = tmp_path / "test.wav"
        test_file.touch()

        # Test with Path object
        result_path = validate_audio_file(test_file)
        assert isinstance(result_path, Path)

        # Test with string
        result_str = validate_audio_file(str(test_file))
        assert isinstance(result_str, Path)

