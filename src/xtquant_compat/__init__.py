"""MiniQMT-style APIs backed by a Big QMT file bridge."""

from . import xtdata
from .config import configure

__all__ = ["configure", "xtdata"]
__version__ = "0.1.0"
