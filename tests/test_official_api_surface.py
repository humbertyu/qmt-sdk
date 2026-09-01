import inspect

from xtquant_compat import xtdata


def test_all_official_xtdata_functions_have_public_entries_and_signatures():
    spec = xtdata.OFFICIAL_API_SPEC
    assert spec["function_count"] == 138
    missing = []
    mismatches = []
    for item in spec["functions"]:
        function = getattr(xtdata, item["name"], None)
        if not callable(function):
            missing.append(item["name"])
            continue
        actual = str(inspect.signature(function))
        if actual != item["signature"]:
            mismatches.append((item["name"], item["signature"], actual))
    assert missing == []
    assert mismatches == []
