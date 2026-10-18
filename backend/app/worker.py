import json, os, signal, subprocess, sys, time
from filelock import FileLock
from . import db, service
from .settings import DATA, ROOT


def execute(row):
    folder = service.job_dir(row["id"])
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "preset.json").write_text(json.dumps(row["preset"]))
    state = folder / "job.json"
    if not state.exists():
        state.write_text(
            json.dumps(
                {
                    "job_id": row["id"],
                    "paper_id": row["paper_id"],
                    "user_id": "owner",
                    "preset_id": row["preset"]["preset_id"],
                }
            )
        )
    env = dict(os.environ)
    env.pop(
        "SS_RENDER_MODE", None
    )  # API jobs must never opt into trusted golden local mode.
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    log = open(folder / "worker.log", "a")
    child = subprocess.Popen(
        [sys.executable, "-m", "app.run_job", row["id"]],
        cwd=ROOT,
        env=env,
        stdout=log,
        stderr=log,
        start_new_session=True,
    )
    start = time.monotonic()
    terminated = False
    try:
        while child.poll() is None:
            current = db.get(row["id"])
            cancelled = current["cancel_requested"]
            timed_out = time.monotonic() - start > int(
                os.getenv("SS_JOB_TIMEOUT_SEC", "3600")
            )
            if cancelled or timed_out:
                (folder / "cancel.requested").touch()
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()
                if shutil.which("docker"):
                    result = subprocess.run(
                        [
                            "docker",
                            "ps",
                            "-q",
                            "--filter",
                            f"name=ss-render-{row['id']}-",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    for container in result.stdout.split():
                        subprocess.run(
                            ["docker", "rm", "-f", container],
                            capture_output=True,
                            timeout=15,
                        )
                db.update(
                    row["id"],
                    status="cancelled" if cancelled else "failed",
                    error=None if cancelled else "Job timeout exceeded",
                )
                terminated = True
                break
            time.sleep(1)
        if not terminated and db.get(row["id"])["status"] == "running":
            db.update(
                row["id"],
                status="failed",
                error="Worker process exited before completion; inspect local worker.log",
            )
    finally:
        if child.poll() is None:
            os.killpg(child.pid, signal.SIGTERM)
            child.wait(timeout=10)
        log.close()


from pathlib import Path
import shutil


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    with FileLock(str(DATA / "worker.lock"), timeout=0):
        # A crashed worker never silently repeats potentially billable LLM calls.
        for row in db.all_jobs():
            if row["status"] == "running":
                db.update(
                    row["id"],
                    status="failed",
                    error="Worker interrupted; explicitly retry to resume",
                )
        print("ScholarShorts worker ready", flush=True)
        while True:
            row = db.claim()
            if row:
                execute(row)
            else:
                time.sleep(1)


if __name__ == "__main__":
    main()
