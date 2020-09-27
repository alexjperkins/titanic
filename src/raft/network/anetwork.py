import asyncio
import collections
import logging
import socket
from typing import Any, Awaitable, Dict, Tuple

from .. interfaces import (
    IAsyncNetwork, IConfig, ISerializer, ISocketFactory
)
from .. messaging.network import Address, NetworkMessage
from .. sockets.factories import AsyncSocketFactory


class AsyncNetwork(IAsyncNetwork):
    def __init__(
        self,
        *,
        address: Address,
        config: IConfig,
        loop: asyncio.BaseEventLoop,
        serializer: ISerializer,
        socket_factory: ISocketFactory = AsyncSocketFactory,  # type: ignore
        max_buffer_size: int = 4096,
    ):
        self._address = address
        self._config = config
        self._loop = loop
        self._socket_factory = socket_factory
        self._serializer = serializer
        self._max_buffer_size = max_buffer_size

        self._connections: Dict[int, socket.SocketType] = {}
        self._cluster = self._config.servers

        self._inbound: asyncio.Queue = asyncio.Queue()
        self._outbound: Dict[int, asyncio.Queue] = (
            collections.defaultdict(asyncio.Queue)
        )

        self._log = logging.getLogger(__file__)

    @property
    def identification(self) -> int:
        return self._address.identification

    async def start(self) -> None:
        self._loop.create_task(self._receiver_server())

    async def send(self, *, destination: Address, msg: NetworkMessage) -> None:

        network_msg = NetworkMessage(
            source=self._address,
            dest=destination,
            msg=msg
        )

        await self._outbound[destination.identification].put(network_msg)  # NOQA
        self._loop.create_task(self._sender(destination))

    async def recv(self) -> Awaitable[NetworkMessage]:
        return await self._inbound.get()

    async def _sender(self, destination: Address):
        while True:

            msg = await self._outbound[destination.identification].get()

            if destination.identification not in self._connections:
                client_socket = self._socket_factory.build_write_socket()
                try:
                    await self._loop.sock_connect(
                        client_socket, (destination.host, destination.port)
                    )

                except (IOError, socket.error):
                    self._log.warning(
                        "Connection to %s failed", destination, exc_info=True
                    )
                    continue

                except Exception:
                    self._log.error(
                        "Connection to %s failed", destination, exc_info=True
                    )
                    continue

                else:
                    self._connections[destination.identification] = client_socket  # NOQA

            serialized_msg = self._serializer.serialize(msg=msg)

            try:
                await self._loop.sock_sendall(
                    self._connections[destination.identification], serialized_msg  # NOQA
                )

            except IOError:
                self._log.warning("Failed to send %r", msg, exc_info=True)
                self._close_connection(destination)

            except Exception:
                self._log.error("Failed to send %r", msg, exc_info=True)
                self._close_connection(destination)

            else:
                self._log.info("sent %r")

    async def _receiver_server(self):
        server_socket = self._socket_factory.build_read_socket(
            host=self._address.host,
            port=self._address.port
        )

        self._log.info(
            "%s receiver server starting on %s",
            self.identification, self._address
        )

        while True:
            client, addr = await self._loop.sock_accept(server_socket)
            self._log.info("connection made from %s", addr)

            self._loop.create_task(self._reciever(client))

    async def _reciever(self, client):
        while True:
            # we should close the socket here, and reconnect
            msg = b""
            while True:
                chunk = await self._loop.sock_recv(
                    client, self._max_buffer_size
                )
                msg += chunk

                if len(chunk) < self._max_buffer_size:
                    break

            deserialized_msg = self._serializer.deserialize(msg=msg)
            self._log.info("received msg %s")

            await self._inbound.put(deserialized_msg)

    def _close_connection(self, destination: Address) -> None:
        self._connections[destination.identification].close()
        del self._connections[destination.identification]
