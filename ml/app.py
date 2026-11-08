import time
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import Literal

import torch
from fastapi import HTTPException
from pydantic import BaseModel, Field
from torch import nn

from common import CONFIG, application, call, records, save
from ml.models import fgsm
from ml.training import load_model, metrics, train
from ml.video import dataset, preview


app = application("ml")
executor = ThreadPoolExecutor(max_workers=1)
submission_lock = Lock()


@app.on_event("startup")
def recover_jobs():
    for run in records("runs"):
        if run["status"] in {"queued", "running"}:
            save(
                "runs",
                {**run, "status": "interrupted", "error": "ML service restarted"},
                run["id"],
            )
            model = call("storage", "GET", "/records/models/" + run["model_id"]).json()
            save("models", {**model, "status": "failed"}, model["id"])


class ModelRequest(BaseModel):
    kind: Literal["classifier", "purifier"]


class TrainRequest(BaseModel):
    epochs: int = Field(default=CONFIG["ml"]["epochs"], ge=1, le=200)
    classifier_id: str | None = None


class ExperimentRequest(BaseModel):
    video_id: str
    classifier_id: str
    purifier_id: str
    epsilon: float = Field(default=CONFIG["ml"]["epsilon"], ge=0, le=0.1)
    adaptive: bool = False


def get_model(model_id, kind):
    value = call("storage", "GET", "/records/models/" + model_id).json()
    if value["kind"] != kind or value["status"] != "trained":
        raise HTTPException(409, f"a trained {kind} is required")
    return value


@app.get("/models")
def models():
    return records("models")


@app.post("/models", status_code=201)
def create_model(body: ModelRequest):
    return save(
        "models",
        {"kind": body.kind, "status": "created", "classes": CONFIG["ml"]["classes"]},
    )


@app.get("/models/{model_id}")
def summary(model_id: str):
    return call("storage", "GET", "/records/models/" + model_id).json()


@app.post("/models/{model_id}/train", status_code=202)
def start_training(model_id: str, body: TrainRequest):
    with submission_lock:
        return submit_training(model_id, body)


def submit_training(model_id, body):
    model = summary(model_id)
    if model["status"] != "created":
        raise HTTPException(409, "create a new model version before training")
    classifier = None
    if model["kind"] == "purifier":
        if not body.classifier_id:
            raise HTTPException(422, "classifier_id is required")
        classifier = get_model(body.classifier_id, "classifier")
    if any(v.get("status") in {"queued", "running"} for v in records("runs")):
        raise HTTPException(409, "another task is running; wait for completion")
    run = save(
        "runs",
        {
            "type": "training",
            "model_id": model_id,
            "status": "queued",
            "parameters": {"epochs": body.epochs},
        },
    )
    save("models", {**model, "status": "training"}, model_id)
    executor.submit(train, run, model, classifier)
    return run


@app.get("/runs")
def runs():
    return records("runs")


@app.post("/experiments")
def experiment(body: ExperimentRequest):
    started = time.monotonic()
    classifier_record = get_model(body.classifier_id, "classifier")
    purifier_record = get_model(body.purifier_id, "purifier")
    if purifier_record["classifier_id"] != body.classifier_id:
        raise HTTPException(409, "purifier was trained for a different classifier")
    video = call("storage", "GET", "/records/videos/" + body.video_id).json()
    admitted = purifier_record["diagnostics"]["decision"] == "passed"
    if not admitted and (body.adaptive or video["split"] == "test"):
        raise HTTPException(
            409, "diagnostics inconclusive; use val for the technical demonstration"
        )
    if any(v["status"] in {"queued", "running"} for v in records("runs")):
        raise HTTPException(409, "wait until training completes")
    device = "cpu"
    torch.set_num_threads(CONFIG["ml"]["threads"])
    classifier = load_model(classifier_record, device).eval().requires_grad_(False)
    purifier = load_model(purifier_record, device).eval().requires_grad_(False)
    x, y = dataset([video], device)
    pipeline = nn.Sequential(purifier, classifier)
    attacked = fgsm(pipeline if body.adaptive else classifier, x, y, body.epsilon)
    with torch.no_grad():
        cleaned = purifier(attacked)
        clean_cleaned = purifier(x)

    def prediction(pixels):
        with torch.no_grad():
            probabilities = classifier(pixels).softmax(1)[0]
        return {
            "class": CONFIG["ml"]["classes"][int(probabilities.argmax())],
            "confidence": float(probabilities.max()),
            "correct": bool(int(probabilities.argmax()) == int(y[0])),
        }

    result = {
        "type": "experiment",
        "status": "completed",
        **body.model_dump(),
        "split": video["split"],
        "true_class": video["class"],
        "n": 1,
        "protocol": "adaptive FGSM"
        if body.adaptive
        else "classifier-only FGSM; technical demo",
        "admission": purifier_record["diagnostics"]["decision"],
        "clean": prediction(x),
        "attacked": prediction(attacked),
        "purified": prediction(cleaned),
        "clean_purified": prediction(clean_cleaned),
        "attacked_quality": metrics(classifier, attacked, y, reference=x),
        "purified_quality": metrics(classifier, cleaned, y, reference=x),
        "linf": float((attacked - x).abs().max()),
        "iterations": 1,
        "eot": 1,
        "voting": 1,
        "seconds": time.monotonic() - started,
        "classifier_weights_sha256": classifier_record["weights_sha256"],
        "purifier_weights_sha256": purifier_record["weights_sha256"],
    }
    if body.adaptive:
        result["attack_success"] = (
            result["clean_purified"]["correct"] and not result["purified"]["correct"]
        )
        result["restored"] = None
    else:
        result["attack_success"] = (
            result["clean"]["correct"] and not result["attacked"]["correct"]
        )
        result["restored"] = result["attack_success"] and result["purified"]["correct"]
    saved = save("runs", result)
    return {
        **saved,
        "previews": {
            "clean": preview(x[0]),
            "attacked": preview(attacked[0]),
            "purified": preview(cleaned[0]),
        },
    }
