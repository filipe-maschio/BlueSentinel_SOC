import os
import json
import time
import logging
from datetime import datetime

from filelock import FileLock, Timeout

from infrastructure.logging import setup_logging
from modules.osint_spiderfoot.spiderfoot_automation import main as run_spiderfoot
from modules.detection_engine.detection import main as run_detection
from shared.config import PIPELINE_LOCK_FILE, PIPELINE_LOCK_TIMEOUT
from shared.constants import (
    STATUS_SUCCESS,
    STATUS_ERROR,
    STATUS_TIMEOUT,
    STATUS_NO_CHANGES,
    STATUS_RUNNING,
)
from shared.paths import PIPELINE_RUNS_DIR


log = logging.getLogger("scheduler")


def format_duration(duration_seconds):
    minutes = int(duration_seconds // 60)
    seconds = int(duration_seconds % 60)
    return f"{minutes}m{seconds:02d}s"


def build_step_summary(results):
    return {
        "total": len(results),
        "success": sum(1 for r in results if r["status"] == STATUS_SUCCESS),
        "no_changes": sum(1 for r in results if r["status"] == STATUS_NO_CHANGES),
        "error": sum(1 for r in results if r["status"] == STATUS_ERROR),
        "timeout": sum(1 for r in results if r["status"] == STATUS_TIMEOUT),
    }


def save_pipeline_result(pipeline_result):
    os.makedirs(PIPELINE_RUNS_DIR, exist_ok=True)

    run_id = pipeline_result["run_id"]

    historical_file = os.path.join(
        PIPELINE_RUNS_DIR,
        f"pipeline_run_{run_id}.json"
    )

    latest_file = os.path.join(
        PIPELINE_RUNS_DIR,
        "latest.json"
    )

    try:
        with open(historical_file, "w", encoding="utf-8") as f:
            json.dump(pipeline_result, f, indent=2, ensure_ascii=False)

        with open(latest_file, "w", encoding="utf-8") as f:
            json.dump(pipeline_result, f, indent=2, ensure_ascii=False)

        log.info(
            f"PIPELINE SAVE | historical_file={historical_file} | latest_file={latest_file}"
        )

    except Exception:
        log.exception("PIPELINE SAVE FAILED")


def execute_step(step_name, func):
    start_time = time.time()

    log.info(f"STEP START | step={step_name}")

    results = func()

    duration = time.time() - start_time
    summary = build_step_summary(results)

    log.info(
        f"STEP END | step={step_name} | "
        f"total={summary['total']} | "
        f"success={summary['success']} | "
        f"no_changes={summary['no_changes']} | "
        f"error={summary['error']} | "
        f"timeout={summary['timeout']} | "
        f"duration={duration:.2f}s ({format_duration(duration)})"
    )

    if summary["error"] > 0 or summary["timeout"] > 0:
        raise RuntimeError(f"{step_name} step had failures")

    return {
        "step_name": step_name,
        "duration_seconds": round(duration, 2),
        "duration_human": format_duration(duration),
        "summary": summary,
        "results": results,
    }


def run_pipeline():
    setup_logging()

    pipeline_start = time.time()
    lock = FileLock(PIPELINE_LOCK_FILE, timeout=PIPELINE_LOCK_TIMEOUT)

    started_at = datetime.now()
    run_id = started_at.strftime("%Y%m%d_%H%M%S")

    pipeline_result = {
        "run_id": run_id,
        "started_at": started_at.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": None,
        "status": STATUS_RUNNING,
        "total_duration_seconds": None,
        "total_duration_human": None,
        "steps": {},
        "error": None,
    }

    try:
        with lock:
            log.info("=" * 70)
            log.info(
                f"PIPELINE START | run_id={run_id} | started_at={pipeline_result['started_at']}"
            )

            spiderfoot_step = execute_step("SpiderFoot", run_spiderfoot)
            pipeline_result["steps"]["spiderfoot"] = spiderfoot_step

            detection_step = execute_step("Detection", run_detection)
            pipeline_result["steps"]["detection"] = detection_step

            total_duration = time.time() - pipeline_start

            pipeline_result["status"] = STATUS_SUCCESS
            pipeline_result["total_duration_seconds"] = round(total_duration, 2)
            pipeline_result["total_duration_human"] = format_duration(total_duration)
            pipeline_result["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            log.info(
                f"PIPELINE END | run_id={run_id} | status={STATUS_SUCCESS} | "
                f"duration={total_duration:.2f}s ({format_duration(total_duration)})"
            )

            save_pipeline_result(pipeline_result)

    except Timeout:
        log.warning("PIPELINE SKIPPED | reason=already_running")
        return

    except Exception as exc:
        total_duration = time.time() - pipeline_start

        pipeline_result["status"] = STATUS_ERROR
        pipeline_result["total_duration_seconds"] = round(total_duration, 2)
        pipeline_result["total_duration_human"] = format_duration(total_duration)
        pipeline_result["error"] = str(exc)
        pipeline_result["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log.error(
            f"PIPELINE FAILED | run_id={run_id} | error={str(exc)} | "
            f"duration={total_duration:.2f}s ({format_duration(total_duration)})"
        )
        log.exception("PIPELINE EXCEPTION DETAILS")

        try:
            save_pipeline_result(pipeline_result)
        except Exception:
            log.exception("FAILED TO SAVE PIPELINE RESULT AFTER ERROR")


def main():
    run_pipeline()


if __name__ == "__main__":
    main()