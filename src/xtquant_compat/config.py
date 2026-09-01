import os
import threading
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Config:
    root: str = os.environ.get("XTQUANT_COMPAT_ROOT", r"D:\FinTools\QMT\file_bridge")
    timeout: float = float(os.environ.get("XTQUANT_COMPAT_TIMEOUT", "30"))
    poll_interval: float = float(os.environ.get("XTQUANT_COMPAT_POLL_INTERVAL", "0.05"))


_lock = threading.Lock()
_config = Config()


def configure(root=None, timeout=None, poll_interval=None):
    """Configure the global file transport and reset the active client."""
    global _config
    changes = {}
    if root is not None:
        changes["root"] = os.path.abspath(os.fspath(root))
    if timeout is not None:
        changes["timeout"] = float(timeout)
    if poll_interval is not None:
        changes["poll_interval"] = float(poll_interval)
    with _lock:
        _config = replace(_config, **changes)
    from .client import reset_client
    reset_client()
    return _config


def get_config():
    with _lock:
        return _config
