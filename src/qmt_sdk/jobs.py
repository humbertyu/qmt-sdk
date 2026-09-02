class JobClient:
    def __init__(self, backend):
        self._backend = backend

    def status(self, request_id):
        return self._backend.call("get_request_status", request_id)

    def cancel(self, request_id):
        return self._backend.call("cancel_request", request_id)

    def bridge_status(self):
        return self._backend.call("bridge_status")
