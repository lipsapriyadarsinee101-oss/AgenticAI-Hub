"""Local JSONL stage events and optional metadata-only Langfuse spans."""

import json
import time
from contextlib import contextmanager, nullcontext
from datetime import datetime, timezone
from pathlib import Path


class Recorder:
    def __init__(self, path: Path, trace: bool = False):
        self.path = path
        self.client = None
        if trace:
            import os
            if not all(os.getenv(k) for k in ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY")):
                raise ValueError("--trace requires LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY")
            from langfuse import get_client
            self.client = get_client()

    @contextmanager
    def stage(self, name: str):
        start = time.monotonic()
        status = "ok"
        span = self.client.start_as_current_observation(name=name, as_type="span") if self.client else nullcontext()
        try:
            with span:
                yield
        except BaseException:
            status = "error"
            raise
        finally:
            event = {"time": datetime.now(timezone.utc).isoformat(), "stage": name,
                     "status": status, "elapsed_seconds": round(time.monotonic() - start, 3)}
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event) + "\n")

    def close(self):
        if self.client:
            self.client.flush()
