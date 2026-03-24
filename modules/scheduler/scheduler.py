import time
import subprocess
import sys
import logging
from filelock import FileLock, Timeout
from infrastructure.logging import setup_logging
from datetime import datetime


LOCK_FILE = "pipeline.lock"


log = logging.getLogger(__name__)


def run_pipeline():
    setup_logging()

    pipeline_start = time.time()

    lock = FileLock(LOCK_FILE, timeout=1)

    try:
        with lock:
            log.info("[Scheduler] ")
            log.info("[Scheduler] =" * 60)
            log.info(f"[Scheduler] NEW PIPELINE EXECUTION | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            log.info("[Scheduler] =" * 60)

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
                log.error(f"[Scheduler] SpiderFoot error:\n{result.stderr}")
                raise RuntimeError("SpiderFoot failed")

            log.info("[Scheduler] SpiderFoot step completed")
            log.info(f"[Scheduler] SpiderFoot duration: {time.time() - spider_start:.2f}s")

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
                log.error(f"[Scheduler] Detection error:\n{result.stderr}")
                raise RuntimeError("Detection failed")

            log.info("[Scheduler] Detection step completed")
            log.info(f"[Scheduler] Detection duration: {time.time() - detection_start:.2f}s")

            # Final
            log.info(f"[Scheduler] Total pipeline duration: {time.time() - pipeline_start:.2f}s")
            log.info("[Scheduler] Pipeline finished successfully")
            log.info("[Scheduler] =" * 60)
            log.info("[Scheduler] ")

    except Timeout:
        log.warning("[Scheduler] Pipeline already running. Skipping this execution.")
        return

    except Exception:
        log.exception("[Scheduler] Unexpected error during pipeline execution")


def main():
    run_pipeline()


if __name__ == "__main__":
    main()