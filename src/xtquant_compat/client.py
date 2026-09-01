import os
import json
import threading
import time
import uuid

from .config import get_config
from .exceptions import BridgeRemoteError, BridgeTimeoutError
from .protocol import PROTOCOL_VERSION, atomic_write_json, read_json


class FileBridgeClient:
    def __init__(self, config):
        self.config = config
        self.client_id = "%s-%s" % (os.getpid(), uuid.uuid4().hex)
        self._callbacks = {}
        self._stop = threading.Event()
        self._event_thread = None
        for name in ("requests", "responses", "errors", "events", "processed", "cancellations"):
            os.makedirs(os.path.join(config.root, name), exist_ok=True)

    def request(self, method, params=None, timeout=None):
        request_id = uuid.uuid4().hex
        filename = "REQ_%s.json" % request_id
        payload = {
            "protocol_version": PROTOCOL_VERSION,
            "request_id": request_id,
            "client_id": self.client_id,
            "method": method,
            "params": params or {},
            "created_at": time.time(),
        }
        atomic_write_json(os.path.join(self.config.root, "requests", filename), payload)
        deadline = time.monotonic() + (self.config.timeout if timeout is None else float(timeout))
        while time.monotonic() < deadline:
            for folder in ("responses", "errors"):
                path = os.path.join(self.config.root, folder, filename)
                if not os.path.exists(path):
                    continue
                try:
                    result = read_json(path)
                except (OSError, ValueError, json.JSONDecodeError):
                    time.sleep(min(self.config.poll_interval, 0.05))
                    continue
                try:
                    os.remove(path)
                except OSError:
                    pass
                if folder == "errors" or not result.get("ok", False):
                    raise BridgeRemoteError(result.get("error") or "unknown QMT bridge error")
                return result.get("data")
            time.sleep(self.config.poll_interval)
        self.cancel(request_id)
        raise BridgeTimeoutError("timeout waiting for %s (%s)" % (method, request_id))

    def cancel(self, request_id):
        atomic_write_json(os.path.join(self.config.root, "cancellations", request_id + ".json"), {
            "request_id": request_id, "created_at": time.time(),
        })

    def subscribe_method(self, method, params, callback):
        result = self.request(method, params)
        subscription_id = result.get("subscription_id") if isinstance(result, dict) else result
        if callback is not None:
            self._callbacks[str(subscription_id)] = callback
            self._ensure_event_thread()
        return subscription_id

    def subscribe(self, stock_code, period, start_time, end_time, count, callback):
        return self.subscribe_method("subscribe_quote", {
            "stock_code": stock_code,
            "period": period,
            "start_time": start_time,
            "end_time": end_time,
            "count": count,
        }, callback)

    def unsubscribe(self, subscription_id):
        return self.unsubscribe_method("unsubscribe_quote", subscription_id)

    def unsubscribe_method(self, method, subscription_id, parameter="subscription_id"):
        self._callbacks.pop(str(subscription_id), None)
        return self.request(method, {parameter: subscription_id})

    def _ensure_event_thread(self):
        if self._event_thread and self._event_thread.is_alive():
            return
        self._stop.clear()
        self._event_thread = threading.Thread(target=self._event_loop, name="xtquant-compat-events", daemon=True)
        self._event_thread.start()

    def _event_loop(self):
        event_root = os.path.join(self.config.root, "events", self.client_id)
        processed_root = os.path.join(self.config.root, "processed", self.client_id)
        while not self._stop.wait(self.config.poll_interval):
            if not os.path.isdir(event_root):
                continue
            for subscription_id in sorted(os.listdir(event_root)):
                folder = os.path.join(event_root, subscription_id)
                if not os.path.isdir(folder):
                    continue
                callback = self._callbacks.get(subscription_id)
                if callback is None:
                    continue
                for name in sorted(n for n in os.listdir(folder) if n.endswith(".json")):
                    source = os.path.join(folder, name)
                    try:
                        event = read_json(source)
                        callback(event.get("data"))
                        destination = os.path.join(processed_root, subscription_id, name)
                        os.makedirs(os.path.dirname(destination), exist_ok=True)
                        os.replace(source, destination)
                    except FileNotFoundError:
                        continue
                    except Exception:
                        # Keep the event for at-least-once retry after callback failure.
                        time.sleep(self.config.poll_interval)
                        break

    def close(self):
        self._stop.set()
        if self._event_thread and self._event_thread.is_alive():
            self._event_thread.join(timeout=1)


_client = None
_client_lock = threading.Lock()


def get_client():
    global _client
    with _client_lock:
        if _client is None:
            _client = FileBridgeClient(get_config())
        return _client


def reset_client():
    global _client
    with _client_lock:
        if _client is not None:
            _client.close()
        _client = None
