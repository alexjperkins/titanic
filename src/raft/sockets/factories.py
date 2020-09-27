import functools

from typing import Tuple

from .. interfaces import ISocketFactory
from . import socket


class SocketFactory(ISocketFactory):
    @classmethod
    def build_read_socket(cls, *, host: str, port: int, blocking=True):
        sock = socket.Socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        sock.bind(host=host, port=port)
        sock.listen(1)
        sock.setblocking(blocking)
        return sock

    @classmethod
    def build_write_socket(cls, *, blocking=True):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        sock.setblocking(blocking)
        return sock


class AsyncSocketFactory(ISocketFactory):
    build_read_socket = functools.partial(
        SocketFactory.build_read_socket, blocking=False
    )

    build_write_socket = functools.partial(
        SocketFactory.build_write_socket, blocking=False
    )
