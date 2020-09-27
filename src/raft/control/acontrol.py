import asyncio
from typing import Any, Awaitable

from .. interfaces import IConfig, IAsyncControl, IAsyncNetwork
from .. messaging.network import Address, NetworkMessage


class AsyncControl(IAsyncControl):
    def __init__(
        self,
        *,
        identifier: int,  # move to address
        network: IAsyncNetwork,
        cfg: IConfig,
    ):
        self._identifier = identifier  # own `destination`
        self._network = network
        self._cfg = cfg

        self._peers = {
            iden: address for iden, address in self._cfg.servers.items()
            if iden is not self._identifier
        }

    async def start(self) -> None:
        asyncio.create_task(self._network.start())

    async def send(self, *, destination: Address, msg: Any) -> None:
        return await self._network.send(destination=destination, msg=msg)

    async def broadcast(self, *, msg: Any) -> None:
        for _, destination in self._peers.items():
            await self._network.send(destination=destination, msg=msg)

    async def recv(self) -> Awaitable[NetworkMessage]:
        return await self._network.recv()
