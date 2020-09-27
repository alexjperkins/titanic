from raft.serialization.serializers import PickleSerializer

import pytest


class TestRPCMessage:
    name: str = 'name'
    age: int = 10


@pytest.mark.parametrize(
    'input_msg',
    [
        ("this is an input msg"),
        (""),
        ("!!!*daadsfa££asdkdjasdf"),
        (TestRPCMessage),
    ],
)
def test_pickle_serializer(input_msg):
    serialized = PickleSerializer.serialize(input_msg)
    assert isinstance(serialized, bytes)

    deserialized = PickleSerializer.deserialize(serialized)
    assert deserialized == input_msg
