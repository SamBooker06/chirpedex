from dataclasses import dataclass


@dataclass
class Location:
    """Bird location information."""
    longitude: float
    latitude: float
