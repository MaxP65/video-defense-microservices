import argparse
import json
import time
import tomllib
from pathlib import Path

import httpx


parser = argparse.ArgumentParser()
parser.add_argument("--epochs", type=int, default=40)
parser.add_argument("--output", type=Path, default=Path("artifacts"))
args = parser.parse_args()
config = tomllib.loads(Path("config/docker.toml").read_text("utf-8"))
client = httpx.Client(
    base_url=f"http://127.0.0.1:{config['ports']['master']}", timeout=120
)


def request(method, path, **kwargs):
    response = client.request(method, path, **kwargs)
    response.raise_for_status()
    return response.json()


def training(kind, classifier_id=None):
    model = request("POST", "/models", json={"kind": kind})
    run = request(
        "POST",
        f"/models/{model['id']}/train",
        json={"epochs": args.epochs, "classifier_id": classifier_id},
    )
    deadline = time.monotonic() + 1800
    last_epoch = None
    while time.monotonic() < deadline:
        current = next(v for v in request("GET", "/runs") if v["id"] == run["id"])
        if current.get("epoch") != last_epoch:
            last_epoch = current.get("epoch")
            print(kind, "epoch", last_epoch, flush=True)
        if current["status"] in {"completed", "failed", "interrupted"}:
            args.output.mkdir(parents=True, exist_ok=True)
            (args.output / f"{kind}-run.json").write_text(
                json.dumps(current, indent=2), "utf-8"
            )
            if current["status"] != "completed":
                raise RuntimeError(current)
            print(kind, json.dumps(current["diagnostics"], indent=2), flush=True)
            return model["id"]
        time.sleep(2)
    raise TimeoutError("training exceeded 30 minutes")


if __name__ == "__main__":
    print(request("POST", "/collect"), flush=True)
    classifier_id = training("classifier")
    purifier_id = training("purifier", classifier_id)
    videos = request("GET", "/videos")
    video = next(v for v in videos if v["split"] == "val")
    result = request(
        "POST",
        "/experiments",
        json={
            "video_id": video["id"],
            "classifier_id": classifier_id,
            "purifier_id": purifier_id,
        },
    )
    result.pop("previews")
    (args.output / "demo.json").write_text(json.dumps(result, indent=2), "utf-8")
    print(json.dumps(result, indent=2))
