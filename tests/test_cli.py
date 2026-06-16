"""Tests for the CLI module."""

import sys
from argparse import Namespace
from unittest.mock import MagicMock, patch

import pytest

from chirpedex.cli import create_parser, main
from chirpedex.cli.command import CommandResult
from chirpedex.cli.exit_codes import ExitCode
from chirpedex.cli.factories import CommandFactory, IdentifyCommandFactory
from chirpedex.cli.identify.identify_multi import IdentifyMultiCommand
from chirpedex.cli.identify.identify_single import IdentifySingleCommand
from chirpedex.cli.serve import ServeCommand
from chirpedex.models import BirdPrediction


def test_create_parser_identify() -> None:
    """Test parsing identify command."""
    parser = create_parser()

    args = parser.parse_args(["identify", "test.wav"])

    assert args.command == "identify"
    assert args.audio_path == ["test.wav"]
    assert args.json is False
    assert args.remote is False


def test_create_parser_identify_with_multiple_files() -> None:
    """Test parsing identify command with multiple audio files."""
    parser = create_parser()

    args = parser.parse_args(["identify", "first.wav", "second.wav"])

    assert args.command == "identify"
    assert args.audio_path == ["first.wav", "second.wav"]


def test_create_parser_identify_with_remote_options() -> None:
    """Test parsing identify command with remote API options."""
    parser = create_parser()

    args = parser.parse_args(
        [
            "identify",
            "test.wav",
            "--remote",
            "--host",
            "http://chirpedex.local",
            "--port",
            "8080",
        ]
    )

    assert args.remote is True
    assert args.host == "http://chirpedex.local"
    assert args.port == 8080


def test_create_parser_identify_with_json() -> None:
    """Test parsing identify command with --json flag."""
    parser = create_parser()

    args = parser.parse_args(["identify", "test.wav", "--json"])

    assert args.command == "identify"
    assert args.audio_path == ["test.wav"]
    assert args.json is True


def test_create_parser_serve() -> None:
    """Test parsing serve command."""
    parser = create_parser()

    args = parser.parse_args(["serve", "--host", "127.0.0.1", "--port", "9000"])

    assert args.command == "serve"
    assert args.host == "127.0.0.1"
    assert args.port == 9000


def test_create_parser_no_args() -> None:
    """Test that parser accepts no args for main to handle help output."""
    parser = create_parser()

    args = parser.parse_args([])

    assert args.command is None


def test_command_factory_creates_serve_command() -> None:
    """Test command factory creates serve command."""
    args = Namespace(command="serve", host="127.0.0.1", port=9000)

    command = CommandFactory.create_command(args)

    assert isinstance(command, ServeCommand)
    assert command.host == "127.0.0.1"
    assert command.port == 9000


@patch("chirpedex.cli.factories.BirdNETIdentifier")
def test_identify_command_factory_creates_single_command(
    mock_identifier_class: MagicMock,
) -> None:
    """Test identify factory creates a single-file command."""
    mock_identifier = MagicMock()
    mock_identifier_class.return_value = mock_identifier
    args = Namespace(
        command="identify",
        audio_path=["test.wav"],
        remote=False,
        host="http://localhost",
        port=8000,
    )

    command = IdentifyCommandFactory.create_command(args)

    assert isinstance(command, IdentifySingleCommand)
    assert command.file_path == "test.wav"
    mock_identifier_class.assert_called_once_with()


@patch("chirpedex.cli.factories.BirdNETIdentifier")
def test_identify_command_factory_creates_multi_command(
    mock_identifier_class: MagicMock,
) -> None:
    """Test identify factory creates a multi-file command."""
    mock_identifier = MagicMock()
    mock_identifier_class.return_value = mock_identifier
    args = Namespace(
        command="identify",
        audio_path=["first.wav", "second.wav"],
        remote=False,
        host="http://localhost",
        port=8000,
    )

    command = IdentifyCommandFactory.create_command(args)

    assert isinstance(command, IdentifyMultiCommand)
    assert command.paths == ["first.wav", "second.wav"]
    mock_identifier_class.assert_called_once_with()


@patch("chirpedex.cli.factories.RemoteIdentifier")
def test_identify_command_factory_creates_remote_identifier(
    mock_remote_identifier_class: MagicMock,
) -> None:
    """Test identify factory uses remote identifier when requested."""
    args = Namespace(
        command="identify",
        audio_path=["test.wav"],
        remote=True,
        host="http://chirpedex.local",
        port=8080,
    )

    command = IdentifyCommandFactory.create_command(args)

    assert isinstance(command, IdentifySingleCommand)
    mock_remote_identifier_class.assert_called_once_with("http://chirpedex.local", 8080)


def test_identify_single_command_file_not_found() -> None:
    """Test single-file identify command with non-existent file."""
    command = IdentifySingleCommand(MagicMock(), "nonexistent.wav")

    result = command.execute()

    assert result.exit_code == ExitCode.FILE_NOT_FOUND_ERROR_EXIT_CODE
    assert result.is_error is True
    assert "nonexistent.wav" in str(result.output)


