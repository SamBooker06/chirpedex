# AGENTS.md

## Project: Chirpedex

Chirpedex is a bird identification project. The long-term goal is to build a portable bird “Pokédex” that can listen to birdsong, identify species, and save sightings to a personal collection.

The current priority is **not** the full product. The current priority is a small, reliable proof-of-concept:

```bash
python -m chirpedex identify path/to/audio.wav
```

or, using Docker:

```bash
docker compose run --rm chirpedex identify path/to/audio.wav
```

which returns a likely bird species and confidence score.

---

## Current milestone

### Milestone 1: Dockerised audio identification CLI

Build a Python CLI tool that can:

1. Accept a local audio file.
2. Validate the file.
3. Run bird identification using an existing model/library/API where possible.
4. Return a structured prediction.
5. Handle errors cleanly.
6. Include basic tests.
7. Run cleanly inside Docker.

Do not train a custom ML model unless explicitly requested.

---

## Docker philosophy

Docker is part of the project from the start.

Use Docker to:

* isolate Python/audio/ML dependencies
* make the development environment reproducible
* avoid polluting the host machine
* prepare for future separation between CLI, backend, database, and frontend services

Do **not** use Docker as an excuse to overbuild the project.

For the current milestone, there should usually be only one main service:

```text
chirpedex
```

Later, more services may be added, for example:

```text
chirpedex-api
chirpedex-db
chirpedex-web
```

but these are out of scope until the CLI works.

---

## Expected Docker files

The project should include:

```text
Dockerfile
docker-compose.yml
.dockerignore
```

The Docker setup should support commands like:

```bash
docker compose run --rm chirpedex identify examples/test.wav
docker compose run --rm chirpedex pytest
docker compose run --rm chirpedex python -m chirpedex --help
```

The Docker image should:

* use Python 3.12+
* install dependencies reproducibly
* use a sensible working directory such as `/app`
* avoid copying unnecessary files
* avoid committing or baking large model files into the image
* use volumes for model caches or generated data if needed
* avoid running as root if practical

---

## Design principles

* Keep the project small and working.
* Prefer clear structure over clever abstractions.
* Use type hints throughout.
* Keep functions small and testable.
* Separate audio handling, inference, CLI, and data models.
* Keep the inference backend swappable.
* Use Docker for reproducibility and dependency isolation.
* Avoid adding frontend/backend/database features until the CLI works.

---

## Suggested architecture

```text
src/chirpedex/
  __init__.py
  __main__.py      # allows python -m chirpedex
  cli.py           # CLI entry points
  audio.py         # audio validation/loading helpers
  identifier.py    # BirdIdentifier interface and implementations
  models.py        # dataclasses / pydantic models for predictions
  errors.py        # custom exceptions
```

Tests should live in:

```text
tests/
```

Example audio files, if used, should be small and documented. Do not commit large datasets or model weights.

---

## Code style

Use:

* Python 3.12+
* type hints
* pathlib instead of raw string paths
* dataclasses or Pydantic for structured data
* pytest for tests
* clear exception types
* readable names

Avoid:

* global mutable state
* hard-coded absolute paths
* large untested functions
* unnecessary frameworks
* premature frontend/backend/database work
* committing model weights or large audio files
* building multiple Docker services before the CLI works

---

## CLI behaviour

Target local command:

```bash
python -m chirpedex identify examples/test.wav
```

Target Docker command:

```bash
docker compose run --rm chirpedex identify examples/test.wav
```

Example output:

```text
Species: European Robin
Scientific name: Erithacus rubecula
Confidence: 0.92
```

JSON output can be added later, for example:

```bash
python -m chirpedex identify examples/test.wav --json
```

---

## Testing expectations

Add tests for:

* valid audio file path handling
* missing file handling
* unsupported file extension handling
* prediction schema/model
* CLI argument parsing
* mocked bird identifier output

Do not require real ML inference in unit tests. Mock inference where appropriate.

Tests should be runnable both locally and inside Docker:

```bash
pytest
docker compose run --rm chirpedex pytest
```

---

## Out of scope unless explicitly requested

Do not implement these yet:

* web frontend
* mobile app
* user accounts
* PostgreSQL
* Raspberry Pi deployment
* GPS
* real-time listening
* custom model training
* social/sharing features
* cloud deployment
* production Docker Compose stack

These are future phases.

---

## Future roadmap

Possible future phases:

1. SQLite sighting storage
2. FastAPI backend as a separate Docker service
3. Web dashboard as a separate Docker service
4. PostgreSQL database as a separate Docker service
5. Raspberry Pi microphone recording
6. Offline edge inference
7. GPS-tagged sightings
8. Battery-aware device design
9. E-ink display
10. Bird collection / Pokédex interface

Build only the current milestone unless instructed otherwise.
