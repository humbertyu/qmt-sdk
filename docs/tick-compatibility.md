# Tick compatibility report

[English](tick-compatibility.md) | [简体中文](tick-compatibility.zh-CN.md)

This document records evidence for Tick compatibility separately from the public API
surface. A callable API or matching DataFrame shape does not by itself establish data
parity.

## Tested fixture

| Item | Value |
| --- | --- |
| Symbol | `000779.SZ` |
| Trading day | `2026-09-01` |
| Big QMT historical rows | 4,915 |
| Existing MiniQMT-derived DB6 rows | 4,915 |
| Common timestamps | 4,915 / 4,915 |
| First timestamp | `09:15:00.000` |
| Last timestamp | `15:30:00.001` |

The result includes valid trading records after 15:00. The compatibility layer does not
filter the 15:00–15:30 interval.

## Field results

| Field group | Result | Evidence / difference |
| --- | :---: | --- |
| `time` | ✅ | All 4,915 timestamps match exactly. |
| `lastPrice`, `open`, `high`, `low`, `lastClose` | ✅ | Values match; observed differences are floating-point representation only. |
| `volume` | ✅ | All values match exactly. |
| `askVol`, `bidVol` | ✅ | All values match exactly. |
| `askPrice`, `bidPrice` | ✅ | Numeric values match; serialized floating-point representations may differ. |
| `transactionNum`, `openInt` | ✅ | All values match exactly in the tested fixture. |
| `amount` | ⚠️ | 1,716 rows differ by a rounding amount; maximum absolute difference is 1 currency unit. |
| `stockStatus` | ⚠️ | Tested Big QMT historical payload returned `0`; DB6 contains trading-phase codes such as `2`, `3`, `5`, `8`, `12`, and `13`. |
| `pvolume` | ⚠️ | Tested Big QMT historical payload returned `0` for the meaningful trading rows; DB6 contains cumulative share-volume values. |
| `tickvol` | ⚠️ | The tested Big QMT historical payload did not provide this field. The compatibility DataFrame uses `0` only as a structural placeholder. |
| `pe` | ⚠️ | Not supplied by the tested Big QMT payload; the compatibility DataFrame uses `0.0` as a structural placeholder. |

## Usage decision

The tested bridge is suitable for timestamp reconciliation and consumers based on core
price, cumulative volume, order book, and transaction-count fields. Consumers that use
`stockStatus`, `pvolume`, `tickvol`, or `pe` must treat the compatibility result as not yet
data-equivalent to native MiniQMT.

`sync-tick-redis` can therefore be tested safely against a separate Redis database, but it
must not overwrite the trusted production dataset until downstream dependence on the
four documented fields has been audited.

## Reproduction tools

- `tools/capture_workflow_fixture.py`
- `tools/compare_workflow_fixtures.py`
- `tools/probe_subscription.py`

The repository does not depend on Redis. DB6 was used only as an external acceptance
oracle for this fixture.
