# Локальная проверка

Сгенерировано из `artifacts/*-run.json` и `artifacts/demo.json`.
Веса и исходные видео не входят в Git. Test не использован для выбора весов.

## adaptive-run

```json
{
  "type": "experiment",
  "status": "completed",
  "video_id": "4aa42386589a41dcb099ec95c9e44c45",
  "classifier_id": "8393e9c0c25c4b0bbea3785f33422986",
  "purifier_id": "9c506080cf49472791646ad68db9ad40",
  "epsilon": 0.03137254901960784,
  "adaptive": true,
  "split": "val",
  "true_class": "ApplyEyeMakeup",
  "n": 1,
  "protocol": "adaptive FGSM",
  "admission": "passed",
  "clean": {
    "class": "ApplyEyeMakeup",
    "confidence": 0.44932979345321655,
    "correct": true
  },
  "attacked": {
    "class": "BasketballDunk",
    "confidence": 0.39800000190734863,
    "correct": false
  },
  "purified": {
    "class": "BasketballDunk",
    "confidence": 0.4664030075073242,
    "correct": false
  },
  "clean_purified": {
    "class": "ApplyEyeMakeup",
    "confidence": 0.462108314037323,
    "correct": true
  },
  "attacked_quality": {
    "correct": 0,
    "n": 1,
    "accuracy": 0.0,
    "mse": 0.0008804426761344075,
    "psnr_db": 30.55298914823265,
    "motion_error": 0.0007288246415555477
  },
  "purified_quality": {
    "correct": 0,
    "n": 1,
    "accuracy": 0.0,
    "mse": 0.0008803694508969784,
    "psnr_db": 30.55335036015392,
    "motion_error": 0.0006936521967872977
  },
  "linf": 0.03137257695198059,
  "iterations": 1,
  "eot": 1,
  "voting": 1,
  "seconds": 0.5160000000032596,
  "classifier_weights_sha256": "c920b0925fb8427c22e97344f18fdbea75a41ee9e3115ce54e8f454d8cb11bb0",
  "purifier_weights_sha256": "c6e7bff9f0e0d408a327f989cf144bdc3ba606da95d282ef75fc45815e1da2a5",
  "attack_success": true,
  "restored": null,
  "id": "c13cd8f52df54ebd8ad1979c997329d6",
  "split_counts": {},
  "full_manifest": "artifacts\\adaptive-run.json"
}
```

## classifier-run

```json
{
  "type": "training",
  "model_id": "8393e9c0c25c4b0bbea3785f33422986",
  "status": "completed",
  "parameters": {
    "epochs": 40
  },
  "id": "1931ccd491b04b6f97cb97118c10f266",
  "code_sha256": "a0625ba4a88ba2202fda742ef91761986c2747eb67bce6db02f7006cdad60e86",
  "device": "cuda",
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
    "initial_val_loss": 1.1105725765228271,
    "best_val_loss": 0.7879738807678223,
    "initial_train_loss": 1.1093602180480957,
    "all_finite": true,
    "gradient_norms": {
      "features.0.weight": 0.6445752382278442,
      "features.0.bias": 0.369638592004776,
      "features.3.weight": 0.3224431276321411,
      "features.3.bias": 0.06319998949766159,
      "head.weight": 0.31721916794776917,
      "head.bias": 0.07404821366071701
    },
    "loss": "cross_entropy",
    "loss_weight": 1.0,
    "temporal_loss": "not used",
    "seed": 42,
    "validation": {
      "correct": 10,
      "n": 18,
      "accuracy": 0.5555555555555556
    },
    "reversed_time": {
      "correct": 10,
      "n": 18,
      "accuracy": 0.5555555555555556
    },
    "repeated_frame": {
      "correct": 13,
      "n": 18,
      "accuracy": 0.7222222222222222
    },
    "decision": "passed"
  },
  "weights_file": "a732e004468a4833822de0686b639559",
  "weights_sha256": "c920b0925fb8427c22e97344f18fdbea75a41ee9e3115ce54e8f454d8cb11bb0",
  "seconds": 19.75,
  "split_counts": {
    "train": 36,
    "val": 18
  },
  "full_manifest": "artifacts\\classifier-run.json"
}
```

