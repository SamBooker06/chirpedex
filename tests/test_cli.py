"""Tests for the CLI module."""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from chirpedex.cli.cli import (
    create_parser,
    handle_identify,
    handle_multi_identify,
    main,
)
from chirpedex.exit_codes import (
    CHIRPEDEX_ERROR_EXIT_CODE,
    FILE_NOT_FOUND_ERROR_EXIT_CODE,
    SUCCESS_EXIT_CODE,
)
from chirpedex.errors import FileNotFoundError_
from chirpedex.models import BirdPrediction


def test_create_parser() -> None:
    """Test that the parser is created correctly."""
    parser = create_parser()
    assert parser is not None

    # Test parsing identify command
    args = parser.parse_args(["identify", "test.wav"])
    assert args.command == "identify"
    assert args.audio_path == ["test.wav"]


def test_create_parser_identify_with_json() -> None:
    """Test parsing identify command with --json flag."""
    parser = create_parser()
    args = parser.parse_args(["identify", "test.wav", "--json"])
    assert args.command == "identify"
    assert args.audio_path == ["test.wav"]
    assert args.json is True


def test_create_parser_no_args() -> None:
    """Test that parser shows help when no args."""
    parser = create_parser()
    args = parser.parse_args([])
    assert args.command is None


def test_handle_identify_file_not_found() -> None:
    """Test handle_identify with non-existent file."""
    result = handle_identify("nonexistent.wav")
    assert result.exit_code == FILE_NOT_FOUND_ERROR_EXIT_CODE
    assert result.is_error is True


def test_handle_identify_invalid_format() -> None:
    """Test handle_identify with unsupported file format."""
    with patch("chirpedex.cli.identify.validate_audio_file") as mock_validate:
        from chirpedex.errors import InvalidAudioFormatError

        mock_validate.side_effect = InvalidAudioFormatError(
            "Unsupported audio format: .txt"
        )
        result = handle_identify("test.txt")

    assert result.exit_code == CHIRPEDEX_ERROR_EXIT_CODE
    assert result.output == "Error: Unsupported audio format: .txt"


@patch("chirpedex.cli.identify.BirdNETIdentifier")
@patch("chirpedex.cli.identify.validate_audio_file")
def test_handle_identify_success(mock_validate, mock_identifier_class) -> None:
    """Test successful bird identification."""
    test_path = Path("test.wav")
    mock_validate.return_value = test_path

    mock_prediction = BirdPrediction(
        species_common_name="European Robin",
        species_scientific_name="Erithacus rubecula",
        confidence=0.95,
        source_audio_path=test_path,
    )
    mock_identifier = MagicMock()
    mock_identifier.identify_from_file.return_value = mock_prediction
    mock_identifier_class.return_value = mock_identifier

    result = handle_identify("test.wav")

    assert result.exit_code == SUCCESS_EXIT_CODE
    assert "Species: European Robin" in result.output
    mock_identifier.identify_from_file.assert_called_once_with(test_path)


@patch("chirpedex.cli.identify.BirdNETIdentifier")
@patch("chirpedex.cli.identify.validate_audio_file")
def test_handle_identify_json_output(mock_validate, mock_identifier_class) -> None:
    """Test JSON output from identify command."""
    test_path = Path("test.wav")
    mock_validate.return_value = test_path

    test_time = datetime.now()
    mock_prediction = BirdPrediction(
        species_common_name="European Robin",
        species_scientific_name="Erithacus rubecula",
        confidence=0.95,
        timestamp=test_time,
        source_audio_path=test_path,
    )
    mock_identifier = MagicMock()
    mock_identifier.identify_from_file.return_value = mock_prediction
    mock_identifier_class.return_value = mock_identifier

    result = handle_identify("test.wav", json_output=True)

    assert result.exit_code == SUCCESS_EXIT_CODE
    assert json.loads(result.output)["species_common_name"] == "European Robin"


def test_main_no_args() -> None:
    """Test main with no arguments."""
    with patch.object(__import__("sys"), "argv", ["chirpedex"]):
        exit_code = main()
        assert exit_code == 0


def test_main_identify(capsys) -> None:
    """Test main with identify command."""
    mock_prediction = BirdPrediction(
        species_common_name="European Robin",
        species_scientific_name="Erithacus rubecula",
        confidence=0.95,
    )

    with patch("chirpedex.cli.identify.BirdNETIdentifier") as mock_id:
        mock_instance = MagicMock()
        mock_instance.identify_from_file.return_value = mock_prediction
        mock_id.return_value = mock_instance

        with patch("chirpedex.cli.identify.validate_audio_file") as mock_validate:
            mock_validate.return_value = Path("test.wav")

            with patch.object(
                __import__("sys"), "argv", ["chirpedex", "identify", "test.wav"]
            ):
                exit_code = main()
                assert exit_code == 0
                assert "Species: European Robin" in capsys.readouterr().out


def test_main_identify_error_uses_stderr(capsys) -> None:
    """Test that main prints command errors and returns their exit code."""
    with patch.object(
        __import__("sys"),
        "argv",
        ["chirpedex", "identify", "missing.wav"],
    ):
        exit_code = main()

    captured = capsys.readouterr()
    assert exit_code == FILE_NOT_FOUND_ERROR_EXIT_CODE
    assert captured.out == ""
    assert "missing.wav" in captured.err


@patch("chirpedex.cli.identify.BirdNETIdentifier")
@patch("chirpedex.cli.identify.validate_audio_file")
def test_handle_multi_identify_success(
    mock_validate,
    mock_identifier_class,
) -> None:
    """Test identification of multiple files with one identifier."""
    paths = [Path("first.wav"), Path("second.wav")]
    mock_validate.side_effect = paths
    mock_identifier = MagicMock()
    mock_identifier.identify_from_file.side_effect = [
        BirdPrediction("European Robin", source_audio_path=paths[0]),
        BirdPrediction("Common Blackbird", source_audio_path=paths[1]),
    ]
    mock_identifier_class.return_value = mock_identifier

    result = handle_multi_identify(["first.wav", "second.wav"])

    assert result.exit_code == SUCCESS_EXIT_CODE
    assert "European Robin" in result.output
    assert "Common Blackbird" in result.output
    mock_identifier_class.assert_called_once_with()


@patch("chirpedex.cli.identify.BirdNETIdentifier")
@patch("chirpedex.cli.identify.validate_audio_file")
def test_handle_multi_identify_partial_failure(
    mock_validate,
    mock_identifier_class,
) -> None:
    """Test that valid files are processed when another file is missing."""
    valid_path = Path("valid.wav")
    mock_validate.side_effect = [
        valid_path,
        FileNotFoundError_("Audio file not found: missing.wav"),
    ]
    mock_identifier = MagicMock()
    mock_identifier.identify_from_file.return_value = BirdPrediction(
        "European Robin",
        source_audio_path=valid_path,
    )
    mock_identifier_class.return_value = mock_identifier

    result = handle_multi_identify(["valid.wav", "missing.wav"])

    assert result.exit_code == FILE_NOT_FOUND_ERROR_EXIT_CODE
    assert result.is_error is True
    assert "European Robin" in result.output
    assert "missing.wav" in result.output
