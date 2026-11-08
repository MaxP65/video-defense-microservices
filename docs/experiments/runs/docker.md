# Docker CPU

Сгенерировано из `artifacts/docker/*-run.json` и `artifacts/docker/demo.json`.
Веса и исходные видео не входят в Git. Test не использован для выбора весов.

## checks-run

```json
{
  "type": "docker_api_checks",
  "status": "completed",
  "health": {
    "storage": {
      "service": "storage",
      "status": "ok"
    },
    "collector": {
      "service": "collector",
      "status": "ok"
    },
    "ml": {
      "service": "ml",
      "status": "ok"
    },
    "master": {
      "service": "master",
      "status": "ok"
    },
    "visualization": {
      "service": "visualization",
      "status": "ok"
    }
  },
  "storage_crud": "passed",
  "gui_html": "passed",
  "gui_gateway_proxy": "passed",
  "invalid_split_422": "passed",
  "batch": "passed: 2 clips from val, total=18",
  "repeat_collect": {
    "added": 0,
    "total": 72
  },
  "trained_models_via_gui_proxy": 2,
  "split_counts": {},
  "full_manifest": "artifacts\\docker\\checks-run.json"
}
```

## classifier-run

```json
{
  "type": "training",
  "model_id": "3a1dec18a081413a865e53db795ea853",
  "status": "completed",
  "parameters": {
    "epochs": 40
  },
  "id": "551f60eb7e8149f18e9018845e094164",
  "code_sha256": "94a1a3976d7795815b7956fd629f4728f97c3cf102517aff6809e6b587950d33",
  "device": "cpu",
  "config": {
    "classes": [
      "ApplyEyeMakeup",
      "BabyCrawling",
      "BasketballDunk"
    ],
    "frames": 8,
    "size": 48,
    "epochs": 40,
    "batch_size": 6,
    "learning_rate": 0.001,
    "epsilon": 0.03137254901960784,
    "seed": 42,
    "device": "auto",
    "threads": 2,
    "min_classifier_accuracy": 0.5,
    "min_mse_improvement": 0.01
  },
  "attack": {
    "method": "untargeted FGSM",
    "epsilon": 0.03137254901960784,
    "iterations": 1,
    "eot": 1,
    "voting": 1
  },
  "protocol": "training diagnostics; validation only; not a robustness evaluation",
  "epoch": 40,
  "diagnostics": {
    "initial_val_loss": 1.1105726957321167,
    "best_val_loss": 0.8188073635101318,
    "initial_train_loss": 1.1093605756759644,
    "all_finite": true,
    "gradient_norms": {
      "features.0.weight": 9.845532417297363,
      "features.0.bias": 3.451460599899292,
      "features.3.weight": 2.0404648780822754,
      "features.3.bias": 0.30716603994369507,
      "head.weight": 1.9215776920318604,
      "head.bias": 0.46893271803855896
    },
    "loss": "cross_entropy",
    "loss_weight": 1.0,
    "temporal_loss": "not used",
    "seed": 42,
    "validation": {
      "correct": 13,
      "n": 18,
      "accuracy": 0.7222222222222222
    },
    "reversed_time": {
      "correct": 13,
      "n": 18,
      "accuracy": 0.7222222222222222
    },
    "repeated_frame": {
      "correct": 12,
      "n": 18,
      "accuracy": 0.6666666666666666
    },
    "decision": "passed"
  },
  "weights_file": "0713a928a7ec44b681abbf2f263fe336",
  "weights_sha256": "7afd2c1306bd53dbdb8b2e2bcf3342398ab1629bb6509e5e1bee8ee07d59cb6e",
  "seconds": 32.922894203,
  "split_counts": {
    "train": 36,
    "val": 18
  },
  "full_manifest": "artifacts\\docker\\classifier-run.json"
}
```

## preflight-run

```json
{
  "type": "docker_preflight",
  "status": "completed",
  "date": "2026-11-08",
  "hypothesis": "five isolated services support collect, batch, training and FGSM through the gateway on CPU",
  "command": "docker compose --env-file config/ports.env up --build -d --wait --wait-timeout 180; python scripts/demo.py --epochs 40 --output artifacts/docker",
  "config": "config/docker.toml",
  "data": "UCF101, three classes; train 36 / val 18 / test 18; grouped split; seed 42",
  "training": "Adam, lr=0.001, batch=6, 40 epochs, no warmup; classifier CE then purifier MSE weight=1; MSE weight=0 control, identical budget",
  "criteria": "classifier validation accuracy >= 0.5; purifier MSE improvement >= 1%, clean accuracy and motion error not worse, finite nonzero full-model validation gradients and finite second derivatives",
  "scope": "training diagnostics and one validation technical example; no robustness sweep; no final-test tuning",
  "artifacts": "artifacts/docker; Docker volume vcr-microservices_storage",
  "failures": [],
  "result": "5/5 healthy; CRUD, GUI proxy, batch, collect, both training runs and validation FGSM inference passed",
  "code_sha256": "94a1a3976d7795815b7956fd629f4728f97c3cf102517aff6809e6b587950d33",
  "split_counts": {},
  "full_manifest": "artifacts\\docker\\preflight-run.json"
}
```

