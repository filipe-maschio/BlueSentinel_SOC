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
    # 🔥 garante logging sempre
    setup_logging()

    pipeline_start = time.time()

    lock = FileLock(LOCK_FILE, timeout=1)

    try:
        with lock:
            log.info("")
            log.info("=" * 60)
            log.info(f"NEW PIPELINE EXECUTION | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            log.info("=" * 60)

            # ================================
            # 🔍 SPIDERFOOT
            # ================================
            spider_start = time.time()

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "modules.osint_spiderfoot.spiderfoot_automation"
                ],
                capture_output=True,
                text=True,
                timeout=600
            )

            clean_output = "\n".join(
                line for line in result.stdout.splitlines() if line.strip()
            )

            log.info("----- SPIDERFOOT START -----")

            if clean_output:
                for line in clean_output.splitlines():
                    log.info(f"[SpiderFoot] {line}")

            log.info("----- SPIDERFOOT END -----")

            if result.returncode != 0:
                log.error(f"SpiderFoot error:\n{result.stderr}")
                raise RuntimeError("SpiderFoot failed")

            log.info("SpiderFoot step completed")
            log.info(f"SpiderFoot duration: {time.time() - spider_start:.2f}s")

            # ================================
            # 🧠 DETECTION
            # ================================
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

            log.info("----- DETECTION START -----")

            if clean_output:
                for line in clean_output.splitlines():
                    log.info(f"[Detection] {line}")

            log.info("----- DETECTION END -----")

            if result.returncode != 0:
                log.error(f"Detection error:\n{result.stderr}")
                raise RuntimeError("Detection failed")

            log.info("Detection step completed")
            log.info(f"Detection duration: {time.time() - detection_start:.2f}s")

            # ================================
            # ✅ FINAL
            # ================================
            log.info(f"Total pipeline duration: {time.time() - pipeline_start:.2f}s")
            log.info("Pipeline finished successfully")
            log.info("=" * 60)
            log.info("")

    except Timeout:
        log.warning("Pipeline already running. Skipping this execution.")
        return

    except Exception:
        log.exception("Unexpected error during pipeline execution")


def main():
    run_pipeline()


if __name__ == "__main__":
    main()