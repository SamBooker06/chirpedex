# Chirpedex

A portable bird identification system ("Pokédex for birds") that can listen to birdsong, identify species, and save sightings to a personal collection.

## Quick Start

### Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/chirpedex.git
   cd chirpedex
   ```

2. Install dependencies with `uv`:
   ```bash
   uv sync
   ```

3. Run the CLI:
   ```bash
   uv run python -m chirpedex identify path/to/audio.wav
   ```

### Docker Usage

Build the image:
```bash
docker compose build
```

Run identification:
```bash
docker compose run --rm chirpedex identify path/to/audio.wav
```

Run tests:
```bash
docker compose run --rm chirpedex pytest
```

Show help:
```bash
docker compose run --rm chirpedex --help
```

## Example Output

```
Species: European Robin
Scientific name: Erithacus rubecula
Confidence: 0.92
```

## Project Structure

```
chirpedex/
├── README.md
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── src/
│   └── chirpedex/
│       └── identification/
│           ├── identifier.py            # Bird identification interface
│           └── birdnet_identifier.py    # Identification using birdnet
│       ├── __init__.py
│       ├── __main__.py        # Entry point for python -m chirpedex
│       ├── cli.py             # CLI interface
│       ├── audio.py           # Audio file validation
│       ├── models.py          # Data models
│       └── errors.py          # Custom exceptions
└── tests/
    ├── test_cli.py
    ├── test_audio.py
    ├── test_models.py
    ├── test_identifier.py
    └── conftest.py
```

## Architecture

### Audio Module (`audio.py`)
- Handles audio file validation
- Supports: WAV, MP3, FLAC, OGG, M4A
- Validates file existence and format

### Identifier Module (`identifier.py`)
- Abstract `BirdIdentifier` interface
- `BirdNETIdentifier` implementation using the BirdNET model
- Keeps inference backend swappable for future alternatives

### Models Module (`models.py`)
- `BirdPrediction` dataclass
- Contains: common name, scientific name, confidence, timestamp, source path

### CLI Module (`cli.py`)
- Argument parsing with subcommands
- `identify` command for bird audio analysis
- Structured output with human-readable formatting
- Future support for JSON output

## Testing

Run all tests locally:
```bash
pytest
```

Run tests in Docker:
```bash
docker compose run --rm chirpedex pytest
```

Test coverage includes:
- CLI argument parsing and command handling
- Audio file validation (exists, format)
- Prediction schema and output
- Mocked inference results
- Error handling

## Machine Learning Model

Uses [BirdNET](https://birdnet.cornell.edu/) for bird sound classification:
- Trained on Cornell Lab of Ornithology data
- Supports 6,000+ global bird species
- Model weights downloaded automatically on first run (~1 GB)
- Cached locally for subsequent runs

## Future Roadmap

1. **Phase 2**: SQLite sighting storage
2. **Phase 3**: FastAPI backend and web dashboard
3. **Phase 4**: Raspberry Pi integration
4. **Phase 5**: GPS-tagged sightings
5. **Phase 6**: Offline edge inference
6. **Phase 7**: PostgreSQL backend
7. **Phase 8**: Portable device design
8. **Phase 9**: E-ink display interface

## Development

### Install development environment:
```bash
uv sync
```

### Run the application:
```bash
uv run python -m chirpedex identify path/to/audio.wav
```

### Run tests locally:
```bash
uv run pytest
```

### Code style:
- Python 3.12+
- Type hints throughout
- Pytest for tests
- Clear error messages
- Pathlib for file paths

### Running tests with coverage:
```bash
uv run pytest --cov=src/chirpedex tests/
```

## Docker Configuration

### Dockerfile
- Based on `python:3.12-slim-bookworm`
- System dependencies: libsndfile1 (for audio processing)
- Non-root user for security
- Includes model cache volume for persistence
- Multi-stage build approach (future optimization)

### Docker Compose
- Single service: `chirpedex`
- Volume mounts for development and caching
- Supports local audio files via volume binding

### Supported commands:
```bash
# Identify a bird
docker compose run --rm chirpedex identify path/to/audio.wav

# Run tests
docker compose run --rm chirpedex pytest

# Show help
docker compose run --rm chirpedex --help
```

## Contributing

See `AGENTS.md` for implementation guidelines and design principles.

## License

See LICENSE file.

## References

- [BirdNET](https://birdnet.cornell.edu/)
- [Cornell Lab of Ornithology](https://www.birds.cornell.edu/)
- [birdnetlib Python package](https://pypi.org/project/birdnetlib/)

