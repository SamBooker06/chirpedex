from datetime import datetime
from unittest.mock import MagicMock

from psycopg.sql import SQL

from chirpedex.core.db.models.bird_sighting_create import BirdSightingCreate
from chirpedex.core.db.postgres_repo import PostgresChirpedexRepo


def make_repo(cursor: MagicMock) -> PostgresChirpedexRepo:
    repo = object.__new__(PostgresChirpedexRepo)
    repo.connection_pool = MagicMock()
    repo.connection_pool.connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = cursor
    return repo


def test_init_db_executes_schema_read_from_file() -> None:
    cursor = MagicMock()
    repo = make_repo(cursor)
    schema = "CREATE TABLE bird (id INTEGER PRIMARY KEY);"

    repo.init_db(schema)

    executed_schema = cursor.execute.call_args.args[0]
    assert isinstance(executed_schema, SQL)
    assert executed_schema.as_string(None) == schema


def test_add_sighting_upserts_bird_and_inserts_sighting() -> None:
    cursor = MagicMock()
    repo = make_repo(cursor)
    sighting = BirdSightingCreate(
        scientific_name="Erithacus rubecula",
        common_name="European Robin",
        timestamp=datetime(2026, 6, 19, 12, 0, 0),
    )

    repo.add_sighting(sighting)

    query, parameters = cursor.execute.call_args.args
    assert "ON CONFLICT (scientific_name)" in query
    assert "DO UPDATE SET common_name = EXCLUDED.common_name" in query
    assert "RETURNING id" in query
    assert "SELECT id, %s, %s" in query
    assert parameters == (
        "Erithacus rubecula",
        "European Robin",
        None,
        datetime(2026, 6, 19, 12, 0, 0),
    )
