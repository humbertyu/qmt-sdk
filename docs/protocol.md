# File protocol v1

Default root: the path configured by `XTQUANT_COMPAT_ROOT` (otherwise the bridge's
platform default). Deployments should choose a dedicated directory outside production data.

```text
requests/                      external -> QMT requests
processing/                    requests claimed by QMT
responses/                     successful QMT responses
errors/                        failed QMT responses
events/<client>/<sub>/         durable quote callbacks
processed/<client>/<sub>/      callbacks acknowledged by the client
```

All visible messages are complete UTF-8 JSON files. A producer writes a unique `.tmp`
file in the destination directory and atomically renames it to `.json`.

Requests carry `protocol_version`, `request_id`, `client_id`, `method`, `params`, and
`created_at`. Responses reuse the request filename. Subscription event filenames are
zero-padded monotonically increasing sequence numbers scoped to a subscription.

Event delivery is at least once. The client moves an event into `processed` only after
the user callback returns successfully. Applications should still deduplicate by the
market event identity because a crash can occur after callback side effects but before
the acknowledgement move.

Version 1 is local-machine only. The protocol does not authenticate clients and the
bridge root must not be exposed through an untrusted network share.
