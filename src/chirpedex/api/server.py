import signal

import fastapi

import chirpedex
from chirpedex.api import DEFAULT_HOST, DEFAULT_API_PORT

_app = fastapi.FastAPI()


@_app.get("/")
@_app.get("/version")
def version() -> dict[str, str]:
    return {
        "version": chirpedex.__version__,
    }


@_app.post("/shutdown")
def shutdown() -> str:
    signal.raise_signal(signal.SIGTERM)
    return "Shutting down..."


def start_server(host: str = DEFAULT_HOST, port: int = DEFAULT_API_PORT) -> None:
    from uvicorn import run

    run(_app, host=host, port=port)


if __name__ == "__main__":
    start_server()
