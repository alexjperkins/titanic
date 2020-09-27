import asyncio
import random
import sys
from pathlib import Path

root = Path(__file__).parent.absolute()
sys.path.append(str(root))
sys.path.append("..")
sys.path.append(".")

from . control import AsyncControl
from . config import RaftConfig
from . messaging.network import Address
from . network import AsyncNetwork
from . serialization import PickleSerializer
from . sockets.factories import AsyncSocketFactory


SERVERS = {
    0: ('localhost', 8880),
    1: ('localhost', 8881),
    2: ('localhost', 8882),
}


def bootstrap(iden: int, loop) -> AsyncControl:

    servers = {
        k: Address(*v, identification=k) for k, v in
        SERVERS.items()
    }

    cfg = RaftConfig(
        servers=servers
    )

    host, port = SERVERS[iden]
    address = Address(host=host, port=int(port), identification=iden)

    net = AsyncNetwork(
        address=address,
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
        msg = f"{salt}"
        await controller.broadcast(msg=msg)
        to_sleep = random.randint(1, 5)
        await asyncio.sleep(to_sleep)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ./raft <server identifier: int>")
        raise RuntimeError

    iden = sys.argv[1]
    asyncio.run(main())
