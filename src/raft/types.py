from typing import NewType

from . network.messages import Address, NetworkMessage
from . sockets.socket import Socket


AddressType = NewType("AddressType", Address)
NetworkMessageType = NewType("NetworkMessageType", NetworkMessage)
SocketType = NewType("SocketType", Socket)
