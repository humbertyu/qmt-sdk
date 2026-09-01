"""Print a Markdown API table from an installed official xtquant.xtdata module."""

import inspect

import xtquant.xtdata as xtdata


def main():
    print("| Official API and signature |")
    print("| --- |")
    for name, value in inspect.getmembers(xtdata, inspect.isfunction):
        if name.startswith("_"):
            continue
        try:
            signature = inspect.signature(value)
        except (TypeError, ValueError):
            signature = "(...)"
        print("| `%s%s` |" % (name, signature))


if __name__ == "__main__":
    main()
