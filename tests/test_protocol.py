from xtquant_compat.protocol import atomic_write_json, read_json


def test_atomic_json_round_trip(tmp_path):
    path = tmp_path / "nested" / "message.json"
    payload = {"text": "行情", "values": [1, 2, 3]}
    atomic_write_json(str(path), payload)
    assert read_json(str(path)) == payload
    assert not list(path.parent.glob("*.tmp"))
