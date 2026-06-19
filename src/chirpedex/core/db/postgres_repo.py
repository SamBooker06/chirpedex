import os
from typing import LiteralString, List

from psycopg.sql import SQL
from psycopg_pool import ConnectionPool

from chirpedex.core.db import ChirpedexRepository
from chirpedex.core.db.models.bird_sighting import BirdSighting
from chirpedex.core.db.models.bird_sighting_create import BirdSightingCreate


class PostgresChirpedexRepo(ChirpedexRepository):
    def __init__(self, connection_string: str | None = None):
        if connection_string is None:
            username = os.getenv("POSTGRES_USERNAME", "postgres")
            password = os.getenv("POSTGRES_PASSWORD", "")
            host = os.getenv("POSTGRES_HOST", "localhost")
            port = os.getenv("POSTGRES_PORT", "5432")
            db_name = os.getenv("POSTGRES_DB", "chirpedex")

            connection_string = f"postgresql://{username}:{password}@{host}:{port}/{db_name}"

        self.connection_pool = ConnectionPool(connection_string)

    def init_db(self, schema: SQL | LiteralString):
        with self.connection_pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(schema)

    def get_sightings_by_scientific_name(self, scientific_name: str) -> List[BirdSighting]:
        with self.connection_pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM bird_sighting JOIN bird ON bird_sighting.bird_id = bird.id WHERE bird.scientific_name = %s",
                    (scientific_name,))
                results = cursor.fetchall()
                return [BirdSighting.model_validate(row) for row in results]

    def get_sightings_by_common_name(self, common_name: str) -> List[BirdSighting]:
        with self.connection_pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM bird_sighting JOIN bird ON bird_sighting.bird_id = bird.id WHERE bird.common_name = %s",
                    (common_name,))
                results = cursor.fetchall()
                return [BirdSighting.model_validate(row) for row in results]

    def add_sighting(self, bird_sighting: BirdSightingCreate) -> None:
        with self.connection_pool.connection() as conn:
            with conn.cursor() as cursor:
                scientific_name = bird_sighting.scientific_name
                common_name = bird_sighting.common_name
                location = bird_sighting.location
                timestamp = bird_sighting.timestamp

                # Will also add a bird if it doesn't exist
                cursor.execute("""
                               WITH upserted_bird AS (
                                   INSERT INTO bird (scientific_name, common_name)
                                       VALUES (%s, %s) ON CONFLICT (scientific_name) DO UPDATE SET common_name=EXCLUDED.common_name RETURNING bird.id)
                               INSERT
                               INTO bird_sighting (bird_id, location, timestamp)
                               VALUES ((SELECT id FROM upserted_bird), %s, %s)
                               """, (scientific_name, common_name, location, timestamp))
