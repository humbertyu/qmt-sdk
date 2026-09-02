"""Unified QMT SDK.

The SDK exposes one client for QMT and MiniQMT backends.  The existing
``xtquant_compat`` module remains available as a migration surface, while new
code should use the domain clients below.
"""

from .client import QmtClient
from .bridge import configure
import os
import sys
import sysconfig


def get_template_dir():
    """Return the installed directory containing QMT strategy templates."""
    candidates = []
    data_root = sysconfig.get_path("data")
    if data_root:
        candidates.append(os.path.join(data_root, "qmt_strategy"))
    # Source checkouts remain directly usable without building a wheel.
    candidates.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "qmt_strategy")))
    for path in candidates:
        if os.path.isfile(os.path.join(path, "XTQUANT_COMPAT_BRIDGE.py")):
            return path
    raise FileNotFoundError("QMT strategy templates are not installed")

__all__ = ["QmtClient", "configure", "get_template_dir"]
__version__ = "0.3.0"
