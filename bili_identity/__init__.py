import os
import sys


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = getattr(sys, "_MEIPASS")
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)


with open(resource_path("VERSION")) as f:
    __version__ = f.read().strip()

__all__ = ["__version__"]
