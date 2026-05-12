import sys
from pathlib import Path


def get_base_path():
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    return Path(__file__).resolve().parent.parent


def resource_path(*parts):
    return get_base_path().joinpath(*parts)
