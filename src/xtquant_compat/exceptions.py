"""Exception aliases retained for MiniQMT compatibility imports."""

from qmt_sdk.bridge.exceptions import (
    XtQuantCompatError, BridgeTimeoutError, BridgeRemoteError,
    BridgeCancelledError, BridgeUnavailableError,
    BridgeMethodNotSupportedError, BridgePartialResultError,
)

__all__ = [name for name in globals() if name.startswith("Bridge") or name == "XtQuantCompatError"]
