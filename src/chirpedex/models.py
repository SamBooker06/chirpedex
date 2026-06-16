"""Data models for bird predictions and sightings."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class BirdPrediction:
    """A prediction of a bird species from audio analysis."""

    species_common_name: str
    species_scientific_name: str | None = None
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    source_audio_path: Path | None = None

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        lines = [
            f"Species: {self.species_common_name}",
        ]
        if self.species_scientific_name:
            lines.append(f"Scientific name: {self.species_scientific_name}")
        lines.append(f"Confidence: {self.confidence:.2f}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "species_common_name": self.species_common_name,
            "species_scientific_name": self.species_scientific_name,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "source_audio_path": (
                str(self.source_audio_path)
                if self.source_audio_path is not None
                else None
            ),
        }


