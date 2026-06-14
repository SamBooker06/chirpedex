from chirpedex.cli.command import CommandResult
from chirpedex.exit_codes import IMPORT_ERROR_EXIT_CODE, SUCCESS_EXIT_CODE


def handle_serve_command(host: str, port: int) -> CommandResult:
    try:
        from chirpedex.api.server import start_server

        start_server(host, port)

        return CommandResult("Server started successfully", SUCCESS_EXIT_CODE)

    except ImportError:
        return CommandResult("Could not start chirpedex server", IMPORT_ERROR_EXIT_CODE)