## purifier-run

```json
{
  "type": "training",
  "model_id": "9c506080cf49472791646ad68db9ad40",
  "status": "completed",
  "parameters": {
    "epochs": 40
  },
  "id": "d1f5d20ac41341eca21323d6e9006e47",
  "code_sha256": "a0625ba4a88ba2202fda742ef91761986c2747eb67bce6db02f7006cdad60e86",
  "device": "cuda",
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
  "classifier_id": "8393e9c0c25c4b0bbea3785f33422986",
  "classifier_weights_sha256": "c920b0925fb8427c22e97344f18fdbea75a41ee9e3115ce54e8f454d8cb11bb0",
  "epoch": 40,
  "diagnostics": {
    "initial_val_loss": 0.0009052801178768277,
    "best_val_loss": 0.000634367170277983,
    "initial_train_loss": 0.000861368898767978,
    "all_finite": true,
    "gradient_norms": {
      "net.0.weight": 0.001028121798299253,
      "net.0.bias": 0.0010576462373137474,
      "net.2.weight": 0.0007850744877941906,
      "net.2.bias": 0.0011278166202828288,
      "net.4.weight": 0.0006853877566754818,
      "net.4.bias": 0.0014193807728588581
    },
    "loss": "MSE",
    "loss_weight": 1.0,
    "temporal_loss": "not used",
    "seed": 42,
    "clean": {
      "correct": 10,
      "n": 18,
      "accuracy": 0.5555555555555556
    },
    "attacked_baseline": {
      "correct": 5,
      "n": 18,
      "accuracy": 0.2777777777777778,
      "mse": 0.0009052801178768277,
      "psnr_db": 30.432170176734694,
      "motion_error": 0.0008120840648189187
    },
    "purified": {
      "correct": 7,
      "n": 18,
      "accuracy": 0.3888888888888889,
      "mse": 0.000634367170277983,
      "psnr_db": 31.97659300684213,
      "motion_error": 0.0007918723858892918
    },
    "clean_purified": {
      "correct": 12,
      "n": 18,
      "accuracy": 0.6666666666666666,
      "mse": 0.00011330936831654981,
      "psnr_db": 39.45734181575409,
      "motion_error": 5.022772529628128e-05
    },
    "zero_loss_ablation": {
      "result": {
        "correct": 5,
        "n": 18,
        "accuracy": 0.2777777777777778,
        "mse": 0.0009052801178768277,
        "psnr_db": 30.432170176734694,
        "motion_error": 0.0008120840648189187
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
    "classifier_input_gradient_norm": 0.11935825645923615,
    "classifier_second_derivative_finite": true,
    "validation_gradient_norms": {
      "net.0.weight": 0.0012122951447963715,
      "net.0.bias": 0.000896113459020853,
      "net.2.weight": 0.0007106289849616587,
      "net.2.bias": 0.0010395017452538013,
      "net.4.weight": 0.0008277485612779856,
      "net.4.bias": 0.002992692170664668
    },
    "decision": "passed"
  },
  "weights_file": "0927bfc441134107be78a69aa8da90e3",
  "weights_sha256": "c6e7bff9f0e0d408a327f989cf144bdc3ba606da95d282ef75fc45815e1da2a5",
  "seconds": 17.93699999997625,
  "split_counts": {
    "train": 36,
    "val": 18
  },
  "full_manifest": "artifacts\\purifier-run.json"
}
```

## ui-run

