import json
import logging
import os
import time
import tomllib
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse


CONFIG = tomllib.loads(
    Path(os.getenv("VCR_CONFIG", "config/docker.toml")).read_text("utf-8")
)


def application(name):
    log_dir = Path(os.getenv("VCR_LOGS", "logs"))
    log_dir.mkdir(exist_ok=True, parents=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.FileHandler(log_dir / f"{name}.log", encoding="utf-8"))
    app = FastAPI(title=name)

    @app.middleware("http")
    async def log_request(request: Request, call_next):
        start = time.monotonic()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("request failed")
            response = JSONResponse(
                {"detail": "internal service error; see logs"}, status_code=500
            )
        logger.info(
            json.dumps(
                {
                    "method": request.method,
                    "path": request.url.path,
                    "status": response.status_code,
                    "seconds": time.monotonic() - start,
                }
            )
        )
        return response

    @app.get("/health")
    def health():
        return {"service": name, "status": "ok"}

    return app


def call(service, method, path, **kwargs):
    try:
        response = httpx.request(
            method, CONFIG["services"][service] + path, timeout=60, **kwargs
        )
    except httpx.RequestError as error:
        raise HTTPException(503, f"{service} unavailable") from error
    if response.is_error:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise HTTPException(response.status_code, detail)
    return response


def records(kind, **params):
    return call("storage", "GET", f"/records/{kind}", params=params).json()


def save(kind, body, item_id=None):
    path = f"/records/{kind}" + (f"/{item_id}" if item_id else "")
    return call("storage", "PUT" if item_id else "POST", path, json=body).json()
