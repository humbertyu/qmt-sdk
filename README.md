# qmt-sdk

[English](README.md) | [简体中文](README.zh-CN.md)

`qmt-sdk` exposes a unified QMT API and MiniQMT-compatible `xtquant.xtdata` surface through a
pure file bridge running inside QMT. It is designed for QMT Python runtimes that do
not provide `_socket`, `_ctypes`, pandas, Redis, ZeroMQ, or third-party packages.

Status: experimental `0.2.0`. Use it beside an existing MiniQMT deployment until the
output has been validated against your production feed.

## Why file IPC?

- The QMT strategy uses only its bundled standard library and `ContextInfo`.
- Requests, responses, and subscription events are atomically written and inspectable.
- Subscription events remain on disk until an external callback handles them.
- No QMT DLLs, proprietary Python packages, or vendor source code are distributed.

The trade-off is latency and filesystem load. This transport targets ordinary quote
workloads, recovery, and portability rather than order-book or transaction-level HFT.

## API implementation and compatibility

README intentionally does not duplicate per-API claims. The single
[API compatibility document](docs/xtdata-api-matrix.md) contains all 138 official APIs,
workflow mappings, return-shape checks, field-level differences, numeric tolerances,
known limitations, and retained reproduction tools.
The step-by-step checklist for adding another API is in the
[API implementation standard](docs/api-implementation-standard.md).

Unsupported or unverified APIs are marked explicitly and are not silently claimed as
compatible.

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
