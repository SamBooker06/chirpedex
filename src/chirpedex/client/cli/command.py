from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import TypeVar, Generic, Optional

from chirpedex.client.cli.exit_codes import ExitCode

T = TypeVar("T")

@dataclass(frozen=True)
class CommandResult(Generic[T]):
    """
    Represents the result of executing a command.

    This class encapsulates details about the result of a command execution,
    including the exit code, whether an error occurred, and any output produced.
    It is generic and allows specifying the type of the output.

    :ivar exit_code: The exit code of the command execution.
    :type exit_code: ExitCode
    :ivar output: The output produced by the command execution, if any.
    :type output: Optional[T]
    :ivar is_error: Indicates whether the command execution resulted in an error.
    :type is_error: bool
    """
    exit_code: ExitCode
    output: Optional[T] = None
    is_error: bool = False

    def __str__(self) -> str:
        return str(self.output)


class Command(ABC):
    @abstractmethod
    def execute(self) -> CommandResult:
        pass


