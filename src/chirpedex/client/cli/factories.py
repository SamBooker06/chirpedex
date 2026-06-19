import os
from argparse import Namespace, ArgumentError
from typing import cast

from psycopg.sql import SQL

from chirpedex.client.cli.command import Command
from chirpedex.client.cli.identify.identify_multi import IdentifyMultiCommand
from chirpedex.client.cli.identify.identify_single import IdentifySingleCommand
from chirpedex.client.cli.serve import ServeCommand
from chirpedex.client.identify_and_record_service import IdentifyAndRecordService
from chirpedex.core.db.no_repo import NoRepo
from chirpedex.core.db.postgres_repo import PostgresChirpedexRepo
from chirpedex.core.identification.birdnet_identifier import BirdNETIdentifier
from chirpedex.core.identification.remote_identifier import RemoteIdentifier


class CommandFactory:
    @staticmethod
    def create_command(args: Namespace) -> Command:
        if args.command == "identify":
            return IdentifyCommandFactory.create_command(args)

        elif args.command == "serve":
            return ServeCommandFactory.create_command(args)

        raise ArgumentError(None, f"Unknown command: {args.command}")


class ServeCommandFactory(CommandFactory):
    @staticmethod
    def create_command(args: Namespace) -> Command:
        return ServeCommand(args.host, args.port)


class IdentifyCommandFactory(CommandFactory):
    DEFAULT_SCHEMA_PATH = ""

    @staticmethod
    def create_command(args: Namespace) -> Command:
        audio_paths = args.audio_path

        assert audio_paths is not None

        if type(args.audio_path) is str:
            args.audio_path = [args.audio_path]

        assert len(audio_paths) >= 1
        assert all(isinstance(path, str) for path in audio_paths)

        schema_path = os.getenv("SCHEMA_PATH", None)
        assert schema_path is not None, "Schema path is not set"

        host = args.host
        port = args.port

        identifier = BirdNETIdentifier() if not args.remote else RemoteIdentifier(host, port)

        if not args.no_register:
            db = PostgresChirpedexRepo()

            with open(schema_path, "r") as f:
                contents = cast(SQL, cast(object, f.read()))
                db.init_db(contents)

        else:
            db = NoRepo()

        identification_service = IdentifyAndRecordService(identifier, db)

        if len(audio_paths) > 1:
            identify_command = IdentifyMultiCommand(identification_service, audio_paths)

        else:
            identify_command = IdentifySingleCommand(identification_service, audio_paths[0])

        return identify_command
