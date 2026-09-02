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

## Official QMT data-function baseline

The official QMT data-function page lists 42 query/data-function entries. They
are grouped below as the initial QMT-native scope; this list is independent of
the MiniQMT compatibility matrix.

| Group | Official functions |
| --- | --- |
| Market and subscriptions (22) | `download_history_data`, `ContextInfo.get_market_data_ex`, `ContextInfo.get_full_tick`, `ContextInfo.subscribe_quote`, `ContextInfo.subscribe_whole_quote`, `ContextInfo.unsubscribe_quote`, `subscribe_formula`, `unsubscribe_formula`, `call_formula`, `call_formula_batch`, `ContextInfo.get_svol`, `ContextInfo.get_bvol`, `ContextInfo.get_turnover_rate`, `ContextInfo.get_longhubang`, `ContextInfo.get_north_finance_change`, `ContextInfo.get_hkt_details`, `ContextInfo.get_hkt_statistics`, `get_etf_info`, `get_etf_iopv`, `ContextInfo.get_local_data`, `ContextInfo.get_history_data`, `ContextInfo.get_market_data` |
| Financial (4) | `ContextInfo.get_financial_data`, `ContextInfo.get_raw_financial_data`, `ContextInfo.get_last_volume`, `ContextInfo.get_total_share` |
| Instruments and contracts (7) | `ContextInfo.get_instrument_detail`, `get_st_status`, `ContextInfo.get_his_st_data`, `ContextInfo.get_main_contract`, `ContextInfo.get_contract_multiplier`, `ContextInfo.get_contract_expire_date`, `ContextInfo.get_his_contract_list` |
| Options (5) | `ContextInfo.get_option_detail_data`, `ContextInfo.get_option_list`, `ContextInfo.get_option_undl_data`, `ContextInfo.bsm_price`, `ContextInfo.bsm_iv` |
| Corporate actions and index (2) | `ContextInfo.get_divid_factors`, `ContextInfo.get_weight_in_index` |
| Constituents and calendar (2) | `ContextInfo.get_stock_list_in_sector`, `ContextInfo.get_trading_dates` |

The page also documents data dictionaries and field tables; those are schemas,
not additional callable APIs. Each function will first be exposed through
`QmtClient.query()` and then promoted to a typed domain method after runtime
verification.

## Integration rule

Every new QMT query starts as a bridge method available through:

```python
client.query("method_name", {"parameter": value})
```

After signature, return structure, error behavior, and performance are
validated, it becomes a typed method in the appropriate domain client. It is
added to `xtquant_compat` only if a MiniQMT equivalent exists. This prevents
QMT-only features from being distorted by compatibility requirements.

## Native query acceptance checklist

The bridge accepts documented QMT keyword names and positional arguments for
the official functions below. Runtime availability and whether a result is
non-empty still depend on QMT version, local data, permissions, and instrument.

| Function group | Dispatch | Acceptance notes |
| --- | --- | --- |
| Market, history, local data | ✅ | Native parameter order is mapped; `get_full_tick` is latest snapshot only. |
| Quote/formula subscriptions | ✅ | Subscribe/unsubscribe and file-delivered callbacks are implemented. |
| Scalar market queries (`get_svol`, `get_bvol`, turnover, ETF, northbound/HK) | ✅ | Scalar samples verified where data existed; turnover wrapper may require pandas. |
| Financial (`get_financial_data`, raw) | ✅ | Field-list/stock-list order preserved; raw/turnover official wrappers may require pandas. |
| Instruments, contracts, options | ✅ | Signatures mapped; values depend on the local universe and permissions. |
| Corporate actions, index weights, sectors, calendar | ✅ | Official parameter aliases mapped; empty results are runtime/data conditions. |
| Formula calculation (`bsm_price`, `bsm_iv`, formula calls) | ✅ | Calculation samples verified; formula APIs require configured formulas. |

For each acceptance run record QMT version, exact parameters, elapsed time,
result type, row/count information, and exception text. An empty result is not
treated as an implementation failure. New functions must be added to this map
and to the automated probe before being promoted to a typed domain method.
Some QMT bindings are unavailable during `init`; `get_trading_dates` should be
exercised after initialization in QMT's `after_init` phase. The bridge exposes
an `after_init` hook and performs a request scan there as well.

