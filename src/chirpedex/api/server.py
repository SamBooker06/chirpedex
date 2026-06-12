import signal

import fastapi

import chirpedex

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


def start_server() -> None:
    from uvicorn import run

    run(_app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    start_server()