def test_identify_single_command_success(tmp_path) -> None:
    """Test successful single-file bird identification."""
    test_path = tmp_path / "test.wav"
    test_path.write_bytes(b"audio")
    mock_prediction = BirdPrediction(
        species_common_name="European Robin",
        species_scientific_name="Erithacus rubecula",
        confidence=0.95,
        source_audio_path=test_path,
    )
    mock_identifier = MagicMock()
    mock_identifier.identify_from_file.return_value = mock_prediction
    command = IdentifySingleCommand(mock_identifier, str(test_path))

    result = command.execute()

    assert result.exit_code == ExitCode.SUCCESS_EXIT_CODE
    assert result.output == mock_prediction
    mock_identifier.identify_from_file.assert_called_once()


def test_identify_single_command_low_confidence_is_error(tmp_path) -> None:
    """Test low-confidence predictions are treated as no detection."""
    test_path = tmp_path / "test.wav"
    test_path.write_bytes(b"audio")
    mock_identifier = MagicMock()
    mock_identifier.identify_from_file.return_value = BirdPrediction(
        species_common_name="European Robin",
        confidence=0.01,
    )
    command = IdentifySingleCommand(mock_identifier, str(test_path))

    result = command.execute()

    assert result.exit_code == ExitCode.CHIRPEDEX_ERROR_EXIT_CODE
    assert result.is_error is True
    assert result.output == "No bird species detected"


def test_identify_multi_command_success(tmp_path) -> None:
    """Test successful multi-file bird identification."""
    paths = [tmp_path / "first.wav", tmp_path / "second.wav"]
    for path in paths:
        path.write_bytes(b"audio")

    predictions = [
        BirdPrediction("European Robin", "Erithacus rubecula", 0.95),
        BirdPrediction("Common Blackbird", "Turdus merula", 0.85),
    ]
    mock_identifier = MagicMock()
    mock_identifier.identify_from_file.side_effect = predictions
    command = IdentifyMultiCommand(mock_identifier, [str(path) for path in paths])

    result = command.execute()

    assert result.exit_code == ExitCode.SUCCESS_EXIT_CODE
    assert result.output == predictions
    assert mock_identifier.identify_from_file.call_count == 2


def test_identify_multi_command_partial_failure(tmp_path) -> None:
    """Test multi-file command reports failure if any file fails."""
    valid_path = tmp_path / "valid.wav"
    valid_path.write_bytes(b"audio")
    mock_identifier = MagicMock()
    mock_identifier.identify_from_file.return_value = BirdPrediction(
        "European Robin",
        confidence=0.95,
    )
    command = IdentifyMultiCommand(
        mock_identifier,
        [str(valid_path), str(tmp_path / "missing.wav")],
    )

    result = command.execute()

    assert result.exit_code == ExitCode.CHIRPEDEX_ERROR_EXIT_CODE
    assert result.is_error is True
    assert "One or more files failed to identify" in str(result.output)
    assert "missing.wav" in str(result.output)


def test_main_no_args(capsys: pytest.CaptureFixture[str]) -> None:
    """Test main with no arguments."""
    with patch.object(sys, "argv", ["chirpedex"]):
        exit_code = main()

    captured = capsys.readouterr()
    assert exit_code == ExitCode.INVALID_ARGUMENT_ERROR_EXIT_CODE
    assert "Available commands" in captured.out


def test_main_prints_single_command_output(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test main prints a single command result."""
    prediction = BirdPrediction(
        species_common_name="European Robin",
        species_scientific_name="Erithacus rubecula",
        confidence=0.95,
    )
    mock_command = MagicMock()
    mock_command.execute.return_value = CommandResult(
        ExitCode.SUCCESS_EXIT_CODE,
        prediction,
    )

    with patch.object(sys, "argv", ["chirpedex", "identify", "test.wav"]):
        with patch(
            "chirpedex.cli.factories.CommandFactory.create_command",
            return_value=mock_command,
        ):
            exit_code = main()

    captured = capsys.readouterr()
    assert exit_code == ExitCode.SUCCESS_EXIT_CODE
    assert "Species: European Robin" in captured.out
    assert "Scientific name: Erithacus rubecula" in captured.out


def test_main_prints_multi_command_output(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test main prints each item from a list command result."""
    mock_command = MagicMock()
    mock_command.execute.return_value = CommandResult(
        ExitCode.SUCCESS_EXIT_CODE,
        [
            BirdPrediction("European Robin", "Erithacus rubecula", 0.95),
            BirdPrediction("Common Blackbird", "Turdus merula", 0.85),
        ],
    )

    with patch.object(
        sys,
        "argv",
        ["chirpedex", "identify", "first.wav", "second.wav"],
    ):
        with patch(
            "chirpedex.cli.factories.CommandFactory.create_command",
            return_value=mock_command,
        ):
            exit_code = main()

    captured = capsys.readouterr()
    assert exit_code == ExitCode.SUCCESS_EXIT_CODE
    assert "European Robin" in captured.out
    assert "Common Blackbird" in captured.out


def test_main_returns_error_code_from_command(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test main returns the command's error code."""
    mock_command = MagicMock()
    mock_command.execute.return_value = CommandResult(
        ExitCode.FILE_NOT_FOUND_ERROR_EXIT_CODE,
        "Audio file not found: missing.wav",
        is_error=True,
    )

    with patch.object(sys, "argv", ["chirpedex", "identify", "missing.wav"]):
        with patch(
            "chirpedex.cli.factories.CommandFactory.create_command",
            return_value=mock_command,
        ):
            exit_code = main()

    captured = capsys.readouterr()
    assert exit_code == ExitCode.FILE_NOT_FOUND_ERROR_EXIT_CODE
    assert "missing.wav" in captured.out
