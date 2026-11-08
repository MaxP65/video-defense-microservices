import argparse
import json
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("--check", action="store_true")
parser.add_argument("--source", type=Path, default=Path("artifacts"))
parser.add_argument(
    "--output", type=Path, default=Path("docs/experiments/runs/local.md")
)
parser.add_argument("--title", default="Локальная проверка")
args = parser.parse_args()
target = args.output
lines = [
    f"# {args.title}",
    "",
    f"Сгенерировано из `{args.source.as_posix()}/*-run.json` и `{args.source.as_posix()}/demo.json`.",
    "Веса и исходные видео не входят в Git. Test не использован для выбора весов.",
    "",
]
for path in sorted(args.source.glob("*-run.json")):
    value = json.loads(path.read_text("utf-8"))
    compact = {k: v for k, v in value.items() if k not in {"splits", "history"}}
    compact["split_counts"] = {k: len(v) for k, v in value.get("splits", {}).items()}
    compact["full_manifest"] = str(path)
    lines += [
        f"## {path.stem}",
        "",
        "```json",
        json.dumps(compact, ensure_ascii=False, indent=2),
        "```",
        "",
    ]
demo = args.source / "demo.json"
if demo.exists():
    lines += [
        "## Технический пример на validation",
        "",
        "```json",
        demo.read_text("utf-8"),
        "```",
        "",
    ]
content = "\n".join(lines)
if args.check:
    if not target.exists() or target.read_text("utf-8") != content:
        raise SystemExit("experiment documentation is outdated")
else:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, "utf-8")
