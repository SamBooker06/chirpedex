import signal
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import fastapi

import chirpedex
from chirpedex.api import DEFAULT_HOST, DEFAULT_API_PORT

SERVER_READY = "[SERVER READY]"
SERVER_SHUTDOWN = "[SERVER SHUTDOWN]"

@asynccontextmanager
async def lifespan(_) -> AsyncGenerator[None, Any]:
    print(SERVER_READY)
    yield
    print(SERVER_SHUTDOWN)


app = fastapi.FastAPI(lifespan=lifespan)

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


def start_server(host: str = DEFAULT_HOST, port: int = DEFAULT_API_PORT) -> None:
    from uvicorn import run

    run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
