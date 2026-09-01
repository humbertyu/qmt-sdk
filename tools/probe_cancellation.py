"""Run a cooperative cancellation probe against the live file bridge."""
import os
import threading
import time

from xtquant_compat import xtdata
from xtquant_compat.exceptions import BridgeCancelledError


client = xtdata.get_client()
stocks = ["%06d.SZ" % i for i in range(1, 5220)]
result = {}


def worker():
    try:
        result["value"] = client.request(
            "get_instrument_detail_list", {"stock_list": stocks}, timeout=120,
        )
    except Exception as exc:  # report the concrete bridge behavior
        result["error"] = exc


thread = threading.Thread(target=worker)
thread.start()
request_id = None
for _ in range(100):
    status_dir = os.path.join(client.config.root, "status")
    candidates = []
    for name in os.listdir(status_dir):
        if not name.endswith(".json"):
            continue
        path = os.path.join(status_dir, name)
        try:
            status = xtdata.get_request_status(name[:-5])
        except Exception:
            continue
        if status and status.get("state") in ("pending", "running"):
            candidates.append(status)
    if candidates:
        request_id = max(candidates, key=lambda item: item.get("updated_at", 0))["request_id"]
        if any(item.get("state") == "running" for item in candidates):
            break
    time.sleep(0.05)

if request_id:
    print("request_id", request_id)
    print("before_cancel", xtdata.get_request_status(request_id))
    xtdata.cancel_request(request_id)
else:
    print("request_id not found")

thread.join(30)
print("alive", thread.is_alive())
print("error_type", type(result.get("error")).__name__ if result.get("error") else None)
print("error", repr(result.get("error")))
if request_id:
    print("after_cancel", xtdata.get_request_status(request_id))
processing = os.path.join(client.config.root, "processing")
print("processing_files", len(os.listdir(processing)))
