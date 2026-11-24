"""Private subprocess entry point; receives only a validated check snapshot."""

import json
import sys
from dataclasses import asdict
from types import SimpleNamespace
from .probes import probe

if __name__ == "__main__":
    payload = json.load(sys.stdin)
    host = payload.pop("host")
    check = SimpleNamespace(node=SimpleNamespace(host=host), **payload)
    print(json.dumps(asdict(probe(check))))
