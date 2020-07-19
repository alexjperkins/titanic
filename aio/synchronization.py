class Lock:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass  # for now


class Awaitable:
    def __await__(self):
        yield
