import time

from xtquant_compat import xtdata


def on_tick(data):
    print(data)


sequence = xtdata.subscribe_quote("000779.SZ", period="tick", callback=on_tick)
print("subscription:", sequence)
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    xtdata.unsubscribe_quote(sequence)
