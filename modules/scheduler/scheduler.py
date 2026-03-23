import time
import schedule
import subprocess
import sys
from datetime import datetime
from infrastructure.logging import setup_logging
import logging
from filelock import FileLock, Timeout


LOCK_FILE = "pipeline.lock"
log = logging.getLogger(__name__)


def print_banner():
    print("\n=====================================")
    print(" 🚀  BlueSentinel SOC Pipeline START")
    print(f" 🕒  {datetime.now()}")
    print("=====================================\n")


def run_pipeline():
    lock = FileLock(LOCK_FILE, timeout=1)

    try:
        with lock:
            print_banner()
            log.info("Pipeline START")

            subprocess.run([
                sys.executable,
                "-m",
                "modules.osint_spiderfoot.spiderfoot_automation"
            ], check=True)

            subprocess.run([
                sys.executable,
                "-m",
                "modules.detection_engine.compare_by_target"
            ], check=True)

            log.info("Pipeline finished successfully")

    except Timeout:
        log.warning("Pipeline already running. Skipping.")

    except subprocess.CalledProcessError as e:
        log.error(f"Subprocess error: {e}")

    except Exception:
        log.exception("Unexpected error")


def main():
    setup_logging()

    log.info("BlueSentinel SOC Scheduler started")

    schedule.every().monday.at("10:00").do(run_pipeline)

    # execução imediata (modo teste/dev)
    run_pipeline()

    while True:
        schedule.run_pending()
        time.sleep(10)


if __name__ == "__main__":
    main()