```json
{
  "type": "experiment",
  "status": "completed",
  "video_id": "4aa42386589a41dcb099ec95c9e44c45",
  "classifier_id": "8393e9c0c25c4b0bbea3785f33422986",
  "purifier_id": "9c506080cf49472791646ad68db9ad40",
  "epsilon": 0.03137254901960784,
  "adaptive": false,
  "split": "val",
  "true_class": "ApplyEyeMakeup",
  "n": 1,
  "protocol": "classifier-only FGSM; technical demo",
  "admission": "passed",
  "clean": {
    "class": "ApplyEyeMakeup",
    "confidence": 0.44932979345321655,
    "correct": true
  },
  "attacked": {
    "class": "BasketballDunk",
    "confidence": 0.5718998908996582,
    "correct": false
  },
  "purified": {
    "class": "ApplyEyeMakeup",
    "confidence": 0.3760775923728943,
    "correct": true
  },
  "clean_purified": {
    "class": "ApplyEyeMakeup",
    "confidence": 0.462108314037323,
    "correct": true
  },
  "attacked_quality": {
    "correct": 0,
    "n": 1,
    "accuracy": 0.0,
    "mse": 0.0009019013377837837,
    "psnr_db": 30.448409688878396,
    "motion_error": 0.0005385475815273821
  },
  "purified_quality": {
    "correct": 1,
    "n": 1,
    "accuracy": 1.0,
    "mse": 0.00044939169310964644,
    "psnr_db": 33.473749596649654,
    "motion_error": 0.0005026887520216405
  },
  "linf": 0.03137257695198059,
  "iterations": 1,
  "eot": 1,
  "voting": 1,
  "seconds": 0.6560000000172295,
  "classifier_weights_sha256": "c920b0925fb8427c22e97344f18fdbea75a41ee9e3115ce54e8f454d8cb11bb0",
  "purifier_weights_sha256": "c6e7bff9f0e0d408a327f989cf144bdc3ba606da95d282ef75fc45815e1da2a5",
  "attack_success": true,
  "restored": true,
  "id": "fbbb1451289f41ed856895af4e7f4a53",
  "split_counts": {},
  "full_manifest": "artifacts\\ui-run.json"
}
```

## Технический пример на validation

```json
{
  "type": "experiment",
  "status": "completed",
  "video_id": "4aa42386589a41dcb099ec95c9e44c45",
  "classifier_id": "8393e9c0c25c4b0bbea3785f33422986",
  "purifier_id": "9c506080cf49472791646ad68db9ad40",
  "epsilon": 0.03137254901960784,
  "adaptive": false,
  "split": "val",
  "true_class": "ApplyEyeMakeup",
  "n": 1,
  "protocol": "classifier-only FGSM; technical demo",
  "admission": "passed",
  "clean": {
    "class": "ApplyEyeMakeup",
    "confidence": 0.44932979345321655,
    "correct": true
  },
  "attacked": {
    "class": "BasketballDunk",
    "confidence": 0.5718998908996582,
    "correct": false
  },
  "purified": {
    "class": "ApplyEyeMakeup",
    "confidence": 0.3760775923728943,
    "correct": true
  },
  "clean_purified": {
    "class": "ApplyEyeMakeup",
    "confidence": 0.462108314037323,
    "correct": true
  },
  "attacked_quality": {
    "correct": 0,
    "n": 1,
    "accuracy": 0.0,
    "mse": 0.0009019013377837837,
    "psnr_db": 30.448409688878396,
    "motion_error": 0.0005385475815273821
  },
  "purified_quality": {
    "correct": 1,
    "n": 1,
    "accuracy": 1.0,
    "mse": 0.00044939169310964644,
    "psnr_db": 33.473749596649654,
    "motion_error": 0.0005026887520216405
  },
  "linf": 0.03137257695198059,
  "iterations": 1,
  "eot": 1,
  "voting": 1,
  "seconds": 2.655999999959022,
  "classifier_weights_sha256": "c920b0925fb8427c22e97344f18fdbea75a41ee9e3115ce54e8f454d8cb11bb0",
  "purifier_weights_sha256": "c6e7bff9f0e0d408a327f989cf144bdc3ba606da95d282ef75fc45815e1da2a5",
  "attack_success": true,
  "restored": true,
  "id": "7f62766dbec747538eda4eeba47c7e58"
}
```
