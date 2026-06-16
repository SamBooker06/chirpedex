from abc import ABC

from chirpedex.cli.command import Command
from chirpedex.identification.identifier import BirdIdentifier


class IdentifyCommand(Command, ABC):
    def __init__(self, identifier: BirdIdentifier) -> None:
        self._identifier = identifier
