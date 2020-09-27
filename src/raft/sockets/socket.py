import socket as _socket

from socket import *  # NOQA


class Socket(_socket.socket):
    def bind(self, host: str, port: int):  # type: ignore
        return super().bind(address=(host, port))
