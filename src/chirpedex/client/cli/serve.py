from chirpedex.client.cli.exit_codes import ExitCode
from chirpedex.client.cli.command import CommandResult, Command


class ServeCommand(Command):
    def __init__(self, host: str, port: int):
        super().__init__()

        self.host = host
        self.port = port

    def execute(self) -> CommandResult:
        try:
            from chirpedex.client.api.server import start_server

            start_server(self.host, self.port)

            return CommandResult(ExitCode.SUCCESS_EXIT_CODE, "")

        except ImportError:
            return CommandResult(ExitCode.IMPORT_ERROR_EXIT_CODE, "Could not start chirpedex server", is_error=True)