## purifier-run

```json
{
  "type": "training",
  "model_id": "bbe34ac18b854838ae995d99e7541336",
  "status": "completed",
  "parameters": {
    "epochs": 40
  },
  "id": "e973cebb3a664b768b486e77d0614de5",
  "code_sha256": "94a1a3976d7795815b7956fd629f4728f97c3cf102517aff6809e6b587950d33",
  "device": "cpu",
  "config": {
    "classes": [
      "ApplyEyeMakeup",
      "BabyCrawling",
      "BasketballDunk"
    ],
    "frames": 8,
    "size": 48,
    "epochs": 40,
    "batch_size": 6,
    "learning_rate": 0.001,
    "epsilon": 0.03137254901960784,
    "seed": 42,
    "device": "auto",
    "threads": 2,
    "min_classifier_accuracy": 0.5,
    "min_mse_improvement": 0.01
  },
  "attack": {
    "method": "untargeted FGSM",
    "epsilon": 0.03137254901960784,
    "iterations": 1,
    "eot": 1,
    "voting": 1
  },
  "protocol": "training diagnostics; validation only; not a robustness evaluation",
  "classifier_id": "3a1dec18a081413a865e53db795ea853",
  "classifier_weights_sha256": "7afd2c1306bd53dbdb8b2e2bcf3342398ab1629bb6509e5e1bee8ee07d59cb6e",
  "epoch": 40,
  "diagnostics": {
    "initial_val_loss": 0.0009048372157849371,
    "best_val_loss": 0.0006426777108572423,
    "initial_train_loss": 0.0008651419775560498,
    "all_finite": true,
    "gradient_norms": {
      "net.0.weight": 0.0017177334520965815,
      "net.0.bias": 0.0011777776526287198,
      "net.2.weight": 0.0010288566118106246,
      "net.2.bias": 0.0011839458020403981,
      "net.4.weight": 0.000944511906709522,
      "net.4.bias": 0.00338667887263
    },
    "loss": "MSE",
    "loss_weight": 1.0,
    "temporal_loss": "not used",
    "seed": 42,
    "clean": {
      "correct": 13,
      "n": 18,
      "accuracy": 0.7222222222222222
    },
    "attacked_baseline": {
      "correct": 5,
      "n": 18,
      "accuracy": 0.2777777777777778,
      "mse": 0.0009048372739925981,
      "psnr_db": 30.434295173267696,
      "motion_error": 0.0007924672099761665
    },
    "purified": {
      "correct": 8,
      "n": 18,
      "accuracy": 0.4444444444444444,
      "mse": 0.0006426777108572423,
      "psnr_db": 31.92006761890696,
      "motion_error": 0.00077962497016415
    },
    "clean_purified": {
      "correct": 14,
      "n": 18,
      "accuracy": 0.7777777777777778,
      "mse": 0.00011148731573484838,
      "psnr_db": 39.52774540864448,
      "motion_error": 4.431216439115815e-05
    },
    "zero_loss_ablation": {
      "result": {
        "correct": 5,
        "n": 18,
        "accuracy": 0.2777777777777778,
        "mse": 0.0009048372157849371,
        "psnr_db": 30.434295452646847,
        "motion_error": 0.0007924672099761665
      },
      "steps": 240,
      "epochs": 40,
      "seed": 42,
      "loss_weight": 0.0,
      "weighted_loss": 0.0,
      "gradient_norm": 0.0,
      "reason": "same initialization, batches and optimizer budget; MSE weight zero"
    },
    "temporal_context": "framewise purifier; no neighboring-frame input",
    "randomness": "deterministic inference; no random routes or voting",
    "classifier_input_gradient_norm": 0.0907120332121849,
    "classifier_second_derivative_finite": true,
    "validation_gradient_norms": {
      "net.0.weight": 0.0005629861843772233,
      "net.0.bias": 0.00033178587909787893,
      "net.2.weight": 0.0003072120889555663,
      "net.2.bias": 0.00030217805760912597,
      "net.4.weight": 0.00040577229810878634,
      "net.4.bias": 0.001263099373318255
    },
    "decision": "passed"
  },
  "weights_file": "ca0d988582564c0cb9c0d8c4114a969a",
  "weights_sha256": "d5d7f424a4a0bcebb579b81727c6f3558a6fa2503eac82f9ff8b118ac1c5ddcb",
  "seconds": 48.337206079,
  "split_counts": {
    "train": 36,
    "val": 18
  },
  "full_manifest": "artifacts\\docker\\purifier-run.json"
}
```

