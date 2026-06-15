"""Command-line interface for Chirpedex."""

import argparse
import sys

from chirpedex.api import DEFAULT_API_PORT
from chirpedex.cli.api import handle_serve_command
from chirpedex.cli.identify import handle_identify, handle_multi_identify
from chirpedex.exit_codes import SUCCESS_EXIT_CODE


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

    return parser


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "identify":
        if len(args.audio_path) > 1:
            result = handle_multi_identify(args.audio_path, args.json)
        else:
            result = handle_identify(args.audio_path[0], args.json)

        if result.output:
            stream = sys.stderr if result.is_error else sys.stdout
            print(result.output, file=stream)
        return result.exit_code

    elif args.command == "serve":
        result = handle_serve_command(args.host, args.port)

        return result.exit_code

    parser.print_help()
    return SUCCESS_EXIT_CODE


if __name__ == "__main__":
    sys.exit(main())
