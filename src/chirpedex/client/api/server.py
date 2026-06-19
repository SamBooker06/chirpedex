"""
The only role of the server is to identify the birds - it is not responsible for keeping track
"""

import asyncio
import io
import json
import signal
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Annotated, Any, AsyncGenerator

from fastapi import Depends, UploadFile, FastAPI
from starlette.websockets import WebSocket

import chirpedex
from chirpedex.client.api import DEFAULT_HOST, DEFAULT_API_PORT
from chirpedex.core.identification.birdnet_identifier import BirdNETIdentifier
from chirpedex.core.identification import BirdIdentifier

SERVER_READY = "[SERVER READY]"
SERVER_SHUTDOWN = "[SERVER SHUTDOWN]"

CHUNK_SIZE = 1024 * 1024


@lru_cache(maxsize=1)
def get_identifier() -> BirdIdentifier:
    """Return the shared identifier used by API requests."""
    return BirdNETIdentifier()


IdentifierInstance = Annotated[BirdIdentifier, Depends(get_identifier)]


@asynccontextmanager
async def lifespan(_) -> AsyncGenerator[None, Any]:
    # Load the identifier ready
    print(SERVER_READY)
    yield
    print(SERVER_SHUTDOWN)


app = FastAPI(lifespan=lifespan)


@app.get("/")
@app.get("/version")
def version() -> dict[str, str]:
    return {
        "version": chirpedex.__version__,
    }


@app.post("/shutdown")
def shutdown() -> str:
    signal.raise_signal(signal.SIGTERM)
    return "Shutting down..."


@app.post("/identify")
async def identify(audio_file: UploadFile, identifier: IdentifierInstance):
    contents = await audio_file.read()

    with io.BytesIO(contents) as f:
        res = await asyncio.to_thread(lambda: identifier.identify_from_file(f))

        return json.dumps(res.to_dict())


@app.websocket("/identify/stream")
async def identify_stream(ws: WebSocket, identifier: IdentifierInstance):
    raise NotImplementedError("PCM streaming not implemented yet.")


def start_server(host: str = DEFAULT_HOST, port: int = DEFAULT_API_PORT) -> None:
    from uvicorn import run

    run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
