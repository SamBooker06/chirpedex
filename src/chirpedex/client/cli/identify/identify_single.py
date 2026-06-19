from io import BytesIO

from chirpedex.client.cli.command import CommandResult
from chirpedex.client.cli.exit_codes import ExitCode
from chirpedex.client.cli.identify.identify import IdentifyCommand
from chirpedex.client.identify_and_record_service import IdentifyAndRecordService
from chirpedex.core.identification import BirdIdentifier
from chirpedex.core.models import BirdPrediction


class IdentifySingleCommand(IdentifyCommand):
    def __init__(self, identification_service: IdentifyAndRecordService, file_path: str):
        super().__init__(identification_service)

        assert isinstance(file_path, str)
        self.file_path = file_path

    def execute(self) -> CommandResult[BirdPrediction | str]:
        try:
            with open(self.file_path, "rb") as fh:
                with BytesIO(fh.read()) as f:
                    identification_result = self._identifier.identify_from_file(f)

                    if identification_result.confidence > BirdIdentifier.MinimumConfidence:
                        command_result: CommandResult[BirdPrediction] = CommandResult(ExitCode.SUCCESS_EXIT_CODE,
                                                                                      output=identification_result)

                    else:
                        command_result: CommandResult[str] = CommandResult(output="No bird species detected",
                                                                           exit_code=ExitCode.CHIRPEDEX_ERROR_EXIT_CODE,
                                                                           is_error=True)

                    return command_result

        except FileNotFoundError as e:
            raise e
            command_result = CommandResult(ExitCode.FILE_NOT_FOUND_ERROR_EXIT_CODE, str(e), is_error=True)

        except Exception as e:
            raise e
            command_result = CommandResult(ExitCode.CHIRPEDEX_ERROR_EXIT_CODE, str(e), is_error=True)

        finally:
            return command_result
