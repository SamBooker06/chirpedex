from chirpedex.cli.exit_codes import ExitCode
from chirpedex.cli.command import CommandResult


def handle_serve_command(host: str, port: int) -> CommandResult:
    try:
        from chirpedex.api.server import start_server

        start_server(host, port)

        return CommandResult("Server started successfully", ExitCode.SUCCESS_EXIT_CODE)

    except ImportError:
        return CommandResult("Could not start chirpedex server", ExitCode.IMPORT_ERROR_EXIT_CODE)
