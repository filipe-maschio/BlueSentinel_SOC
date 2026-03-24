import os
import sys
import time
import subprocess
from datetime import datetime
import logging

from shared.config import SPIDERFOOT_TIMEOUT
from shared.constants import (
    STATUS_SUCCESS,
    STATUS_ERROR,
    STATUS_TIMEOUT,
)
from shared.paths import (
    TARGETS_FILE,
    SPIDERFOOT_PATH,
    SPIDERFOOT_OUTPUTS_DIR,
)


log = logging.getLogger(__name__)


def format_duration(duration_seconds):
    minutes = int(duration_seconds // 60)
    seconds = int(duration_seconds % 60)
    return f"{minutes}m{seconds:02d}s"


def sanitize_target(target):
    return target.replace("@", "_").replace(".", "_")


def build_scan_result(target, status, duration, output_file=None, error=None):
    return {
        "target": target,
        "status": status,
        "duration": duration,
        "output_file": output_file,
        "error": error,
    }


def load_targets():
    if not os.path.exists(TARGETS_FILE):
        log.error(f"[SpiderFoot] Targets file not found: {TARGETS_FILE}")
        return []

    with open(TARGETS_FILE, encoding="utf-8") as f:
        targets = [line.strip() for line in f if line.strip()]

    log.info(f"[SpiderFoot] Loaded {len(targets)} target(s)")
    return targets


def run_scan(target):
    log.info(f"[SpiderFoot] Running scan for: {target}")
    start_time = time.time()

    safe_target = sanitize_target(target)
    target_folder = os.path.join(SPIDERFOOT_OUTPUTS_DIR, safe_target)
    os.makedirs(target_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(target_folder, f"scan_{timestamp}.json")

    spiderfoot_dir = os.path.dirname(SPIDERFOOT_PATH)

    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = spiderfoot_dir

        with open(output_file, "w", encoding="utf-8") as f:
            result = subprocess.run(
                [
                    sys.executable,
                    SPIDERFOOT_PATH,
                    "-s", target,
                    "-o", "json",
                ],
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                timeout=SPIDERFOOT_TIMEOUT,
                cwd=spiderfoot_dir,
                env=env,
            )

        duration = time.time() - start_time

        if result.returncode != 0:
            error_message = (result.stderr or "").strip()[:500] or "Unknown SpiderFoot error"

            log.error(
                f"[SpiderFoot] Scan failed | target={target} | "
                f"duration={duration:.2f}s ({format_duration(duration)}) | "
                f"error={error_message}"
            )

            return build_scan_result(
                target=target,
                status=STATUS_ERROR,
                duration=duration,
                output_file=output_file,
                error=error_message,
            )

        log.info(
            f"[SpiderFoot] Scan completed | target={target} | "
            f"duration={duration:.2f}s ({format_duration(duration)})"
        )

        return build_scan_result(
            target=target,
            status=STATUS_SUCCESS,
            duration=duration,
            output_file=output_file,
            error=None,
        )

    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        error_message = f"SpiderFoot scan timed out after {SPIDERFOOT_TIMEOUT} seconds"

        log.warning(
            f"[SpiderFoot] Timeout | target={target} | "
            f"duration={duration:.2f}s ({format_duration(duration)})"
        )

        return build_scan_result(
            target=target,
            status=STATUS_TIMEOUT,
            duration=duration,
            output_file=output_file,
            error=error_message,
        )

    except Exception as exc:
        duration = time.time() - start_time

        log.exception(
            f"[SpiderFoot] Unexpected error | target={target} | "
            f"duration={duration:.2f}s ({format_duration(duration)})"
        )

        return build_scan_result(
            target=target,
            status=STATUS_ERROR,
            duration=duration,
            output_file=output_file,
            error=str(exc),
        )


def main():
    log.info("=" * 70)
    log.info("[SpiderFoot] Automation started")

    targets = load_targets()

    if not targets:
        log.warning("[SpiderFoot] No targets found")
        return []

    results = []

    for target in targets:
        results.append(run_scan(target))

    return results


if __name__ == "__main__":
    main()