"""QMT runtime backend using the shared file bridge."""

from xtquant_compat import xtdata


class QmtBackend:
    """Backend that exposes the unified request operations."""

    def call(self, method, *args, **kwargs):
        function = getattr(xtdata, method)
        return function(*args, **kwargs)

