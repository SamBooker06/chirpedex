# Chirpedex

Chirpedex identifies birds from audio recordings using [BirdNET](https://birdnet.cornell.edu/). It provides a Python CLI for local inference, an optional HTTP API, and optional PostgreSQL-backed sighting registration.

## Requirements

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/)
- Docker and Docker Compose (for containerised use)

The first local BirdNET run downloads model data, so it needs network access and can take longer than later runs.

## Quick start

Install the project dependencies:

```bash
uv sync
```

Identify an audio file without recording a sighting:

```bash
SCHEMA_PATH=src/chirpedex/core/db/sql/01-schema.sql \
  uv run chirpedex identify --no-register examples/audio/buzzard.mp3
```

`--no-register` is the simplest mode: it runs local BirdNET inference and does not require PostgreSQL. `SCHEMA_PATH` is currently required by the CLI for every `identify` invocation.

Example output:

```text
Species: European Robin
Scientific name: Erithacus rubecula
Confidence: 0.92
```

## CLI

The package exposes both `chirpedex` and `python -m chirpedex` entry points.

```bash
chirpedex identify [OPTIONS] AUDIO_PATH [AUDIO_PATH ...]
```

Useful options:

- `--no-register` — do not persist sightings; use this unless PostgreSQL is configured.
- `--remote` — send each audio file to a running Chirpedex API instead of using local BirdNET inference.
- `--host URL` and `--port PORT` — remote API address (defaults: `http://localhost` and `7092`).

Multiple audio files can be supplied in a single command. The CLI prints one prediction for each input file.

Start the API server with:

```bash
uv run chirpedex serve --host 0.0.0.0 --port 7092
```

The API exposes `POST /identify`, which accepts an uploaded audio file, and `GET /version`.

## PostgreSQL sighting registration

Without `--no-register`, the CLI initialises and writes to PostgreSQL. Set these variables before running it:

```bash
export SCHEMA_PATH=src/chirpedex/core/db/sql/01-schema.sql
export POSTGRES_USERNAME=postgres
export POSTGRES_PASSWORD=your-password
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=chirpedex
```

Start the bundled development database with:

```bash
docker compose up -d postgres
```

Do not commit the resulting `.env` file or database credentials.

## Docker

Build the runtime image:

```bash
docker compose --profile prod build chirpedex
```

The runtime image intentionally does not include example audio or database schema files. Mount the working tree when passing an audio file or schema path:

```bash
docker compose --profile prod run --rm \
  -v "$PWD:/workspace:ro" \
  -e SCHEMA_PATH=/workspace/src/chirpedex/core/db/sql/01-schema.sql \
  chirpedex identify --no-register /workspace/examples/audio/buzzard.mp3
```

Run the test image:

```bash
docker compose --profile testing run --rm chirpedex-test
```

## Testing

Run the unit tests locally:

```bash
uv run pytest
```

The test suite uses mocked inference and does not download or run the BirdNET model.

## Project layout

```text
src/chirpedex/
├── client/
│   ├── api/                 # FastAPI application
│   ├── cli/                 # Command parsing and CLI commands
│   └── identify_and_record_service.py
└── core/
    ├── audio.py             # Audio validation helpers
    ├── db/                  # Repository and PostgreSQL schema
    ├── identification/      # Local and remote identifier backends
    └── models.py            # Prediction and sighting models
tests/
examples/audio/
```

## Current limitations

- Streaming identification is not implemented.
- The CLI accepts `--json`, but JSON output is not rendered yet.
- BirdNET model data is fetched at runtime; model weights are not committed to the repository.

## License

See [LICENSE](LICENSE).
