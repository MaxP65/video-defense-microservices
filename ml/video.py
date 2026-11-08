import base64
import tempfile
from pathlib import Path

import cv2
import numpy as np
import torch

from common import CONFIG, call


def read_clip(content):
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "video.avi"
        path.write_bytes(content)
        capture = cv2.VideoCapture(str(path))
        count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        frames = []
        try:
            for index in np.linspace(
                0, max(count - 1, 0), CONFIG["ml"]["frames"]
            ).astype(int):
                capture.set(cv2.CAP_PROP_POS_FRAMES, int(index))
                ok, frame = capture.read()
                if not ok:
                    raise ValueError("cannot decode video")
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                size = CONFIG["ml"]["size"]
                frames.append(cv2.resize(frame, (size, size)))
        finally:
            capture.release()
    return torch.from_numpy(np.stack(frames)).permute(3, 0, 1, 2).float() / 255


def dataset(items, device):
    clips = [
        read_clip(call("storage", "GET", "/files/" + v["file_id"]).content)
        for v in items
    ]
    return torch.stack(clips).to(device), torch.tensor(
        [v["label"] for v in items], device=device
    )


def preview(clip):
    frames = (
        (clip.detach().cpu().permute(1, 2, 3, 0).numpy() * 255)
        .round()
        .clip(0, 255)
        .astype("uint8")
    )
    result = []
    for frame in frames:
        ok, encoded = cv2.imencode(".png", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        if not ok:
            raise ValueError("cannot encode frame")
        result.append("data:image/png;base64," + base64.b64encode(encoded).decode())
    return result
