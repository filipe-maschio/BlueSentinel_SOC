import time
import logging

from modules.detection_engine.compare_by_target import run_detection_by_target
from shared.constants import (
    STATUS_SUCCESS,
    STATUS_NO_CHANGES,
    STATUS_ERROR,
)

log = logging.getLogger(__name__)


def format_duration(duration_seconds):
    minutes = int(duration_seconds // 60)
    seconds = int(duration_seconds % 60)
    return f"{minutes}m{seconds:02d}s"


def main():
    log.info("[Detection] Detection engine started")

    start_time = time.time()

    results = run_detection_by_target()

    total = len(results)
    success_count = sum(1 for r in results if r["status"] == STATUS_SUCCESS)
    no_changes_count = sum(1 for r in results if r["status"] == STATUS_NO_CHANGES)
    error_count = sum(1 for r in results if r["status"] == STATUS_ERROR)

    duration = time.time() - start_time

    log.info(
        f"[Detection] Detection engine finished | "
        f"total={total} | "
        f"success={success_count} | "
        f"no_changes={no_changes_count} | "
        f"error={error_count} | "
        f"duration={duration:.2f}s ({format_duration(duration)})"
    )

    return results


if __name__ == "__main__":
    main()