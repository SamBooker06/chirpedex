"""Tests for the public CLI interface."""

import sys
from argparse import Namespace
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from chirpedex.cli import create_parser, main
from chirpedex.cli.exit_codes import ExitCode
from chirpedex.models import BirdPrediction


class FakeCommand:
    """Small command double used to keep CLI tests at the public boundary."""

    def __init__(self, exit_code: ExitCode, output: object) -> None:
        self.exit_code = exit_code
        self.output = output

    def execute(self) -> SimpleNamespace:
        return SimpleNamespace(exit_code=self.exit_code, output=self.output)


def parse_args(argv: list[str]) -> Namespace:
    return create_parser().parse_args(argv)


def run_cli_with_command(
    argv: list[str],
    command: FakeCommand,
) -> tuple[ExitCode, Namespace]:
    created_with: Namespace | None = None

    def create_command(args: Namespace) -> FakeCommand:
        nonlocal created_with
        created_with = args
        return command

    with patch.object(sys, "argv", ["chirpedex", *argv]):
        with patch("chirpedex.cli.CommandFactory.create_command", create_command):
            exit_code = main()

    assert created_with is not None
    return exit_code, created_with


def test_parser_accepts_identify_audio_path() -> None:
    args = parse_args(["identify", "test.wav"])

    assert args.command == "identify"
    assert args.audio_path == ["test.wav"]
    assert args.json is False
    assert args.remote is False


def test_parser_accepts_multiple_identify_audio_paths() -> None:
    args = parse_args(["identify", "first.wav", "second.wav"])

    assert args.command == "identify"
    assert args.audio_path == ["first.wav", "second.wav"]


def test_parser_accepts_identify_json_output() -> None:
    args = parse_args(["identify", "test.wav", "--json"])

    assert args.command == "identify"
    assert args.audio_path == ["test.wav"]
    assert args.json is True


def test_parser_accepts_identify_remote_options() -> None:
    args = parse_args(
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

    assert args.command == "identify"
    assert args.audio_path == ["test.wav"]
    assert args.remote is True
    assert args.host == "http://chirpedex.local"
    assert args.port == 8080


def test_parser_accepts_serve_options() -> None:
    args = parse_args(["serve", "--host", "127.0.0.1", "--port", "9000"])

    assert args.command == "serve"
    assert args.host == "127.0.0.1"
    assert args.port == 9000


def test_parser_accepts_no_args_for_main_to_handle_help() -> None:
    args = parse_args([])

    assert args.command is None


def test_main_no_args_prints_help(capsys: pytest.CaptureFixture[str]) -> None:
    with patch.object(sys, "argv", ["chirpedex"]):
        exit_code = main()

    captured = capsys.readouterr()
    assert exit_code == ExitCode.INVALID_ARGUMENT_ERROR_EXIT_CODE
    assert "Available commands" in captured.out


def test_main_identify_prints_prediction(
    capsys: pytest.CaptureFixture[str],
) -> None:
    command = FakeCommand(
        ExitCode.SUCCESS_EXIT_CODE,
        BirdPrediction(
            species_common_name="European Robin",
            species_scientific_name="Erithacus rubecula",
            confidence=0.95,
        ),
    )

    exit_code, args = run_cli_with_command(["identify", "test.wav"], command)

    captured = capsys.readouterr()
    assert exit_code == ExitCode.SUCCESS_EXIT_CODE
    assert args.command == "identify"
    assert args.audio_path == ["test.wav"]
    assert "Species: European Robin" in captured.out
    assert "Scientific name: Erithacus rubecula" in captured.out
    assert "Confidence: 0.95" in captured.out


def test_main_identify_prints_multiple_predictions(
    capsys: pytest.CaptureFixture[str],
) -> None:
    command = FakeCommand(
        ExitCode.SUCCESS_EXIT_CODE,
        [
            BirdPrediction("European Robin", "Erithacus rubecula", 0.95),
            BirdPrediction("Common Blackbird", "Turdus merula", 0.85),
        ],
    )

    exit_code, args = run_cli_with_command(
        ["identify", "first.wav", "second.wav"],
        command,
    )

    captured = capsys.readouterr()
    assert exit_code == ExitCode.SUCCESS_EXIT_CODE
    assert args.command == "identify"
    assert args.audio_path == ["first.wav", "second.wav"]
    assert "European Robin" in captured.out
    assert "Common Blackbird" in captured.out


def test_main_identify_forwards_remote_options(
    capsys: pytest.CaptureFixture[str],
) -> None:
    command = FakeCommand(ExitCode.SUCCESS_EXIT_CODE, "ok")

    exit_code, args = run_cli_with_command(
        [
            "identify",
            "test.wav",
            "--remote",
            "--host",
            "http://chirpedex.local",
            "--port",
            "8080",
        ],
        command,
    )

    captured = capsys.readouterr()
    assert exit_code == ExitCode.SUCCESS_EXIT_CODE
    assert args.remote is True
    assert args.host == "http://chirpedex.local"
    assert args.port == 8080
    assert "ok" in captured.out


def test_main_returns_command_error_code(
    capsys: pytest.CaptureFixture[str],
) -> None:
    command = FakeCommand(
        ExitCode.FILE_NOT_FOUND_ERROR_EXIT_CODE,
        "Audio file not found: missing.wav",
    )

    exit_code, args = run_cli_with_command(["identify", "missing.wav"], command)

    captured = capsys.readouterr()
    assert exit_code == ExitCode.FILE_NOT_FOUND_ERROR_EXIT_CODE
    assert args.command == "identify"
    assert "missing.wav" in captured.out


def test_main_serve_uses_parsed_host_and_port(
    capsys: pytest.CaptureFixture[str],
) -> None:
    command = FakeCommand(ExitCode.SUCCESS_EXIT_CODE, "")

    exit_code, args = run_cli_with_command(
        ["serve", "--host", "127.0.0.1", "--port", "9000"],
        command,
    )

    capsys.readouterr()
    assert exit_code == ExitCode.SUCCESS_EXIT_CODE
    assert args.command == "serve"
    assert args.host == "127.0.0.1"
    assert args.port == 9000


def test_main_returns_generic_error_when_command_creation_fails(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with patch.object(sys, "argv", ["chirpedex", "identify", "test.wav"]):
        with patch(
            "chirpedex.cli.CommandFactory.create_command",
            MagicMock(side_effect=RuntimeError("factory failed")),
        ):
            exit_code = main()

    captured = capsys.readouterr()
    assert exit_code == ExitCode.CHIRPEDEX_ERROR_EXIT_CODE
    assert "factory failed" in captured.out
