import asyncio
import collections
import logging
import socket
from typing import Any, Dict, Tuple

from .. interfaces import IAsyncNetwork, IConfig, IMessage, ISerializer, ISocketFactory
from .. sockets import AsyncSocketFactory

Address = Tuple[str, int]
NetworkMessage = Tuple[Address, IMessage]


class AsyncNetwork(IAsyncNetwork):
    def __init__(
        self,
        *,
        identifier: Any,
        address: Address,
        config: IConfig,
        loop: asyncio.BaseEventLoop,
        serializer: ISerializer,
        socket_factory: ISocketFactory = AsyncSocketFactory,  # type: ignore
        max_buffer_size: int = 4096,
    ):
        self._identifier = identifier
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
    def identification(self) -> Any:
        return self._identifier

    async def start(self):
        self._loop.create_task(self._receiver_server())

    async def send(self, *, destination: int, msg: str):
        await self._outbound[destination].put((self._address, msg))
        self._loop.create_task(self._sender(destination))

    async def recv(self):
        return await self._inbound.get()

    async def close(self):
        ...

    async def _sender(self, destination: int):
        while True:
            msg = await self._outbound[destination].get()
            if destination not in self._connections:
                client_socket = self._socket_factory.build_write_socket()
                try:
                    await self._loop.sock_connect(
                        client_socket, self._cluster[destination]
                    )

                except (IOError, socket.error):
                    self._log.warning(
                        "Connection to %s failed",
                        self._cluster[destination], exc_info=True
                    )
                    continue

                except Exception:
                    self._log.error(
                        "Connection to %s failed",
                        self._cluster[destination], exc_info=True
                    )
                    continue

                else:
                    self._connections[destination] = client_socket

            serialized_msg = self._serializer.serialize(msg=msg)

            try:
                await self._loop.sock_sendall(
                    self._connections[destination], serialized_msg
                )

            except IOError:
                self._log.warning(
                    "Failed to send %r to %d", msg, destination, exc_info=True
                )
                self._connections[destination].close()
                del self._connections[destination]

            except Exception:
                self._log.error(
                    "Failed to send %r to %d", msg, destination, exc_info=True
                )
                self._connections[destination].close()
                del self._connections[destination]

            else:
                self._log.info("sent %r to %d", msg, destination)

    async def _receiver_server(self):
        server_socket = self._socket_factory.build_read_socket(
            address=self._address
        )

        self._log.info(
            "%s receiver server starting on %s",
            self._identifier, self._address
        )

        while True:
            client, addr = await self._loop.sock_accept(server_socket)
            self._log.info("connection made from %s", addr)

            self._loop.create_task(self._reciever(client, addr))

    async def _reciever(self, client, addr):
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
            self._log.info("received msg %s from %s", msg, addr)

            await self._inbound.put((self._identifier, deserialized_msg))
