import os

_here = os.path.dirname(__file__)

with open(os.path.join(_here, "VERSION")) as f:
    __version__ = f.read().strip()

__all__ = ["__version__"]
