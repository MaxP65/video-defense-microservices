import hashlib
import json
from pathlib import Path

from fastapi import HTTPException, Query

from common import CONFIG, application, call, records, save


app = application("collector")


@app.post("/collect")
def collect():
    source = Path(CONFIG["collector"]["source"]).resolve()
    manifest = source / "manifest.json"
    if not manifest.exists():
        raise HTTPException(409, "prepare UCF101 first: python scripts/prepare_data.py")
    items = json.loads(manifest.read_text("utf-8"))
    existing = {v["sha256"] for v in records("videos")}
    added = 0
    for item in items:
        path = (source / item["path"]).resolve()
        if not path.is_relative_to(source) or not path.is_file():
            raise HTTPException(400, "invalid source path")
        content = path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        if digest in existing:
            continue
        uploaded = call("storage", "POST", "/files", content=content).json()
        save("videos", {**item, **uploaded, "sha256": digest})
        existing.add(digest)
        added += 1
    return {"added": added, "total": len(existing)}


@app.get("/batch")
def batch(
    split: str = "train",
    offset: int = Query(0, ge=0),
    limit: int = Query(8, ge=1, le=128),
):
    if split not in {"train", "val", "test"}:
        raise HTTPException(422, "split must be train, val or test")
    values = records("videos", split=split)
    return {
        "items": values[offset : offset + limit],
        "total": len(values),
        "offset": offset,
    }
