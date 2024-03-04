from micropython import const


DEBUG = const(0)


def debug(*args, **kwargs) -> None:
    print(*args, **kwargs)


def warning(*args, **kwargs) -> None:
    print(*args, **kwargs)


def error(*args, **kwargs) -> None:
    print(*args, **kwargs)


def setLevel(level) -> None:
    pass
