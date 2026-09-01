# xtquant-compat

[English](README.md) | [简体中文](README.zh-CN.md)

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

## API compatibility status

The compatibility target is derived from the public functions exposed by an installed official
`xtquant.xtdata`, rather than an invented project-specific API. The current reference is official
distribution `250516.1.1` / module `xtquant_250516`, containing 138 public functions. All 138
have matching public names and signatures; behavioral verification is tracked separately.

| Status | Count |
| --- | ---: |
| Public API surface | 138 / 138 |
| Behavior verified | 8 |
| Adapter implemented, verification pending | 116 |
| Different MiniQMT-local semantics | 14 |

See the complete table of official names, signatures, status, and known differences in
[`docs/xtdata-api-matrix.md`](docs/xtdata-api-matrix.md).

### Implemented core API

Legend: ✅ verified; ⚠️ usable with a documented difference; ⏳ pending.

| API | Current workflow | Big QMT call | Native structure | Native data | Notes |
| --- | --- | :---: | :---: | :---: | --- |
| `get_stock_list_in_sector` | `update-instruments`, `sync-auto` | ✅ | ✅ | ⚠️ | Big QMT contained all MiniQMT symbols plus 10 newer symbols. |
| `get_instrument_detail` | `update-instruments` | ✅ | ✅ | ✅ | Required fields, aliases, defaults, and date strings verified. |
| `get_market_data` (`1d`) | `update-instruments` | ✅ | ✅ | ✅ | Stock-by-timetag matrix and one-day values verified. |
| `download_history_data2` (`1d`) | `sync-auto` | ✅ | ✅ | ✅ | Two-stock download and completion callback verified. |
| `get_market_data_ex` (`1d`) | `sync-auto` | ✅ | ✅ | ✅ | Fields, index, dtypes, and one-day values verified. |
| `download_history_data2` (`1m`) | `sync-auto` | ✅ | ✅ | ✅ | Two-stock download and completion callback verified. |
| `get_market_data_ex` (`1m`) | `sync-auto` | ✅ | ✅ | ✅ | 241 bars; fields, index, dtypes, and values verified. |
| `subscribe_quote` (`tick`) | `subscribe-tick` | ✅ | ✅ | ✅ | Native callback shape and quote timestamps verified. |
| `unsubscribe_quote` | `subscribe-tick` | ✅ | ✅ | ✅ | Real Big QMT unsubscribe verified. |
| `download_history_data2` (`tick`) | `sync-auto`, `sync-tick-redis` | ✅ | ✅ | ✅ | Two-stock download verified, including data after 15:00. |
| `get_market_data_ex` (`tick`) | `sync-auto`, `sync-tick-redis` | ✅ | ✅ | ⚠️ | All 4,915 timestamps and core fields match; see field differences below. |
| `get_full_tick` | Snapshot/polling | ✅ | ✅ | ✅ | Current three-second quote snapshot verified. |
| `bridge_status` | Diagnostics | ✅ | N/A | N/A | Project extension API. |

The retained acceptance tools are `tools/capture_workflow_fixture.py`,
`tools/compare_workflow_fixtures.py`, and `tools/probe_subscription.py`.

For the tested `000779.SZ` trading day, Big QMT and the existing MiniQMT-derived
store had all 4,915 tick timestamps in common, including `15:30:00.001`. Prices,
volume, order-book volume, and transaction count matched (apart from floating-point
representation); `amount` differed by at most one currency unit. Historical Big QMT
payloads did not reproduce native `stockStatus`, `pvolume`, or `tickvol` exactly.
These remain documented deviations: missing structural fields use neutral placeholders
and must not be treated as data-equivalent to native values.

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
