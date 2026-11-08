import hashlib
import io
import math
import time
from pathlib import Path

import torch
from torch.nn import functional as F

from common import CONFIG, call, records, save
from ml.models import Classifier, Purifier, fgsm
from ml.video import dataset


def fingerprint():
    digest = hashlib.sha256()
    for path in sorted(Path(".").glob("**/*.py")):
        if not any(part.startswith(".") for part in path.parts):
            digest.update(str(path).encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def load_model(record, device):
    model = (
        Classifier(len(CONFIG["ml"]["classes"]))
        if record["kind"] == "classifier"
        else Purifier()
    )
    if record.get("weights_file"):
        content = call("storage", "GET", "/files/" + record["weights_file"]).content
        if hashlib.sha256(content).hexdigest() != record["weights_sha256"]:
            raise ValueError("checkpoint checksum mismatch")
        model.load_state_dict(
            torch.load(io.BytesIO(content), map_location="cpu", weights_only=True)
        )
    return model.to(device)


def metrics(classifier, x, y, purifier=None, reference=None):
    with torch.no_grad():
        output = purifier(x) if purifier is not None else x
        result = {
            "correct": int((classifier(output).argmax(1) == y).sum()),
            "n": len(y),
        }
        result["accuracy"] = result["correct"] / result["n"]
        if reference is not None:
            mse = float(F.mse_loss(output, reference))
            result.update(
                mse=mse,
                psnr_db=-10 * math.log10(max(mse, 1e-12)),
                motion_error=float(
                    F.mse_loss(
                        output[:, :, 1:] - output[:, :, :-1],
                        reference[:, :, 1:] - reference[:, :, :-1],
                    )
                ),
            )
        return result


def train(run, model_record, classifier_record=None):
    started = time.monotonic()
    model_id = model_record["id"]
    try:
        settings = {**CONFIG["ml"], **run["parameters"]}
        torch.manual_seed(settings["seed"])
        torch.set_num_threads(settings["threads"])
        device = (
            "cuda"
            if settings["device"] == "auto" and torch.cuda.is_available()
            else settings["device"]
        )
        if device == "auto":
            device = "cpu"
        model = load_model(model_record, device)
        items = {split: records("videos", split=split) for split in ("train", "val")}
        if any(not values for values in items.values()):
            raise ValueError("collect nonempty train and val splits first")
        groups = [{v["group"] for v in values} for values in items.values()]
        hashes = [{v["sha256"] for v in values} for values in items.values()]
        if groups[0] & groups[1] or hashes[0] & hashes[1]:
            raise ValueError("train/val leakage")
        expected = set(range(len(settings["classes"])))
        if any({v["label"] for v in values} != expected for values in items.values()):
            raise ValueError("each split must contain all classes")
        run.update(
            status="running",
            code_sha256=fingerprint(),
            device=device,
            config=settings,
            splits=items,
            attack={
                "method": "untargeted FGSM",
                "epsilon": settings["epsilon"],
                "iterations": 1,
                "eot": 1,
                "voting": 1,
            },
            protocol="training diagnostics; validation only; not a robustness evaluation",
        )
        save("runs", run, run["id"])
        train_x, train_y = dataset(items["train"], device)
        val_x, val_y = dataset(items["val"], device)
        target_x = train_x
        val_target = val_x
        classifier = None
        if classifier_record:
            classifier = (
                load_model(classifier_record, device).eval().requires_grad_(False)
            )
            train_x = fgsm(classifier, train_x, train_y, settings["epsilon"])
            val_x = fgsm(classifier, val_x, val_y, settings["epsilon"])
            run["classifier_id"] = classifier_record["id"]
            run["classifier_weights_sha256"] = classifier_record["weights_sha256"]
        optimizer = torch.optim.Adam(model.parameters(), lr=settings["learning_rate"])

        def loss_on(x, y, target):
            return (
                F.mse_loss(model(x), target)
                if classifier
                else F.cross_entropy(model(x), y)
            )

        model.eval()
        with torch.no_grad():
            initial_loss = float(loss_on(val_x, val_y, val_target))
            initial_train_loss = float(loss_on(train_x, train_y, target_x))
        history = []
        best_loss = initial_loss
        best_state = {
            k: v.detach().cpu().clone() for k, v in model.state_dict().items()
        }
        gradients = {}
        for epoch in range(settings["epochs"]):
            model.train()
            total = 0
            for batch in torch.randperm(len(train_y), device=device).split(
                settings["batch_size"]
            ):
                optimizer.zero_grad(set_to_none=True)
                loss = loss_on(train_x[batch], train_y[batch], target_x[batch])
                if not torch.isfinite(loss):
                    raise ValueError("nonfinite training loss")
                loss.backward()
                gradients = {
                    name: float(parameter.grad.norm())
                    for name, parameter in model.named_parameters()
                    if parameter.grad is not None
                }
                if not all(math.isfinite(value) for value in gradients.values()):
                    raise ValueError("nonfinite gradient")
                optimizer.step()
                total += float(loss.detach()) * len(batch)
            model.eval()
            with torch.no_grad():
                val_loss = float(loss_on(val_x, val_y, val_target))
            history.append(
                {
                    "epoch": epoch + 1,
                    "train_loss": total / len(train_y),
                    "val_loss": val_loss,
                    "weighted_loss": val_loss,
                    "loss_weight": 1.0,
                    "gradient_norms": gradients,
                }
            )
            if not math.isfinite(val_loss):
                raise ValueError("nonfinite validation loss")
            if val_loss < best_loss:
                best_loss = val_loss
                best_state = {
                    k: v.detach().cpu().clone() for k, v in model.state_dict().items()
                }
            run.update(history=history, epoch=epoch + 1)
            save("runs", run, run["id"])
        model.load_state_dict(best_state)
        model.eval()
        diagnosis = {
            "initial_val_loss": initial_loss,
            "best_val_loss": best_loss,
            "initial_train_loss": initial_train_loss,
            "all_finite": True,
            "gradient_norms": gradients,
            "loss": "MSE" if classifier else "cross_entropy",
            "loss_weight": 1.0,
            "temporal_loss": "not used",
            "seed": settings["seed"],
        }
        if classifier:
            torch.manual_seed(settings["seed"])
            ablation = Purifier().to(device)
            ablation_optimizer = torch.optim.Adam(
                ablation.parameters(), lr=settings["learning_rate"]
            )
            ablation_steps = 0
            for _ in range(settings["epochs"]):
                for batch in torch.randperm(len(train_y), device=device).split(
                    settings["batch_size"]
                ):
                    ablation_optimizer.zero_grad(set_to_none=True)
                    (
                        F.mse_loss(ablation(train_x[batch]), target_x[batch]) * 0
                    ).backward()
                    ablation_optimizer.step()
                    ablation_steps += 1
            ablation_result = metrics(classifier, val_x, val_y, ablation, val_target)
            clean = metrics(classifier, val_target, val_y)
            baseline = metrics(classifier, val_x, val_y, reference=val_target)
            full = metrics(classifier, val_x, val_y, model, val_target)
            clean_purified = metrics(classifier, val_target, val_y, model, val_target)
            diagnosis.update(
                clean=clean,
                attacked_baseline=baseline,
                purified=full,
                clean_purified=clean_purified,
                zero_loss_ablation={
                    "result": ablation_result,
                    "steps": ablation_steps,
                    "epochs": settings["epochs"],
                    "seed": settings["seed"],
                    "loss_weight": 0.0,
                    "weighted_loss": 0.0,
                    "gradient_norm": float(
                        torch.stack(
                            [p.grad.norm() for p in ablation.parameters()]
                        ).norm()
                    ),
                    "reason": "same initialization, batches and optimizer budget; MSE weight zero",
                },
                temporal_context="framewise purifier; no neighboring-frame input",
                randomness="deterministic inference; no random routes or voting",
            )
            probe = val_target[:1].detach().requires_grad_(True)
            (gradient,) = torch.autograd.grad(
                classifier(probe).square().sum(), probe, create_graph=True
            )
            (second,) = torch.autograd.grad(gradient.square().sum(), probe)
            diagnosis["classifier_input_gradient_norm"] = float(gradient.norm())
            diagnosis["classifier_second_derivative_finite"] = bool(
                torch.isfinite(second).all()
            )
            probe_loss = F.mse_loss(model(val_x), val_target)
            val_gradients = torch.autograd.grad(probe_loss, tuple(model.parameters()))
            diagnosis["validation_gradient_norms"] = {
                name: float(g.norm())
                for (name, _), g in zip(model.named_parameters(), val_gradients)
            }
            passed = (
                clean["accuracy"] >= settings["min_classifier_accuracy"]
                and full["mse"]
                <= baseline["mse"] * (1 - settings["min_mse_improvement"])
                and clean_purified["accuracy"] >= clean["accuracy"]
                and full["motion_error"] <= baseline["motion_error"]
                and all(
                    math.isfinite(float(g.norm())) and float(g.norm()) > 0
                    for g in val_gradients
                )
                and bool(torch.isfinite(second).all())
                and float(gradient.norm()) > 0
            )
        else:
            normal = metrics(model, val_x, val_y)
            reversed_time = metrics(model, val_x.flip(2), val_y)
            repeated_frame = metrics(model, val_x[:, :, :1].expand_as(val_x), val_y)
            diagnosis.update(
                validation=normal,
                reversed_time=reversed_time,
                repeated_frame=repeated_frame,
            )
            passed = normal["accuracy"] >= settings["min_classifier_accuracy"]
        diagnosis["decision"] = "passed" if passed else "inconclusive"
        buffer = io.BytesIO()
        torch.save(best_state, buffer)
        content = buffer.getvalue()
        file_id = call("storage", "POST", "/files", content=content).json()["file_id"]
        model_record.update(
            status="trained",
            weights_file=file_id,
            weights_sha256=hashlib.sha256(content).hexdigest(),
            run_id=run["id"],
            diagnostics=diagnosis,
            parameters=sum(p.numel() for p in model.parameters()),
        )
        if classifier_record:
            model_record["classifier_id"] = classifier_record["id"]
        save("models", model_record, model_id)
        run.update(
            status="completed",
            diagnostics=diagnosis,
            weights_file=file_id,
            weights_sha256=model_record["weights_sha256"],
            seconds=time.monotonic() - started,
        )
        save("runs", run, run["id"])
    except Exception as error:
        run.update(
            status="failed", error=str(error), seconds=time.monotonic() - started
        )
        model_record.update(status="failed")
        save("models", model_record, model_id)
        save("runs", run, run["id"])
