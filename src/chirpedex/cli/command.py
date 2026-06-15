from dataclasses import dataclass


@dataclass(frozen=True)
class CommandResult:
    """The output and exit status produced by a CLI command."""

    output: str
    exit_code: int
    is_error: bool = False
