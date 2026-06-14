import json
from pathlib import Path
from typing import Sequence

from chirpedex.audio import validate_audio_file
from chirpedex.cli.command import CommandResult
from chirpedex.errors import ModelError, FileNotFoundError_, ChirpedexError
from chirpedex.exit_codes import MODEL_ERROR_EXIT_CODE, FILE_NOT_FOUND_ERROR_EXIT_CODE, CHIRPEDEX_ERROR_EXIT_CODE, \
    IMPORT_ERROR_EXIT_CODE, GENERIC_ERROR_EXIT_CODE, SUCCESS_EXIT_CODE

from chirpedex.identifiers.birdnet_identifier import BirdNETIdentifier
from chirpedex.models import BirdPrediction


def _prediction_to_dict(prediction: BirdPrediction) -> dict[str, object]:
    """Convert a prediction to a JSON-serialisable dictionary."""
    return {
        "species_common_name": prediction.species_common_name,
        "species_scientific_name": prediction.species_scientific_name,
        "confidence": prediction.confidence,
        "timestamp": prediction.timestamp.isoformat(),
        "source_audio_path": (
            str(prediction.source_audio_path)
            if prediction.source_audio_path is not None
            else None
        ),
    }


def _format_prediction(
        prediction: BirdPrediction,
        json_output: bool,
) -> str:
    """Render a prediction for CLI output."""
    if json_output:
        return json.dumps(_prediction_to_dict(prediction), indent=2)
    return str(prediction)


def _identify(
        audio_path: Path,
        identifier: BirdNETIdentifier,
) -> BirdPrediction:
    """Identify one validated audio file."""
    return identifier.identify_from_file(audio_path)


def _error_result(exc: Exception) -> CommandResult:
    """Convert a command exception into output and an exit code."""
    if isinstance(exc, ModelError):
        return CommandResult(
            output=(
                f"Model Error: {exc}\n"
                "Note: First run may download the BirdNET model (~1 GB)."
            ),
            exit_code=MODEL_ERROR_EXIT_CODE,
            is_error=True,
        )
    if isinstance(exc, FileNotFoundError_):
        return CommandResult(
            output=f"Error: {exc}",
            exit_code=FILE_NOT_FOUND_ERROR_EXIT_CODE,
            is_error=True,
        )
    if isinstance(exc, ChirpedexError):
        return CommandResult(
            output=f"Error: {exc}",
            exit_code=CHIRPEDEX_ERROR_EXIT_CODE,
            is_error=True,
        )
    if isinstance(exc, ImportError):
        return CommandResult(
            output=f"ImportError: {exc}",
            exit_code=IMPORT_ERROR_EXIT_CODE,
            is_error=True,
        )
    return CommandResult(
        output=f"Unexpected error: {exc}",
        exit_code=GENERIC_ERROR_EXIT_CODE,
        is_error=True,
    )


def handle_identify(
        audio_path: str,
        json_output: bool = False,
) -> CommandResult:
    """Handle the identify command.

    Args:
        audio_path: Path to the audio file.
        json_output: Whether to output as JSON.

    Returns:
        The rendered command output and exit status.
    """
    try:
        validated_path = validate_audio_file(audio_path)
        identifier = BirdNETIdentifier()
        prediction = _identify(validated_path, identifier)
        return CommandResult(
            output=_format_prediction(prediction, json_output),
            exit_code=SUCCESS_EXIT_CODE,
        )
    except Exception as exc:
        return _error_result(exc)


def handle_multi_identify(
        audio_paths: Sequence[str],
        json_output: bool = False,
) -> CommandResult:
    """Identify birds in multiple audio files."""
    predictions: list[BirdPrediction] = []
    errors: list[tuple[Path, CommandResult]] = []
    validated_paths: list[Path] = []

    for audio_path in audio_paths:
        try:
            validated_paths.append(validate_audio_file(audio_path))
        except Exception as exc:
            errors.append((Path(audio_path), _error_result(exc)))

    if validated_paths:
        try:
            identifier = BirdNETIdentifier()
        except Exception as exc:
            return _error_result(exc)

        for audio_path in validated_paths:
            try:
                predictions.append(_identify(audio_path, identifier))
            except Exception as exc:
                errors.append((audio_path, _error_result(exc)))

    if json_output:
        output = json.dumps(
            {
                "predictions": [
                    _prediction_to_dict(prediction)
                    for prediction in predictions
                ],
                "errors": [
                    {
                        "source_audio_path": str(path),
                        "message": result.output,
                        "exit_code": result.exit_code,
                    }
                    for path, result in errors
                ],
            },
            indent=2,
        )
    else:
        sections = [
            f"File: {prediction.source_audio_path}\n{prediction}"
            for prediction in predictions
        ]
        sections.extend(
            f"File: {path}\n{result.output}"
            for path, result in errors
        )
        output = "\n\n".join(sections)

    exit_code = (
        errors[0][1].exit_code if errors else SUCCESS_EXIT_CODE
    )
    return CommandResult(
        output=output,
        exit_code=exit_code,
        is_error=bool(errors),
    )
