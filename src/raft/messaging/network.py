import datetime
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Address:
    host: str
    port: int
    identification: int

    def __repr__(self):
        return f"<Address: {self.host}:{self.port} [{self.identification}]>"

    def __str__(self):
        return f"{self.identification}@{self.host}:{self.port}"


@dataclass
class NetworkMessage:
    dest: Address
    source: Address
    msg: Any
    created_at: datetime.datetime = field(init=False)

    def __post_init__(self):
        self.created_at = datetime.datetime.utcnow()

    def __repr__(self):
        return (
            f"<NetworkMessage: src:{self.source}, "
            f"dest:{self.dest} msg:{self.msg}>"
        )

    def __str__(self):
        return f"[{self.created_at}] {self.source} -> {self.dest}: {self.msg}"
