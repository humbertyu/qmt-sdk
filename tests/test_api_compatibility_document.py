import json
from pathlib import Path


ROOT = Path(__file__).parents[1]
MATRIX = ROOT / "docs" / "xtdata-api-matrix.md"


def test_single_api_document_contains_every_official_function_and_markers():
    document = MATRIX.read_text(encoding="utf-8")
    specification = json.loads(
        (ROOT / "src" / "xtquant_compat" / "official_xtdata_api.json").read_text(
            encoding="utf-8",
        ),
    )
    assert document.count("<!-- GENERATED_API_MATRIX_START -->") == 1
    assert document.count("<!-- GENERATED_API_MATRIX_END -->") == 1
    for function in specification["functions"]:
        assert "| `%s%s` |" % (function["name"], function["signature"]) in document

    generated = document.split("<!-- GENERATED_API_MATRIX_START -->", 1)[1].split(
        "<!-- GENERATED_API_MATRIX_END -->", 1,
    )[0]
    rows = [line for line in generated.splitlines() if line.startswith("| `")]
    counts = {
        "✅": sum("| ✅ |" in row for row in rows),
        "⚠️": sum("| ⚠️ |" in row for row in rows),
        "🧪": sum("| 🧪 |" in row for row in rows),
        "➖": sum("| ➖ |" in row for row in rows),
    }
    assert counts == {"✅": 1, "⚠️": 8, "🧪": 115, "➖": 14}
    assert sum(counts.values()) == specification["function_count"] == 138


def test_readmes_link_to_single_api_document_without_tick_detail_duplication():
    for name in ("README.md", "README.zh-CN.md"):
        readme = (ROOT / name).read_text(encoding="utf-8")
        assert "docs/xtdata-api-matrix.md" in readme
        assert "tick-compatibility" not in readme
        assert "stockStatus" not in readme
