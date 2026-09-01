# xtquant-compat

`xtquant-compat` exposes a focused subset of the MiniQMT `xtquant.xtdata` API through a
pure file bridge running inside Big QMT. It is designed for QMT Python runtimes that do
not provide `_socket`, `_ctypes`, pandas, Redis, ZeroMQ, or third-party packages.

Status: experimental `0.1.0`. Use it beside an existing MiniQMT deployment until the
output has been validated against your production feed.

## Why file IPC?

- The QMT strategy uses only its bundled standard library and `ContextInfo`.
- Requests, responses, and subscription events are atomically written and inspectable.
- Subscription events remain on disk until an external callback handles them.
- No QMT DLLs, proprietary Python packages, or vendor source code are distributed.

The trade-off is latency and filesystem load. This transport targets ordinary quote
workloads, recovery, and portability rather than order-book or transaction-level HFT.

## Supported API

| API | Status |
| --- | --- |
| `get_full_tick` | Tested against Big QMT |
| `get_market_data_ex` | Implemented through raw `get_market_data2` |
| `get_market_data` | Field-keyed DataFrame compatibility implemented |
| `subscribe_quote` / `unsubscribe_quote` | Tested against Big QMT |
| `get_instrument_detail` | Tested against Big QMT |
| `get_stock_list_in_sector` | Implemented for sector universes |
| `download_history_data(2)` | Experimental; depends on QMT `down_history_data` |
| `bridge_status` | Extension API |

Unsupported APIs will not be silently emulated. Compatibility details belong in
[`docs/compatibility.md`](docs/compatibility.md).

## Install the external client

Use an external Python 3.8+ environment. Do not install this package into QMT's bundled
Python runtime.

```powershell
cd D:\Projects\xtquant-compat
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

## Deploy the QMT strategy

1. Copy `qmt_strategy/XTQUANT_COMPAT_BRIDGE.py` to:

   ```text
   D:\FinTools\QMT\python\XTQUANT_COMPAT_BRIDGE.py
   ```

2. In Big QMT create a strategy named exactly:

   ```text
   XTQUANT_COMPAT_BRIDGE_LAUNCHER
   ```

3. Paste the contents of `qmt_strategy/XTQUANT_COMPAT_BRIDGE_LAUNCHER.py` into it.
4. Start the strategy and confirm:

   ```text
   [xtquant_compat] started root=D:\FinTools\QMT\xtquant_compat_bridge
   ```

The bridge deliberately uses a new root and does not touch the earlier
`D:\FinTools\QMT\file_bridge` experiment.

## External use

Only the import changes:

```python
from xtquant_compat import xtdata

print(xtdata.bridge_status())
print(xtdata.get_full_tick(["000779.SZ"]))

seq = xtdata.subscribe_quote(
    "000779.SZ",
    period="tick",
    callback=lambda data: print(data),
)
```

The callback is normalized to the common MiniQMT shape:

```python
{"000779.SZ": [{"time": 1788241293000, "lastPrice": 9.98, "volume": 640940}]}
```

Configuration is explicit when the default root is not suitable:

```python
from xtquant_compat import configure

configure(root=r"D:\FinTools\QMT\xtquant_compat_bridge", timeout=30)
```

## Reliability model

- Request and response filenames contain a UUID.
- Writers use a temporary file followed by an atomic rename.
- Quote events are delivered at least once.
- A callback failure leaves its event file pending for retry.
- Consumers must treat `symbol + time` as idempotent for the current three-second feed.
- Historical Tick reconciliation remains an application-level recovery mechanism.

See [`docs/protocol.md`](docs/protocol.md) for the wire protocol.

## License and trademark notice

Apache-2.0. QMT, MiniQMT, and xtquant are names of their respective owners. This is an
independent compatibility project and does not bundle their proprietary components.
