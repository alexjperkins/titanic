import asyncio
import random
import time

from . control import AsyncControl
from . config import RaftConfig
from . network import AsyncNetwork
from . serialization import PickleSerializer
from . sockets import AsyncSocketFactory


SERVERS = {
    0: ('localhost', 8880),
    1: ('localhost', 8881),
    2: ('localhost', 8882),
}


def bootstrap(iden: int, loop) -> AsyncControl:
    cfg = RaftConfig(servers=SERVERS)
    net = AsyncNetwork(
        identifier=iden,
        address=SERVERS[iden],
        config=cfg,  # type: ignore
        loop=loop,
        socket_factory=AsyncSocketFactory,  # type: ignore
        serializer=PickleSerializer,  # type: ignore
        max_buffer_size=4096,
    )
    controller = AsyncControl(
        identifier=iden,
        network=net,  # type: ignore
        cfg=cfg,  # type: ignore
    )
    return controller


async def countin(down_from: int):
    counter = down_from
    while counter > 0:
        print(f"{counter}{'.'*counter}")
        await asyncio.sleep(1)
        counter -= 1

    return


async def main():
    loop = asyncio.get_event_loop()
    controller = bootstrap(int(iden), loop)

    await countin(5)
    loop.create_task(controller.start())

    while True:
        salt = random.randint(0, 10000)
        await controller.broadcast(msg=f"{time.monotonic()}: {salt}")
        to_sleep = random.randint(1, 5)
        await asyncio.sleep(to_sleep)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ./raft <server identifier: int>")
        raise RuntimeError

    iden = sys.argv[1]
    asyncio.run(main())
