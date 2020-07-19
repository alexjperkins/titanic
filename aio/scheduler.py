import heapq
import select
import time

from collections import deque
from typing import ByteString, Callable, Coroutine, Deque, List, Union

from . tasks import Task
from . synchronization import Awaitable, Lock


class Scheduler:
    def __init__(self):
        self.ready: Deque = deque()
        self._waiting: List = []
        self.sequence = 0
        self.current = None
        self._read_waiting = {}
        self._write_waiting = {}

    @property
    def is_busy(self) -> bool:
        return (
            self.ready or
            self._waiting or
            self._read_waiting or
            self._write_waiting
        )

    @staticmethod
    def switch() -> Awaitable:
        return Awaitable()

    def call_soon(self, func: Callable, *args) -> None:
        self.ready.append((func, args))

    def call_later(self, delay: Union[float, int], func: Callable, *args) -> None:
        deadline = time.time() + delay
        with Lock:
            self.sequence += 1
            heapq.heappush(
                self._waiting, (deadline, self.sequence, func, args)
            )

    def read_wait(self, fileno: int, func: Callable) -> None:
        self._read_waiting[fileno] = func

    def write_wait(self, fileno: int, func: Callable) -> None:
        self._write_waiting[fileno] = func

    def new_task(self, coro: Coroutine):
        self.call_soon(Task(coro, scheduler=self))

    async def sleep(self, delay: Union[float, int]) -> None:
        self.call_later(delay, self.current)
        self.current = None
        await self.switch()

    async def recv(self, sock, maxbytes: int) -> ByteString:
        self.read_wait(sock, self.current)
        self.current = None
        await self.switch()
        return sock.recv(maxbytes)

    async def send(self, sock, data: ByteString) -> ByteString:
        self.write_wait(sock, self.current)
        self.current = None
        await self.switch()
        return sock.send(data)

    async def accept(self, sock):
        self.read_wait(sock, self.current)
        self.current = None
        await self.switch()
        return sock.accept()

    def run(self) -> None:
        while self.is_busy():
            if not self.ready:
                if self._waiting:
                    deadline, _, func, args = heapq.heappop(self._waiting)
                    timeout = deadline - time.time()
                    if timeout < 0:
                        timeout = 0
                else:
                    timeout = None

                can_read, can_write, _ = select.select(
                    self._read_waiting,
                    self._write_waiting,
                    [],
                    timeout
                )

                for fd in can_read:
                    self.call_soon(self._read_waiting.pop(fd))

                for fd in can_write:
                    self.call_soon(self._write_waiting.pop(fd))

                now = time.time()
                while self._waiting:
                    if now > self._waiting[0][0]:
                        self.call_soon(heapq.heappush(self._waiting), *args)
                        continue
                    break

            while self.ready:
                func, args = self.ready.popleft()
                func(*args)
            pass
