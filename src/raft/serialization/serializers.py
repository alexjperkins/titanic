import pickle

from .. interfaces import ISerializer


class PickleSerializer(ISerializer):
    @classmethod
    def serialize(cls, *, msg: str) -> bytes:  # type: ignore
        return pickle.dumps(msg)  # type: ignore

    @classmethod
    def deserialize(cls, *, msg: bytes) -> str:  # type: ignore
        return pickle.loads(msg)  # type: ignore
