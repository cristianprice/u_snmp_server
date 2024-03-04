from micropython import const


LOGGING = const(0)


def debug(*args, **kwargs) -> None:
    print(*args, **kwargs)


def warning(*args, **kwargs) -> None:
    print(*args, **kwargs)


def setLevel(level) -> None:
    pass
