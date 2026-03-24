import time
import subprocess
import sys
import logging
from filelock import FileLock, Timeout
from infrastructure.logging import setup_logging
from datetime import datetime


LOCK_FILE = "pipeline.lock"


log = logging.getLogger(__name__)


def format_duration(duration_seconds):
    minutes = int(duration_seconds // 60)
    seconds = int(duration_seconds % 60)
    return f"{minutes}m{seconds:02d}s"


def run_pipeline():
    setup_logging()

    pipeline_start = time.time()

    lock = FileLock(LOCK_FILE, timeout=1)

    try:
        with lock:
            log.info("[Scheduler] " + "=" * 60)
            log.info(f"[Scheduler] NEW PIPELINE EXECUTION | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            log.info("[Scheduler] " + "=" * 60)

            # Start
            spider_start = time.time()

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "modules.osint_spiderfoot.spiderfoot_automation"
                ],
                capture_output=True,
                text=True,
                timeout=3000
            )

            clean_output = "\n".join(
                line for line in result.stdout.splitlines() if line.strip()
            )

            log.info("[Scheduler] ----- SPIDERFOOT START -----")

            if clean_output:
                for line in clean_output.splitlines():
                    log.info(f"[Scheduler] [SpiderFoot] {line}")

            log.info("[Scheduler] ----- SPIDERFOOT END -----")

            if result.returncode != 0:
                log.error(f"[Scheduler] SpiderFoot error: {result.stderr[:500]}")
                raise RuntimeError("SpiderFoot failed")

            log.info("[Scheduler] SpiderFoot step completed")
            spider_duration = time.time() - spider_start

            log.info(f"[Scheduler] SpiderFoot duration: {spider_duration:.2f}s ({format_duration(spider_duration)})")

            # Detection
            detection_start = time.time()

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "modules.detection_engine.compare_by_target"
                ],
                capture_output=True,
                text=True,
                timeout=600
            )

            clean_output = "\n".join(
                line for line in result.stdout.splitlines() if line.strip()
            )

            log.info("[Scheduler] ----- DETECTION START -----")

            if clean_output:
                for line in clean_output.splitlines():
                    log.info(f"[Scheduler] [Detection] {line}")

            log.info("[Scheduler] ----- DETECTION END -----")

            if result.returncode != 0:
                log.error(f"[Scheduler] Detection error: {result.stderr[:500]}")
                raise RuntimeError("Detection failed")

            log.info("[Scheduler] Detection step completed")
            detection_duration = time.time() - detection_start

            log.info(f"[Scheduler] Detection duration: {detection_duration:.2f}s ({format_duration(detection_duration)})")

            # Final
            total_sec = time.time() - pipeline_start

            log.info(f"[Scheduler] Total pipeline duration: {total_sec:.2f}s ({format_duration(total_sec)})")

            log.info("[Scheduler] Pipeline finished successfully")
            log.info("[Scheduler] " + "=" * 60)

    except Timeout:
        log.warning("[Scheduler] Pipeline already running. Skipping this execution.")
        return

    except Exception:
        log.exception("[Scheduler] Unexpected error during pipeline execution")


def main():
    run_pipeline()


if __name__ == "__main__":
    main()