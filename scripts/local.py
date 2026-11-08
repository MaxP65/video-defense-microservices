import os
import subprocess
import sys
import time
import tomllib
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    original = Path("config/docker.toml").read_text("utf-8")
    config = tomllib.loads(original)
    for service in config["services"]:
        original = original.replace(
            f"http://{service}:8000", f"http://127.0.0.1:{config['ports'][service]}"
        )
    Path("config/local.toml").write_text(original, "utf-8")
    env = {**os.environ, "VCR_CONFIG": "config/local.toml", "PYTHONIOENCODING": "utf-8"}
    Path("logs").mkdir(exist_ok=True)
    processes = []
    handles = []
    try:
        for service, port in config["ports"].items():
            handle = open(f"logs/{service}-console.log", "w", encoding="utf-8")
            handles.append(handle)
            processes.append(
                subprocess.Popen(
                    [
                        sys.executable,
                        "-m",
                        "uvicorn",
                        service + ".app:app",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        str(port),
                    ],
                    env=env,
                    stdout=handle,
                    stderr=handle,
                )
            )
        print(f"GUI: http://localhost:{config['ports']['visualization']}", flush=True)
        print("Ctrl+C stops all five services", flush=True)
        while all(process.poll() is None for process in processes):
            time.sleep(1)
        failed = [
            (service, process.returncode)
            for service, process in zip(config["ports"], processes)
            if process.poll() is not None
        ]
        raise RuntimeError(f"a service stopped: {failed}; see logs")
    except KeyboardInterrupt:
        pass
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
        for process in processes:
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
        for handle in handles:
            handle.close()


if __name__ == "__main__":
    main()
