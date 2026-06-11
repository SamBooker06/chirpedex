"""Command-line interface for Chirpedex."""

import argparse
import sys

from chirpedex.audio import validate_audio_file
from chirpedex.errors import ChirpedexError, ModelError
from chirpedex.exit_codes import MODEL_ERROR_EXIT_CODE, SUCCESS_EXIT_CODE, CHIRPEDEX_ERROR_EXIT_CODE, \
    GENERIC_ERROR_EXIT_CODE, IMPORT_ERROR_EXIT_CODE
from chirpedex.identifier import BirdNETIdentifier


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
    )
    identify_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON (not yet implemented).",
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
        return handle_identify(args.audio_path, args.json)

    parser.print_help()
    return 0


def handle_identify(audio_path: str, json_output: bool = False) -> int:
    try:
        # Validate the audio file
        validated_path = validate_audio_file(audio_path)

        # Initialise the identifier
        identifier = BirdNETIdentifier()

        # Run identification
        prediction = identifier.identify_from_file(validated_path)

        # Output result
        if json_output:
            import json

            output = {
                "species_common_name": prediction.species_common_name,
                "species_scientific_name": prediction.species_scientific_name,
                "confidence": prediction.confidence,
                "timestamp": prediction.timestamp.isoformat(),
                "source_audio_path": str(prediction.source_audio_path),
            }
            print(json.dumps(output, indent=2))
        else:
            print(prediction)

        return SUCCESS_EXIT_CODE

    except ModelError as e:
        print(f"Model Error: {e}", file=sys.stderr)
        print(
            "Note: First run may download the BirdNET model (~1 GB).",
            file=sys.stderr,
        )
        return MODEL_ERROR_EXIT_CODE

    except ChirpedexError as e:
        print(f"Error: {e}", file=sys.stderr)
        return CHIRPEDEX_ERROR_EXIT_CODE
    except ImportError as e:
        print(f"ImportError: {e}", file=sys.stderr)

        return IMPORT_ERROR_EXIT_CODE

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return GENERIC_ERROR_EXIT_CODE
    """
    Handle the identify command.

    Args:
        audio_path: Path to the audio file.
        json_output: Whether to output as JSON.

    Returns:
        Exit code (0 for success, non-zero for error).
    """


if __name__ == "__main__":
    sys.exit(main())
