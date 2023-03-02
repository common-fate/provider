from dataclasses import dataclass, asdict
import typing


@dataclass
class Log:
    level: typing.Literal["INFO", "ERROR"]
    msg: str


class Logs:
    logs: typing.List[Log]

    def __init__(self) -> None:
        self.logs = []

    def info(self, msg: str):
        self.logs.append(Log("INFO", msg=msg))

    def error(self, msg: str):
        self.logs.append(Log("ERROR", msg=msg))

    def has_no_errors(self) -> bool:
        has_error = any([l for l in self.logs if l.level == "ERROR"])
        return not has_error

    def export_logs(self) -> typing.List[dict]:
        """
        Returns the diagnostic logs as a list of simple dict objects
        so that it can be easily serialised as JSON.
        """
        return [asdict(l) for l in self.logs]
