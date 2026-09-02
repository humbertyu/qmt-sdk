"""Unified QMT SDK.

The SDK exposes one client for QMT and MiniQMT backends.  The existing
``xtquant_compat`` module remains available as a migration surface, while new
code should use the domain clients below.
"""

from .client import QmtClient
from .bridge import configure

__all__ = ["QmtClient", "configure"]
__version__ = "0.2.0"
