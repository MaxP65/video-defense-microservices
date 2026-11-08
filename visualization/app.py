from pathlib import Path

from fastapi import HTTPException, Request
from fastapi.responses import HTMLResponse, Response

from common import application, call


app = application("visualization")


@app.get("/", response_class=HTMLResponse)
def index():
    return Path("visualization/index.html").read_text("utf-8")


@app.api_route("/api/{path:path}", methods=["GET", "POST"])
async def proxy(path: str, request: Request):
    allowed = {"status", "collect", "videos", "batch", "models", "runs", "experiments"}
    if path.split("/")[0] not in allowed:
        raise HTTPException(404, "unknown scenario")
    content = await request.body()
    response = call(
        "master",
        request.method,
        "/" + path,
        content=content,
        params=request.query_params,
        headers={"content-type": "application/json"},
    )
    return Response(
        response.content,
        status_code=response.status_code,
        media_type="application/json",
    )
