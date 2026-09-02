"""Migration namespace for the unified :mod:`qmt_sdk` package."""

from qmt_sdk import data as xtdata
from qmt_sdk.bridge import configure

__all__ = ["configure", "xtdata"]
__version__ = "0.1.0"
