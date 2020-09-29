import asyncio
import random
import os
import sys
from pathlib import Path

root = Path(__file__).parent.absolute()
sys.path.append(str(root))
sys.path.append("..")
sys.path.append(".")

from . control import AsyncControl
from . config import (
    RaftConfig, build_config_from_json, build_config_from_yaml
)
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
        iden: Address(*address, identification=iden) for iden, address in
        SERVERS.items()
    }

    if os.environ.get('RAFT_USE_DOCKER', False):
        builder_mapping = {
            "json": build_config_from_json,
            "yaml": build_config_from_yaml
        }

        cfg_path = os.environ['RAFT_CONFIG_PATH']
        extension = cfg_path.split('.')[-1]

        print(f'building raft cfg from {cfg_path}...')
        cfg_builder = builder_mapping[extension]
        cfg = cfg_builder(filepath=cfg_path)

    else:
        print('building raft cfg...')
        cfg = RaftConfig(
            servers=servers
        )

    address = cfg.servers[iden]
    print('raft server starting @', address)

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
