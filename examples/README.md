# Example Audio Files

This directory is intended to hold example bird audio files for testing and demonstration.

Note: Audio files are not committed to the repository to keep the project size small.

## Where to find bird audio samples:

1. **Xeno-canto** (https://xeno-canto.org/)
   - Free bird recordings from around the world
   - Multiple recordings per species
   - High quality and well-documented

2. **Macaulay Library** (https://www.macaulaylibrary.org/)
   - From Cornell Lab of Ornithology
   - Extensive bird audio archive
   - Many species with multiple recordings

3. **BirdCLIP Dataset** (https://github.com/slizeng/BirdCLIP)
   - Curated for bird sound classification
   - Well-labeled examples

## Example usage:

Once you've added an example audio file like `robin.wav`:

```bash
# Local
python -m chirpedex identify examples/robin.wav

# Docker
docker compose run --rm chirpedex identify examples/robin.wav
```

## Recommended test species:

- European Robin (*Erithacus rubecula*) - Clear, distinctive call
- Great Tit (*Parus major*) - Repetitive, easy to identify
- Common Blackbird (*Turdus merula*) - Melodious song
- Blue Tit (*Cyanistes caeruleus*) - High-pitched calls

These are easily found on xeno-canto.org or the Macaulay Library.

