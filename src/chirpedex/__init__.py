"""
Chirpedex: A portable bird identification application.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("chirpedex")
except PackageNotFoundError:
    __version__ = "0.0.0"
