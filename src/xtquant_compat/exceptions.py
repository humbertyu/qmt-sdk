class XtQuantCompatError(RuntimeError):
    """Base error raised by xtquant-compat."""


class BridgeTimeoutError(XtQuantCompatError, TimeoutError):
    """The QMT bridge did not respond before the configured timeout."""


class BridgeRemoteError(XtQuantCompatError):
    """The QMT bridge returned an exception."""
