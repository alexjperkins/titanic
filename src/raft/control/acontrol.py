import asyncio
import typing

from .. interfaces import IConfig, IAsyncControl, IAsyncNetwork, IMessage


class AsyncControl(IAsyncControl):
    def __init__(
        self,
        *,
        identifier: int,
        network: IAsyncNetwork,
        cfg: IConfig,
    ):
        self._identifier = identifier  # own `destination`
        self._network = network
        self._cfg = cfg

        self._peers = [
            peer for peer in self._cfg.servers.keys()
            if peer != self._identifier
        ]

    async def start(self) -> None:
        asyncio.create_task(self._network.start())

    async def send(self, *, destination: str, msg: str):
        return await self._network.send(destination=destination, msg=msg)

    async def broadcast(self, *, msg: str):
        for peer in self._peers:
            await self._network.send(destination=peer, msg=msg)
