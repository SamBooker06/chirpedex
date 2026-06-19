from abc import ABC

from chirpedex.client.cli.command import Command
from chirpedex.client.identify_and_record_service import IdentifyAndRecordService
from chirpedex.core.identification import BirdIdentifier


class IdentifyCommand(Command, ABC):
    def __init__(self, identifier: IdentifyAndRecordService) -> None:
        self._identifier = identifier
