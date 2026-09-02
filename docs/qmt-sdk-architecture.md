# qmt-sdk architecture

`qmt-sdk` has one transport bridge and two public API surfaces:

```text
new code:       qmt_sdk.QmtClient
legacy code:    xtquant_compat.xtdata
                         │
                         ▼
                  shared file bridge
                         │
                         ▼
                    QMT runtime
```

The bridge owns request/response files, serialization, status, cancellation,
and subscription events. Domain clients (`market`, `financial`, `instruments`,
and `jobs`) own public Python ergonomics. The compatibility surface owns only
MiniQMT signatures and return-shape normalization. New capabilities should be
added to a domain client first, then exposed through compatibility only when a
MiniQMT equivalent exists.

The package is intentionally a single distribution (`qmt-sdk`). The historical
`xtquant_compat` import remains as a migration module during the early release;
it is not a second transport or a second implementation.
