import abc
from typing import Any, Awaitable, Dict, List, Mapping, Tuple

from . messaging.network import Address, NetworkMessage
from . sockets.socket import Socket


# Controller
class IAsyncControl(abc.ABC):
    @abc.abstractmethod
    async def start(self):
        pass

    @abc.abstractmethod
    async def send(self, *, destination: Address, msg: Any) -> None:
        pass

    @abc.abstractmethod
    async def broadcast(self, *, msg: Any) -> None:
        pass


# Networks
class INetwork(abc.ABC):

    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def send(self, *, destination: Address, msg: NetworkMessage) -> None:
        pass

    @abc.abstractmethod
    def recv(self) -> NetworkMessage:
        pass


class IAsyncNetwork(abc.ABC):

    @abc.abstractproperty
    def identification(self) -> int:
        """Any means of unique identification."""
        pass

    @abc.abstractmethod
    async def start(self) -> None:
        pass

    @abc.abstractmethod
    async def send(self, *, destination: Address, msg: NetworkMessage) -> None:
        pass

    @abc.abstractmethod
    async def recv(self) -> Awaitable[NetworkMessage]:
        pass


# Sockets
class ISocketFactory(abc.ABC):

    @abc.abstractclassmethod
    def build_read_socket(
            cls, *, host: str, port: int, blocking: bool = False
    ) -> Socket:
        pass

    @abc.abstractclassmethod
    def build_write_socket(cls, *, blocking: bool = False) -> Socket:
        pass


# Serialization
class ISerializer(abc.ABC):

    @abc.abstractclassmethod
    def serialize(cls, *, msg: Any) -> bytes:
        pass

    @abc.abstractclassmethod
    def deserialize(cls, *, msg: bytes) -> Any:
        pass


# Config
class IConfig(abc.ABC):

    @abc.abstractmethod
    def to_dict(self) -> Dict[Any, Any]:
        pass

    @abc.abstractproperty
    def servers(self) -> Mapping[int, Address]:
        pass
