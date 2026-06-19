"""Custom exceptions for Chirpedex."""


class ChirpedexError(Exception):
    """Base exception for all Chirpedex errors."""

    pass


class AudioFileError(ChirpedexError):
    """Raised when there is an issue with the audio file."""

    pass


class FileNotFoundError_(ChirpedexError):
    """Raised when an audio file cannot be found."""

    pass


class InvalidAudioFormatError(ChirpedexError):
    """Raised when an audio file format is not supported."""

    pass


class IdentificationError(ChirpedexError):
    """Raised when bird identification fails."""

    pass


class ModelError(ChirpedexError):
    """Raised when the model is unavailable or fails to load."""

    pass

