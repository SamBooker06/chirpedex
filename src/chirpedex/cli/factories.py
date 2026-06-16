from argparse import Namespace, ArgumentError

from chirpedex.cli.command import Command
from chirpedex.cli.identify.identify_multi import IdentifyMultiCommand
from chirpedex.cli.identify.identify_single import IdentifySingleCommand
from chirpedex.cli.serve import ServeCommand
from chirpedex.identification.birdnet_identifier import BirdNETIdentifier
from chirpedex.identification.remote_identifier import RemoteIdentifier


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
    @staticmethod
    def create_command(args: Namespace) -> Command:
        audio_paths = args.audio_path

        assert audio_paths is not None

        if type(args.audio_path) is str:
            args.audio_path = [args.audio_path]

        assert len(audio_paths) >= 1
        assert all(isinstance(path, str) for path in audio_paths)

        host = args.host
        port = args.port

        identifier = BirdNETIdentifier() if not args.remote else RemoteIdentifier(host, port)

        if len(audio_paths) > 1:
            return IdentifyMultiCommand(identifier, audio_paths)

        else:
            return IdentifySingleCommand(identifier, audio_paths[0])
