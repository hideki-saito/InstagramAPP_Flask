from .client import PynstagramClient


def client(*args, **kwargs):
    return PynstagramClient(*args, **kwargs)
