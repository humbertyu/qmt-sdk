# QMT capability map

This document tracks the query capabilities available from the QMT runtime,
independently of the MiniQMT compatibility matrix.

| Capability area | Examples | qmt_sdk layer | Status |
| --- | --- | --- | --- |
| Market data | `get_market_data`, `get_market_data_ex`, `get_full_tick`, local data | `client.market` | Core verified |
| Live subscriptions | quote/tick subscription, events, unsubscribe | `client.market` | Core verified |
| Instruments and metadata | instrument detail, sectors, type, markets, IPO/ETF info | `client.instruments` | Partly verified |
| Financial data | financial table read, raw financial payload | `client.financial` | Structure verified; values depend on data availability |
| Historical downloads | K-line/tick download and status | `client.market` / `client.jobs` | Existing bridge support |
| Calendar | trading dates, holidays, calendar | `client.instruments` | Environment-dependent |
| Derivatives and special data | options, contracts, index weights, L2 query | domain clients via `QmtClient.query` first | Not uniformly normalized |
| Formula and factor queries | formula result, factor data, ranking data | domain clients via `QmtClient.query` first | Extension stage |
| Task control | status, cancellation, bridge status | `client.jobs` | Core verified |

## Integration rule

Every new QMT query starts as a bridge method available through:

```python
client.query("method_name", {"parameter": value})
```

After signature, return structure, error behavior, and performance are
validated, it becomes a typed method in the appropriate domain client. It is
added to `xtquant_compat` only if a MiniQMT equivalent exists. This prevents
QMT-only features from being distorted by compatibility requirements.
