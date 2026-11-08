import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import Body, HTTPException, Request
from fastapi.responses import FileResponse

from common import CONFIG, application


app = application("storage")
root = Path(CONFIG["storage"]["root"])
root.mkdir(parents=True, exist_ok=True)


@contextmanager
def connection():
    db = sqlite3.connect(root / "metadata.sqlite", timeout=30)
    try:
        db.execute(
            "CREATE TABLE IF NOT EXISTS records (id TEXT PRIMARY KEY, kind TEXT, body TEXT)"
        )
        with db:
            yield db
    finally:
        db.close()


def valid_kind(kind):
    if kind not in {"videos", "models", "runs"}:
        raise HTTPException(404, "unknown collection")


@app.get("/records/{kind}")
def listing(kind: str, split: str | None = None):
    valid_kind(kind)
    with connection() as db:
        rows = db.execute(
            "SELECT body FROM records WHERE kind=? ORDER BY rowid", (kind,)
        ).fetchall()
    values = [json.loads(row[0]) for row in rows]
    return [v for v in values if split is None or v.get("split") == split]


@app.get("/records/{kind}/{item_id}")
def get(kind: str, item_id: str):
    valid_kind(kind)
    with connection() as db:
        row = db.execute(
            "SELECT body FROM records WHERE kind=? AND id=?", (kind, item_id)
        ).fetchone()
    if row is None:
        raise HTTPException(404, "record not found")
    return json.loads(row[0])


@app.post("/records/{kind}", status_code=201)
def create(kind: str, body: dict = Body(...)):
    valid_kind(kind)
    value = {**body, "id": uuid4().hex}
    with connection() as db:
        db.execute(
            "INSERT INTO records VALUES (?,?,?)", (value["id"], kind, json.dumps(value))
        )
    return value


@app.put("/records/{kind}/{item_id}")
def update(kind: str, item_id: str, body: dict = Body(...)):
    get(kind, item_id)
    value = {**body, "id": item_id}
    with connection() as db:
        db.execute(
            "UPDATE records SET body=? WHERE id=? AND kind=?",
            (json.dumps(value), item_id, kind),
        )
    return value


@app.delete("/records/{kind}/{item_id}", status_code=204)
def delete(kind: str, item_id: str):
    get(kind, item_id)
    with connection() as db:
        db.execute("DELETE FROM records WHERE id=? AND kind=?", (item_id, kind))


@app.post("/files", status_code=201)
async def upload(request: Request):
    content = await request.body()
    if not content or len(content) > CONFIG["storage"]["max_file_mb"] * 1024**2:
        raise HTTPException(413, "file is empty or too large")
    file_id = uuid4().hex
    (root / file_id).write_bytes(content)
    return {"file_id": file_id}


@app.get("/files/{file_id}")
def download(file_id: str):
    if len(file_id) != 32 or any(c not in "0123456789abcdef" for c in file_id):
        raise HTTPException(404, "file not found")
    path = root / file_id
    if not path.is_file():
        raise HTTPException(404, "file not found")
    return FileResponse(path)
