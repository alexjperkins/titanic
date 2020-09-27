import abc
from typing import Any, Dict, List, Mapping, Tuple


# Controller
class IAsyncControl(abc.ABC):
    @abc.abstractmethod
    async def start(self):
        pass

    @abc.abstractmethod
    async def send(self, *, destination: str, msg: str) -> None:
        pass

    @abc.abstractmethod
    async def broadcast(self, *, msg: str) -> None:
        pass


# Networks
class INetwork(abc.ABC):

    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def send(self, *, destination: str, msg: str) -> None:
        pass

    @abc.abstractmethod
    def recv(self):
        pass


class IAsyncNetwork(abc.ABC):

    @abc.abstractproperty
    def identification(self) -> Any:
        """Any means of unique identification."""
        pass

    @abc.abstractmethod
    async def start(self) -> None:
        pass

    @abc.abstractmethod
    async def send(self, *, destination: str, msg: str) -> None:
        pass

    @abc.abstractmethod
    async def recv(self) -> None:
        pass


# States
class IState(abc.ABC):
    @abc.abstractmethod
    def change_state(self, *, to: "IState") -> None:
        pass


# Sockets
class ISocketFactory(abc.ABC):

    @abc.abstractclassmethod
    def build_read_socket(cls, *, host: str, port: int, blocking: bool = False):
        pass

    @abc.abstractclassmethod
    def build_write_socket(cls, *, blocking: bool = False):
        pass


# Serialization
class ISerializer(abc.ABC):

    @abc.abstractclassmethod
    def serialize(cls, msg: Any) -> Any:
        pass

    @abc.abstractclassmethod
    def deserialize(cls, msg: Any) -> Any:
        pass


# Messages
class IMessage:
    @abc.abstractmethod
    def __repr__(self):
        pass


class BaseMessage(abc.ABC):
    def __init__(self, sender: str, msg: IMessage):
        self._sender = sender
        self._msg = msg

    @abc.abstractmethod
    def to_tuple(self):
        pass

    @abc.abstractmethod
    def __repr__(self):
        pass


# Config
class IConfig(abc.ABC):

    @abc.abstractmethod
    def to_dict(self) -> Dict[Any, Any]:
        pass

    @abc.abstractproperty
    def servers(self) -> Mapping:
        pass
