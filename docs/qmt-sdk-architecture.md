# qmt-sdk architecture

`qmt-sdk` has one transport bridge and two public API surfaces. The current
scope is query-only; trading operations are deliberately out of scope.

```text
new code:       qmt_sdk.QmtClient
legacy code:    xtquant_compat.xtdata
                         │
                         ▼
                   qmt_sdk core
                         │
                         ▼
                  shared file bridge
                         │
                         ▼
                    QMT runtime
```

The bridge owns request/response files, serialization, status, cancellation,
and subscription events. Query domain clients (`market`, `financial`,
`instruments`, and `jobs`) own public Python ergonomics. The compatibility surface owns only
MiniQMT signatures and return-shape normalization. New capabilities should be
added to a domain client first, then exposed through compatibility only when a
MiniQMT equivalent exists.

The package is intentionally a single distribution (`qmt-sdk`). The historical
`xtquant_compat` import is a migration facade over `qmt_sdk`; the dependency
direction never goes from the core SDK back to the compatibility namespace.

## Current scope

Supported focus:

- market and historical data queries;
- tick subscriptions and event delivery;
- financial data download/read workflows;
- instrument, sector, calendar, and metadata queries;
- request status, timeout, cancellation, and recovery.

Order submission, cancellation, account operations, and position mutation are
not part of the current SDK roadmap. They may be considered as a separate
design later, without changing the query bridge contract.
