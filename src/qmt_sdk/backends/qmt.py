"""QMT runtime backend using the shared file bridge."""

from .. import data


class QmtBackend:
    """Backend that exposes the unified request operations."""

    def call(self, method, *args, **kwargs):
        function = getattr(data, method)
        return function(*args, **kwargs)
