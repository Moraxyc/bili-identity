import pkgutil

try:
    VERSION_bin = pkgutil.get_data("bili_identity", "VERSION")
    __version__ = (
        VERSION_bin.decode("utf-8", "ignore") if VERSION_bin else "unknown"
    )
except Exception:
    __version__ = "unknown"

__all__ = ["__version__"]
