import time
import schedule
import subprocess
import sys
from datetime import datetime
from infrastructure.logging import setup_logging
import logging
from filelock import FileLock, Timeout
import threading
import itertools


LOCK_FILE = "pipeline.lock"
log = logging.getLogger(__name__)


def print_banner():
    print("\n=====================================")
    print(" 🚀  BlueSentinel SOC Pipeline START")
    print(f" 🕒  {datetime.now()}")
    print("=====================================\n")


def spinner(stop_event, message="Processing"):
    for char in itertools.cycle(["|", "/", "-", "\\"]):
        if stop_event.is_set():
            break
        sys.stdout.write(f"\r{message}... {char}")
        sys.stdout.flush()
        time.sleep(0.1)

    sys.stdout.write("\r" + " " * (len(message) + 10) + "\r")


def run_pipeline():
    lock = FileLock(LOCK_FILE, timeout=1)

    try:
        with lock:
            print_banner()
            log.info("Pipeline started")

            stop_event = threading.Event()
            thread = threading.Thread(
                target=spinner,
                args=(stop_event, "Running SpiderFoot")
            )
            thread.start()

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "modules.osint_spiderfoot.spiderfoot_automation"
                ],
                capture_output=True,
                text=True
            )

            stop_event.set()
            thread.join()

            if result.returncode != 0:
                log.error(f"SpiderFoot error:\n{result.stderr}")
                raise RuntimeError("SpiderFoot failed")

            log.info("SpiderFoot step completed")

            stop_event = threading.Event()
            thread = threading.Thread(
                target=spinner,
                args=(stop_event, "Running Detection")
            )
            thread.start()

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "modules.detection_engine.compare_by_target"
                ],
                capture_output=True,
                text=True
            )

            stop_event.set()
            thread.join()

            if result.returncode != 0:
                log.error(f"Detection error:\n{result.stderr}")
                raise RuntimeError("Detection failed")

            log.info("Detection step completed")

            log.info("Pipeline finished successfully")

    except Timeout:
        log.warning("Pipeline already running. Skipping.")

    except Exception:
        log.exception("Unexpected error during pipeline execution")


def main():
    setup_logging()

    log.info("BlueSentinel SOC Scheduler started")

    schedule.every().monday.at("10:00").do(run_pipeline)

    run_pipeline()

    while True:
        try:
            schedule.run_pending()
            time.sleep(10)
        except Exception:
            log.exception("Scheduler loop error")
            time.sleep(5)


if __name__ == "__main__":
    main()