### Follow-up runtime verification (2026-09-02)

After deploying the updated bridge and restarting QMT, the remaining signature
checks all reached the native runtime successfully:

| Function | Elapsed | Result | Interpretation |
| --- | ---: | --- | --- |
| `get_his_contract_list` | 0.123 s | `list`, 0 rows | Call path is valid; the sample contract/date has no history in this QMT instance. |
| `get_history_data` | 0.063 s | `dict`, 0 keys | Call path is valid; the selected history index/date returned no rows. |
| `get_trading_dates` | 0.116 s | `list`, 0 rows | Call path is valid after initialization; this runtime returned no dates for the sample window. |

Additional 2026 validation with `stockcode="000001.SZ"`,
`start_date="20260101"`, `end_date="20260902"`, `count=-1` returned 162
trading dates. The earlier empty result was caused by the probe's narrow
window/parameter combination, not by an unavailable API.

### Effective-data follow-up

Using the current QMT strategy instance, `get_history_data(index=0/1, period in
{1d, 1m, tick}, 2026-01-01..2026-09-02)` returned an empty dictionary for all
variants. `get_his_contract_list` also returned an empty list for common sample
codes (`IF.CFFEX`, `IH.CFFEX`, `IC.CFFEX`, `rb.SHFE`). These calls are still
successful; the current strategy/data context does not expose matching history
for those samples. They should be rechecked with a strategy-bound historical
instrument or an account that has futures history loaded.

These results are recorded as “callable, empty runtime result”, not as
unsupported APIs. The raw probe report is
`.artifacts/qmt-native-probe-20260902-170533.json`.

### Typed market-client verification (2026-09-02)

After the bridge switched market queries to the lower-level QMT data binding,
both typed methods returned real daily data without importing pandas:

| Method | Parameters | Result | Elapsed |
| --- | --- | --- | ---: |
| `client.market.get_market_data_ex` | `000001.SZ`, `1d`, `count=2` | 1 symbol; columnar payload with `time/stime/open/high/low/close/volume/amount` | 0.118 s |
| `client.market.get_market_data` | same | Same native columnar structure | 0.167 s |

The same request through `client.qmt.get_market_data_ex` returned the same
structure in 0.055 s. These methods now bypass the pandas-dependent QMT wrapper
and preserve the native QMT columnar result.

### Subscription and download verification (2026-09-02)

| API | Test | Result | Elapsed |
| --- | --- | --- | ---: |
| `client.market.subscribe_quote` | `000001.SZ`, `tick`, 8-second listen | Subscription id `1`; 1 event received with `{symbol: [tick]}` shape | 0.110 s to subscribe |
| `client.market.unsubscribe_quote` | id `1` | Returned native `None`; subscription stopped | immediate |
| `client.market.subscribe_whole_quote` | `000001.SZ`, `600000.SH`, 8-second listen | Subscription id `2`; subscribe/unsubscribe path succeeded, no event during the post-market window | 0.115 s to subscribe |
| `client.market.download_history_data` | one symbol, `1d`, `20260902` | Completed with `{}` | 0.169 s |
| `client.market.download_history_data2` | one symbol, `1d`, `20260902` | Completed with `{}` | 0.168 s |

Formula calls and formula subscriptions remain callable through the typed
methods, but require a formula configured in the running QMT strategy; they are
not invoked with a fabricated formula name.

Financial download functions named `download_financial_data` and
`download_financial_data2` belong to the MiniQMT/`xtquant.xtdata` compatibility
surface, not to the official QMT data-function API. They are therefore not part
of the `qmt_sdk` native financial client. If legacy code needs them, use
`xtquant_compat.xtdata`, where their runtime availability is reported by the
compatibility bridge.

`subscribe_quote2` is not part of the QMT native interface documented in the
QMT Sheet/API pages. It remains a MiniQMT compatibility-only name and is not
exposed by `qmt_sdk.market`.
