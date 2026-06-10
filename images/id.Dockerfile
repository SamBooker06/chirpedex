FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app


# Copy project metadata and source before sync so the package is installed.
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project --no-dev

COPY src ./src

RUN uv sync --frozen --no-dev --no-editable

FROM python:3.12-slim-bookworm AS runtime

# Create non-root user
RUN groupadd --system --gid 999 nonroot && \
    useradd --system --gid 999 --uid 999 --create-home nonroot

COPY --from=builder /app/.venv /app/.venv

USER nonroot
# Rewrite so that the uv binary is moved and we copy the lock and stop using pip
# Entry point

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["chirpedex"]

CMD ["--help"]
