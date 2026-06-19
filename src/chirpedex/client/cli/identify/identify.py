from abc import ABC

from chirpedex.core.cli.command import Command
from chirpedex.core.identification.identifier import BirdIdentifier


class IdentifyCommand(Command, ABC):
    def __init__(self, identifier: BirdIdentifier) -> None:
        self._identifier = identifier
