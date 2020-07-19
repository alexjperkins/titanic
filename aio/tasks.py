from typing import Coroutine

from .types import Scheduler


class Task:
    def __init__(self, coro: Coroutine, scheduler: Scheduler):
        self._coro = coro
        self._scheduler = scheduler

    def __call__(self):
        try:
            setattr(self._scheduler, 'current', self)
            self._coro.send(None)
            if self._scheduler.current:
                self._scheduler.call_soon(self)

        except StopIteration:
            pass
