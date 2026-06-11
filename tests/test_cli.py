"""Tests for the CLI module."""

from unittest.mock import MagicMock, patch

from chirpedex.cli import create_parser, handle_identify, main
from chirpedex.exit_codes import (
    CHIRPEDEX_ERROR_EXIT_CODE,
    FILE_NOT_FOUND_ERROR_EXIT_CODE,
)
from chirpedex.models import BirdPrediction


def test_create_parser() -> None:
    """Test that the parser is created correctly."""
    parser = create_parser()
    assert parser is not None

    # Test parsing identify command
    args = parser.parse_args(["identify", "test.wav"])
    assert args.command == "identify"
    assert args.audio_path == "test.wav"


def test_create_parser_identify_with_json() -> None:
    """Test parsing identify command with --json flag."""
    parser = create_parser()
    args = parser.parse_args(["identify", "test.wav", "--json"])
    assert args.command == "identify"
    assert args.audio_path == "test.wav"
    assert args.json is True


def test_create_parser_no_args() -> None:
    """Test that parser shows help when no args."""
    parser = create_parser()
    args = parser.parse_args([])
    assert args.command is None


def test_handle_identify_file_not_found() -> None:
    """Test handle_identify with non-existent file."""
    exit_code = handle_identify("nonexistent.wav")
    assert exit_code == FILE_NOT_FOUND_ERROR_EXIT_CODE


def test_handle_identify_invalid_format() -> None:
    """Test handle_identify with unsupported file format."""
    with patch("chirpedex.cli.validate_audio_file") as mock_validate:
        from chirpedex.errors import InvalidAudioFormatError

        mock_validate.side_effect = InvalidAudioFormatError(
            "Unsupported audio format: .txt"
        )
        exit_code = handle_identify("test.txt")

    assert exit_code == CHIRPEDEX_ERROR_EXIT_CODE


@patch("chirpedex.cli.BirdNETIdentifier")
@patch("chirpedex.cli.validate_audio_file")
def test_handle_identify_success(mock_validate, mock_identifier_class) -> None:
    """Test successful bird identification."""
    from pathlib import Path

    # Mock the validation
    test_path = Path("test.wav")
    mock_validate.return_value = test_path

    # Mock the identifier
    mock_prediction = BirdPrediction(
        species_common_name="European Robin",
        species_scientific_name="Erithacus rubecula",
        confidence=0.95,
        source_audio_path=test_path,
    )
    mock_identifier = MagicMock()
    mock_identifier.identify_from_file.return_value = mock_prediction
    mock_identifier_class.return_value = mock_identifier

    # Create a temporary test file
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        exit_code = handle_identify(tmp.name)
        assert exit_code == 0


@patch("chirpedex.cli.BirdNETIdentifier")
@patch("chirpedex.cli.validate_audio_file")
def test_handle_identify_json_output(mock_validate, mock_identifier_class) -> None:
    """Test JSON output from identify command."""
    from datetime import datetime
    from pathlib import Path

    # Mock the validation
    test_path = Path("test.wav")
    mock_validate.return_value = test_path

    # Mock the identifier
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

    # Create a temporary test file
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        exit_code = handle_identify(tmp.name, json_output=True)
        assert exit_code == 0


def test_main_no_args() -> None:
    """Test main with no arguments."""
    with patch.object(__import__("sys"), "argv", ["chirpedex"]):
        exit_code = main()
        assert exit_code == 0


def test_main_identify(capsys) -> None:
    """Test main with identify command."""
    from pathlib import Path
    from unittest.mock import patch

    mock_prediction = BirdPrediction(
        species_common_name="European Robin",
        species_scientific_name="Erithacus rubecula",
        confidence=0.95,
    )

    with patch("chirpedex.cli.BirdNETIdentifier") as mock_id:
        mock_instance = MagicMock()
        mock_instance.identify_from_file.return_value = mock_prediction
        mock_id.return_value = mock_instance

        with patch("chirpedex.cli.validate_audio_file") as mock_validate:
            mock_validate.return_value = Path("test.wav")

            with patch.object(
                __import__("sys"), "argv", ["chirpedex", "identify", "test.wav"]
            ):
                exit_code = main()
                assert exit_code == 0
