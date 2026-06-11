FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS build

WORKDIR /app


# Copy project metadata and source before sync so the package is installed.
COPY ./pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project --no-dev

COPY ./src ./src

RUN uv sync --frozen --no-dev --no-editable

FROM build AS test
RUN uv sync --frozen --no-editable

COPY tests ./tests

CMD ["uv", "run", "pytest"]



FROM python:3.12-slim-bookworm AS runtime

# Create non-root user
RUN groupadd --system --gid 999 nonroot && \
    useradd --system --gid 999 --uid 999 --create-home nonroot

COPY --from=build /app/.venv /app/.venv

USER nonroot
# Rewrite so that the uv binary is moved and we copy the lock and stop using pip
# Entry point

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["chirpedex"]
