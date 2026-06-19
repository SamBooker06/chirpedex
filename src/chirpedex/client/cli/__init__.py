import argparse
import sys
from argparse import ArgumentError

from chirpedex.client.api import DEFAULT_API_PORT
from chirpedex.client.cli.factories import CommandFactory, IdentifyCommandFactory
from chirpedex.client.cli.exit_codes import ExitCode


def create_parser() -> argparse.ArgumentParser:
    """Create and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="chirpedex",
        description="A portable bird identification application.",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Identify command
    identify_parser = subparsers.add_parser(
        "identify",
        help="Identify a bird species from an audio file.",
    )
    identify_parser.add_argument(
        "audio_path",
        help="Path to the audio file to analyze.",
        nargs="+",
    )
    identify_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON.",
    )

    identify_parser.add_argument(
        "--remote",
        action="store_true",
        help="Use the remote API instead of the local one.",
    )
    identify_parser.add_argument(
        "--host",
        help="Host of the remote API.",
        default="http://localhost",
    )
    identify_parser.add_argument(
        "--no-register",
        help="Don't register any identified birds into the database.",
        action="store_true",
    )
    identify_parser.add_argument(
        "--port",
        help="Port of the remote API.",
        default=DEFAULT_API_PORT,
        type=int,
    )

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Serve a chirpedex application.")
    serve_parser.add_argument(
        "--port",
        "-p",
        help="Port to serve the chirpedex application.",
        default=DEFAULT_API_PORT,
        type=int
    )
    serve_parser.add_argument(
        "--host",
        help="Host to serve the chirpedex application.",
        default="0.0.0.0",
        type=str
    )
    serve_parser.add_argument(
        "--register",
        help="Register a bird species into the database.",
        action="store_true",
    )

    return parser


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return ExitCode.INVALID_ARGUMENT_ERROR_EXIT_CODE

    try:
        command = CommandFactory.create_command(args)
        result = command.execute()

        if isinstance(result.output, list):
            for output in result.output:
                print(output, end="\n\n")
        else:
            print(result.output)

        return result.exit_code

    except ArgumentError:
        parser.print_help()
        return ExitCode.INVALID_ARGUMENT_ERROR_EXIT_CODE

    except Exception as error:
        print(error)
        return ExitCode.CHIRPEDEX_ERROR_EXIT_CODE


if __name__ == "__main__":
    sys.exit(main())