## runtime-run

```json
{
  "type": "docker_runtime",
  "status": "completed",
  "containers": [
    {
      "service": "collector",
      "container_id": "c2cf0f943b20",
      "state": "running",
      "health": "healthy",
      "image_id": "sha256:a4fa1c34d7a0cb8f855402ea386b08570f2c487631b70f119299fcbd04652e4c",
      "restart_count": 0
    },
    {
      "service": "master",
      "container_id": "2bddd44e11d4",
      "state": "running",
      "health": "healthy",
      "image_id": "sha256:969b7dab7dafe89fa3a011b0ba6ad86527187103ac56a07dab6e74bc73264436",
      "restart_count": 0
    },
    {
      "service": "ml",
      "container_id": "08984a575f5c",
      "state": "running",
      "health": "healthy",
      "image_id": "sha256:50f7246cf32c2b8d2b485f292904f220fe94f512a4b53a1ec25874c18b5c4ce6",
      "restart_count": 0
    },
    {
      "service": "storage",
      "container_id": "e73776cea077",
      "state": "running",
      "health": "healthy",
      "image_id": "sha256:dffbe34d3a9935821b2055a4e8382d89b243e3531ae8da60b709f2e0f16ad8ea",
      "restart_count": 0
    },
    {
      "service": "visualization",
      "container_id": "76e577db61f6",
      "state": "running",
      "health": "healthy",
      "image_id": "sha256:00379abe3b58ccfe82fe3b068fb88a2cf41322a8821891b12c019f9d0fcc5f97",
      "restart_count": 0
    }
  ],
  "environment": {
    "python": "3.12.16 (main, Nov  5 2026, 07:58:20) [GCC 14.2.0]",
    "torch": "2.4.1+cpu",
    "cuda": false,
    "opencv": "4.11.0",
    "fastapi": "0.124.4",
    "httpx": "0.28.1"
  },
  "split_counts": {},
  "full_manifest": "artifacts\\docker\\runtime-run.json"
}
```

## Технический пример на validation

```json
{
  "type": "experiment",
  "status": "completed",
  "video_id": "39ef5e5dba63403a8da503d504dd2c21",
  "classifier_id": "3a1dec18a081413a865e53db795ea853",
  "purifier_id": "bbe34ac18b854838ae995d99e7541336",
  "epsilon": 0.03137254901960784,
  "adaptive": false,
  "split": "val",
  "true_class": "ApplyEyeMakeup",
  "n": 1,
  "protocol": "classifier-only FGSM; technical demo",
  "admission": "passed",
  "clean": {
    "class": "ApplyEyeMakeup",
    "confidence": 0.4134950041770935,
    "correct": true
  },
  "attacked": {
    "class": "BasketballDunk",
    "confidence": 0.6248641610145569,
    "correct": false
  },
  "purified": {
    "class": "BasketballDunk",
    "confidence": 0.4219617545604706,
    "correct": false
  },
  "clean_purified": {
    "class": "ApplyEyeMakeup",
    "confidence": 0.4215259850025177,
    "correct": true
  },
  "attacked_quality": {
    "correct": 0,
    "n": 1,
    "accuracy": 0.0,
    "mse": 0.0009043331956490874,
    "psnr_db": 30.43671527079164,
    "motion_error": 0.0005278231110423803
  },
  "purified_quality": {
    "correct": 0,
    "n": 1,
    "accuracy": 0.0,
    "mse": 0.0004815140273422003,
    "psnr_db": 33.17391056600553,
    "motion_error": 0.0004982608952559531
  },
  "linf": 0.03137257695198059,
  "iterations": 1,
  "eot": 1,
  "voting": 1,
  "seconds": 0.6426198120000208,
  "classifier_weights_sha256": "7afd2c1306bd53dbdb8b2e2bcf3342398ab1629bb6509e5e1bee8ee07d59cb6e",
  "purifier_weights_sha256": "d5d7f424a4a0bcebb579b81727c6f3558a6fa2503eac82f9ff8b118ac1c5ddcb",
  "attack_success": true,
  "restored": false,
  "id": "8c224bd5d2a14f14b02ffa5abf6f3b5f"
}
```
