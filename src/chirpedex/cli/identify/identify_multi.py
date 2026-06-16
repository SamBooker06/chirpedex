from typing import List

from chirpedex.cli.command import CommandResult
from chirpedex.cli.identify.identify import IdentifyCommand
from chirpedex.cli.identify.identify_single import IdentifySingleCommand
from chirpedex.identification.identifier import BirdIdentifier
from chirpedex.cli.exit_codes import ExitCode
from chirpedex.models import BirdPrediction


class IdentifyMultiCommand(IdentifyCommand):
    """Identify multiple files."""

    def __init__(self, identifier: BirdIdentifier, paths: List[str]) -> None:
        super().__init__(identifier)

        assert isinstance(paths, list)
        assert all(isinstance(path, str) for path in paths)
        self._identification_command = IdentifySingleCommand(identifier, paths[0])
        self.paths = paths

    def execute(self) -> CommandResult[List[BirdPrediction] | str]:
        error_outputs: List[str] = []
        predictions: List[BirdPrediction] = []

        for path in self.paths:
            self._identification_command.file_path = path
            result = self._identification_command.execute()

            if result.is_error:
                assert isinstance(result.output, str)
                error_outputs.append(result.output)

            else:
                assert isinstance(result.output, BirdPrediction)
                predictions.append(result.output)

        if len(error_outputs) > 0:
            error_message = "One or more files failed to identify:\n\n" + "\n".join(error_outputs)
            command_result: CommandResult[str] = CommandResult(ExitCode.CHIRPEDEX_ERROR_EXIT_CODE, error_message, is_error=True)

        else:
            command_result: CommandResult[List[BirdPrediction]] = CommandResult(ExitCode.SUCCESS_EXIT_CODE, predictions)

        return command_result
