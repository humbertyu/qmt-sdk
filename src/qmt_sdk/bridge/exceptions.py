class XtQuantCompatError(RuntimeError):
    """Base error raised by xtquant-compat."""


class BridgeTimeoutError(XtQuantCompatError, TimeoutError):
    """The QMT bridge did not respond before the configured timeout."""


class BridgeRemoteError(XtQuantCompatError):
    """The QMT bridge returned an exception."""


class BridgeCancelledError(XtQuantCompatError):
    """A long-running bridge request was cancelled."""


class BridgeUnavailableError(XtQuantCompatError):
    """The file bridge is not running or has restarted."""


class BridgeMethodNotSupportedError(BridgeRemoteError):
    """The active QMT build does not expose the requested method."""


class BridgePartialResultError(BridgeRemoteError):
    """A request returned only a partial result."""
