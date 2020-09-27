import pickle
from typing import Any

from .. interfaces import ISerializer


class PickleSerializer(ISerializer):
    @classmethod
    def serialize(cls, *, msg: Any) -> bytes:
        return pickle.dumps(msg)

    @classmethod
    def deserialize(cls, *, msg: bytes) -> Any:
        return pickle.loads(msg)
