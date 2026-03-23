import os
import sys
import subprocess
from datetime import datetime
from shared.paths import DATA_DIR, TARGETS_FILE, SPIDERFOOT_PATH
import logging


log = logging.getLogger(__name__)


def sanitize_target(target):
    return target.replace("@", "_").replace(".", "_")


def load_targets():
    if not os.path.exists(TARGETS_FILE):
        print(f"Targets file not found: {TARGETS_FILE}")
        return []

    with open(TARGETS_FILE, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def run_scan(target):
    log.info(f"Running scan for: {target}")

    safe_target = sanitize_target(target)

    target_folder = os.path.join(DATA_DIR, "spiderfoot_outputs", safe_target)
    os.makedirs(target_folder, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    output_file = os.path.join(
        target_folder,
        f"scan_{timestamp}.json"
    )

    spiderfoot_dir = os.path.dirname(SPIDERFOOT_PATH)

    try:
        with open(output_file, "w", encoding="utf-8") as f:

            env = os.environ.copy()

            env["PYTHONPATH"] = spiderfoot_dir

            result = subprocess.run(
                [
                    sys.executable,
                    SPIDERFOOT_PATH,
                    "-s", target,
                    "-o", "json"
                ],
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                timeout=300,
                cwd=spiderfoot_dir,
                env=env
            )

        if result.returncode != 0:
            log.error(f"Error running scan for {target}: {result.stderr[:500]}")
        else:
            log.info(f"Scan saved: {output_file}")

    except subprocess.TimeoutExpired:
        print(f"Timeout running scan for {target}")

    except Exception as e:
        print(f"Unexpected error for {target}: {e}")


def main():
    print("\nSpiderFoot Automation Started\n")

    targets = load_targets()

    if not targets:
        print("No targets found. Exiting...")
        return

    for target in targets:
        print(f"\nProcessing target: {target}")
        run_scan(target)

    print("\nSpiderFoot Automation Finished\n")


if __name__ == "__main__":
    main()