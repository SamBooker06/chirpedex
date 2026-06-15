import select
import signal
import subprocess
import sys
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from chirpedex.api.server import app, SERVER_READY, SERVER_SHUTDOWN, start_server
from chirpedex.exit_codes import SUCCESS_EXIT_CODE

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
    proc = subprocess.Popen([sys.executable, "-m", "chirpedex", "serve"], stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)

    assert proc.stdout is not None

    try:
        buffer = ""

        while SERVER_READY not in buffer:
            ready, _, _ = select.select([proc.stdout], [], [], 2)
            if not ready:
                pytest.fail("Server not running")

            buffer += proc.stdout.readline()

        proc.terminate()

        output, _ = proc.communicate(timeout=2)

    finally:
        if proc.poll() is None:
            proc.kill()
            proc.communicate()

    assert SERVER_SHUTDOWN in buffer + output

    # SUCCESS_EXIT_CODE in the event we signal handle in the future
    assert proc.returncode in [-signal.SIGTERM, SUCCESS_EXIT_CODE]

@patch("uvicorn.run")
def test_mock_startup(mock_uvicorn):
    start_server()

    mock_uvicorn.assert_called_once()