"""Subscribe to one Big QMT tick stream and print callback shape/timing."""

import argparse
import threading
import time

from xtquant_compat import xtdata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stock", default="000779.SZ")
    parser.add_argument("--seconds", type=float, default=15.0)
    args = parser.parse_args()
    received = []
    ready = threading.Event()

    def on_quote(data):
        now = time.time()
        received.append(now)
        ticks = data.get(args.stock, []) if isinstance(data, dict) else []
        tick = ticks[-1] if ticks else None
        print("callback=%d data=%r" % (len(received), tick), flush=True)
        ready.set()

    sequence = xtdata.subscribe_quote(
        args.stock, period="tick", start_time="", end_time="", count=0,
        callback=on_quote,
    )
    print("subscribed stock=%s sequence=%s" % (args.stock, sequence), flush=True)
    deadline = time.time() + args.seconds
    try:
        while time.time() < deadline:
            ready.wait(min(0.5, max(0.0, deadline - time.time())))
            ready.clear()
    finally:
        result = xtdata.unsubscribe_quote(sequence)
        intervals = [right - left for left, right in zip(received, received[1:])]
        print(
            "unsubscribed=%r callbacks=%d intervals=%r"
            % (result, len(received), [round(item, 3) for item in intervals]),
            flush=True,
        )


if __name__ == "__main__":
    main()
