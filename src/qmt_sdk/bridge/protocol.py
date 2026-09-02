import json
import os
import uuid

PROTOCOL_VERSION = 1


def atomic_write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temp = "%s.%s.tmp" % (path, uuid.uuid4().hex)
    with open(temp, "w", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, separators=(",", ":"))
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)


def read_json(path):
    with open(path, "r", encoding="utf-8") as stream:
        return json.load(stream)
