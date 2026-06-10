"""Audio file handling and validation."""

from pathlib import Path

from chirpedex.errors import FileNotFoundError_, InvalidAudioFormatError

# Supported audio formats
SUPPORTED_FORMATS = {".wav", ".mp3", ".flac", ".ogg", ".m4a"}


def validate_audio_file(audio_path: str | Path) -> Path:
    """
    Validate that an audio file exists and has a supported format.

    Args:
        audio_path: Path to the audio file.

    Returns:
        Path: The validated Path object.

    Raises:
        FileNotFoundError_: If the file does not exist.
        InvalidAudioFormatError: If the file format is not supported.
    """
    path = Path(audio_path)

    if not path.exists():
        raise FileNotFoundError_(f"Audio file not found: {audio_path}")

    if path.suffix.lower() not in SUPPORTED_FORMATS:
        raise InvalidAudioFormatError(
            f"Unsupported audio format: {path.suffix}. "
            f"Supported formats: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

    return path

