import os

import fsspec

MBX_DATA_URI = os.getenv("MBX_DATA_URI", "file://./_mbxdata")


def resolve_path(subpath: str) -> str:
    return f"{MBX_DATA_URI.rstrip('/')}/{subpath.lstrip('/')}"


def open_file(subpath: str, mode: str = "rb"):
    return fsspec.open(resolve_path(subpath), mode).open()
