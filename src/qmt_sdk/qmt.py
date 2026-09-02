"""QMT-native query namespace."""


class QmtQueryClient:
    def __init__(self, client):
        self._client = client

    def __getattr__(self, method):
        if method.startswith("_"):
            raise AttributeError(method)

        def call(*args, **params):
            # Positional arguments are preserved for callers porting code
            # directly from a QMT strategy.  Keyword arguments remain the
            # preferred form because they are self-documenting across the
            # file bridge boundary.
            if args:
                if params:
                    raise TypeError("%s accepts positional or keyword arguments, not both" % method)
                return self._client.query(method, {"_args": list(args)})
            return self._client.query(method, params)

        call.__name__ = method
        return call
