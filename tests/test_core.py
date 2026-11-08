import hashlib
import json
import sys
from pathlib import Path

import pytest
import torch
from fastapi.testclient import TestClient
from torch import nn
from torch.nn import functional as F

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ml.models import Classifier, Purifier, fgsm


def test_fgsm_uses_real_gradient_and_respects_budget():
    torch.manual_seed(7)
    model = Classifier(3).eval()
    x = torch.rand(2, 3, 4, 12, 12) * 0.8 + 0.1
    y = torch.tensor([0, 1])
    epsilon = 1e-3
    attacked = fgsm(model, x, y, epsilon)
    assert not torch.equal(attacked, x)
    assert (attacked - x).abs().max() <= epsilon + 1e-6
    assert attacked.min() >= 0 and attacked.max() <= 1
    assert F.cross_entropy(model(attacked), y) > F.cross_entropy(model(x), y)
    assert torch.equal(fgsm(model, x, y, 0), x)
    assert all(p.grad is None for p in model.parameters())


def test_purifier_identity_and_second_order_classifier_gradient():
    purifier = Purifier()
    classifier = Classifier(3).eval().requires_grad_(False)
    x = torch.rand(1, 3, 4, 12, 12).requires_grad_(True)
    assert torch.equal(purifier(x), x)
    output = nn.Sequential(purifier, classifier)(x)
    (gradient,) = torch.autograd.grad(output.square().sum(), x, create_graph=True)
    (second,) = torch.autograd.grad(gradient.square().sum(), x)
    assert gradient.norm() > 0
    assert torch.isfinite(second).all()


def test_storage_crud_files_and_missing_records(tmp_path, monkeypatch):
    import storage.app as storage

    monkeypatch.setattr(storage, "root", tmp_path)
    with TestClient(storage.app) as client:
        created = client.post("/records/videos", json={"class": "action"}).json()
        item_id = created["id"]
        assert client.get("/records/videos/" + item_id).json()["class"] == "action"
        assert (
            client.put(
                "/records/videos/" + item_id, json={"class": "other"}
            ).status_code
            == 200
        )
        assert client.get("/records/videos").json()[0]["class"] == "other"
        assert client.post("/files", content=b"video").status_code == 201
        file_id = client.post("/files", content=b"weights").json()["file_id"]
        assert client.get("/files/" + file_id).content == b"weights"
        assert client.get("/files/../../config/docker.toml").status_code == 404
        assert client.delete("/records/videos/" + item_id).status_code == 204
        assert client.get("/records/videos/" + item_id).status_code == 404
        assert client.post("/records/unknown", json={}).status_code == 404


def test_real_dataset_has_disjoint_groups_and_files():
    from common import CONFIG

    root = Path(CONFIG["collector"]["source"])
    manifest = root / "manifest.json"
    if not manifest.exists():
        pytest.skip("run prepare_data.py to check real dataset")
    values = json.loads(manifest.read_text("utf-8"))
    groups = {}
    hashes = {}
    for split in ("train", "val", "test"):
        items = [v for v in values if v["split"] == split]
        assert {v["label"] for v in items} == set(range(len(CONFIG["ml"]["classes"])))
        groups[split] = {v["group"] for v in items}
        hashes[split] = {
            hashlib.sha256((root / v["path"]).read_bytes()).hexdigest() for v in items
        }
    for a, b in [("train", "val"), ("train", "test"), ("val", "test")]:
        assert not groups[a] & groups[b]
        assert not hashes[a] & hashes[b]
