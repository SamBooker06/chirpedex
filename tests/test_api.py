import io
import select
import signal
import subprocess
import sys
import time
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from chirpedex.client.api.server import (
    SERVER_READY,
    SERVER_SHUTDOWN,
    app,
    get_identifier,
    start_server,
)
from chirpedex.client.cli import ExitCode
from chirpedex.core.models import BirdPrediction

client = TestClient(app)


def test_get_version():
    response = client.get("/version")

    assert response.status_code == 200


@patch("signal.raise_signal")
def test_shutdown_mock(mock_raise_signal):
    response = client.post("/shutdown")
    assert response.status_code == 200
    mock_raise_signal.assert_called_once()


def test_shutdown():
    proc = subprocess.Popen(
        [sys.executable, "-u", "-m", "chirpedex", "serve", "--port", "0"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    assert proc.stdout is not None

    try:
        buffer = ""
        deadline = time.monotonic() + 5

        while SERVER_READY not in buffer:
            timeout = deadline - time.monotonic()
            if timeout <= 0:
                pytest.fail(f"Server not ready. Output:\n{buffer}")

            ready, _, _ = select.select([proc.stdout], [], [], timeout)
            if not ready:
                pytest.fail(f"Server not ready. Output:\n{buffer}")

            buffer += proc.stdout.readline()

        proc.terminate()

        output, _ = proc.communicate(timeout=2)

    finally:
        if proc.poll() is None:
            proc.kill()
            proc.communicate()

    assert SERVER_SHUTDOWN in buffer + output

    # SUCCESS_EXIT_CODE in the event we signal handle in the future
    assert proc.returncode in [-signal.SIGTERM, ExitCode.SUCCESS_EXIT_CODE]


@patch("uvicorn.run")
def test_mock_startup(mock_uvicorn):
    with patch("chirpedex.client.api.server.BirdNETIdentifier"):
        start_server()

        mock_uvicorn.assert_called_once()


def test_mock_file_upload():
    mock_identifier = MagicMock()
    uploaded_contents: list[bytes] = []
    def identify_from_file(audio_file: io.BytesIO) -> BirdPrediction:
        uploaded_contents.append(audio_file.read())
        return BirdPrediction(
            species_common_name="European Robin",
            species_scientific_name="Erithacus rubecula",
            confidence=0.95,
        )

    mock_identifier.identify_from_file.side_effect = identify_from_file
    app.dependency_overrides[get_identifier] = lambda: mock_identifier

    try:
        with io.BytesIO(b"test file content") as fs:
            response = client.post("/identify", files={"audio_file": ("robin.wav", fs)})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    mock_identifier.identify_from_file.assert_called_once()
    assert uploaded_contents == [b"test file content"]
