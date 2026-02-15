from __future__ import annotations

import os
import json
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from dotenv import load_dotenv
load_dotenv()

from app.storage.s3 import upload_file


def _utc_parts():
    now = datetime.now(timezone.utc)
    return now, f"{now:%Y/%m/%d}"


class RawEventSink:
    """
    Buffers events to a local JSONL file and periodically uploads to S3,
    then rotates to a new file. Safe and simple.
    """
    def __init__(
        self,
        enabled: bool,
        s3_prefix: str = "raw_events",
        flush_every: int = 500,
        local_dir: str = "tmp/raw_events",
    ):
        self.enabled = enabled
        self.s3_prefix = s3_prefix
        self.flush_every = max(1, int(flush_every))
        self.local_dir = Path(local_dir)
        self.local_dir.mkdir(parents=True, exist_ok=True)

        self._count = 0
        self._fp: Optional[Any] = None
        self._local_path: Optional[Path] = None
        
        if self.enabled:
            self._open_new_file()

    def _open_new_file(self):
        now, date_path = _utc_parts()
        stamp = now.strftime("%H%M%S")
        fname = f"events_{stamp}_{int(time.time())}.jsonl"
        self._local_path = self.local_dir / fname
        self._fp = open(self._local_path, "a", encoding="utf-8")

    def append(self, event: Dict[str, Any]):
        if not self.enabled:
            return

        assert self._fp is not None
        self._fp.write(json.dumps(event, ensure_ascii=False) + "\n")
        self._count += 1

        if self._count % self.flush_every == 0:
            self.flush_and_upload()

    def flush_and_upload(self):
        if not self.enabled:
            return
        if self._fp is None or self._local_path is None:
            return

        self._fp.flush()
        os.fsync(self._fp.fileno())
        self._fp.close()

        # Upload to S3 using date partitioning
        now, date_path = _utc_parts()
        s3_key = f"{self.s3_prefix}/{date_path}/{self._local_path.name}"
        uri = upload_file(str(self._local_path), s3_key, content_type="application/json")
        if uri:
            print(f"☁️ Uploaded raw events: {uri}")
            # Success - we can remove the local file if we want, 
            # but let's keep it for now as a local buffer or just move on.
            # Actually, usually we delete to save space.
            try:
                os.remove(self._local_path)
            except Exception as e:
                print(f"⚠️ Failed to remove local file {self._local_path}: {e}")
        else:
            print(f"❌ Failed to upload raw events to S3: {s3_key}")

        # Rotate
        self._count = 0
        self._open_new_file()

    def close(self):
        if not self.enabled:
            return
        if self._fp and not self._fp.closed:
            try:
                self.flush_and_upload()
            except Exception as e:
                print(f"⚠️ RawEventSink final upload failed: {e}")
