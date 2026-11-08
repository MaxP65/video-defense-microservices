import hashlib
import json
import random
import re
import sys
import tarfile
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import CONFIG


def prepare():
    root = Path(CONFIG["collector"]["source"])
    root.mkdir(parents=True, exist_ok=True)
    archive = root.parent / "ucf101-subset.tar.gz"
    expected = CONFIG["dataset"]["sha256"]
    if not archive.exists():
        temporary = archive.with_suffix(".download")
        with httpx.stream(
            "GET", CONFIG["dataset"]["url"], follow_redirects=True, timeout=120
        ) as response:
            response.raise_for_status()
            with temporary.open("wb") as target:
                for chunk in response.iter_bytes():
                    target.write(chunk)
        temporary.replace(archive)
    if hashlib.file_digest(archive.open("rb"), "sha256").hexdigest() != expected:
        raise ValueError("archive checksum mismatch; remove archive and retry")
    result = []
    with tarfile.open(archive) as source:
        members = {}
        for member in source.getmembers():
            name = Path(member.name).name
            if member.isfile() and name.endswith(".avi"):
                members[name] = member
        for label, action in enumerate(CONFIG["ml"]["classes"]):
            grouped = {}
            for name, member in sorted(members.items()):
                match = re.fullmatch(
                    r"v_" + re.escape(action) + r"_(g\d+)_c\d+\.avi", name
                )
                if match:
                    grouped.setdefault(match[1], []).append(member)
            groups = sorted(grouped)
            random.Random(CONFIG["ml"]["seed"]).shuffle(groups)
            if len(groups) < 5:
                raise ValueError(f"not enough independent groups for {action}")
            first = max(1, int(len(groups) * 0.6))
            second = min(len(groups) - 1, max(first + 1, int(len(groups) * 0.8)))
            splits = {
                "train": groups[:first],
                "val": groups[first:second],
                "test": groups[second:],
            }
            for split, selected in splits.items():
                candidates = [member for group in selected for member in grouped[group]]
                random.Random(CONFIG["ml"]["seed"]).shuffle(candidates)
                limit = CONFIG["dataset"][split + "_per_class"]
                if len(candidates) < limit:
                    raise ValueError(
                        f"not enough clips for {action}/{split}: {len(candidates)} < {limit}"
                    )
                for member in candidates[:limit]:
                    name = Path(member.name).name
                    extracted = source.extractfile(member)
                    content = extracted.read()
                    (root / name).write_bytes(content)
                    group = re.search(r"_g\d+_", name)[0].strip("_")
                    result.append(
                        {
                            "path": name,
                            "class": action,
                            "label": label,
                            "split": split,
                            "group": action + "_" + group,
                            "source": member.name,
                            "dataset": "UCF101 subset",
                            "archive_sha256": expected,
                        }
                    )
    (root / "manifest.json").write_text(json.dumps(result, indent=2), "utf-8")
    print(
        json.dumps(
            {
                split: sum(v["split"] == split for v in result)
                for split in ("train", "val", "test")
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    prepare()
