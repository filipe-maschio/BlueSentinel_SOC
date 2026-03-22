import os
import subprocess
from datetime import datetime
from shared.paths import DATA_DIR, TARGETS_FILE, SPIDERFOOT_PATH


def sanitize_target(target):
    return target.replace("@", "_").replace(".", "_")


def load_targets():
    with open(TARGETS_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]


def run_spiderfoot_scan(target):
    safe_target = sanitize_target(target)

    # 🔥 NOVO: pasta por target
    target_folder = os.path.join(DATA_DIR, "spiderfoot_outputs", safe_target)
    os.makedirs(target_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_file = os.path.join(
        target_folder,
        f"scan_{timestamp}.json"
    )

    print(f"[+] Running scan for: {target}")

    try:
        subprocess.run([
            "python",
            os.path.join(SPIDERFOOT_PATH, "sf.py"),
            "-s", target,
            "-o", "json"
        ], stdout=open(output_file, "w"), stderr=subprocess.DEVNULL)

        print(f"[+] Scan saved to: {output_file}")

    except Exception as e:
        print(f"[!] Error running scan for {target}: {e}")


def main():
    targets = load_targets()

    for target in targets:
        print(f"\n🎯 Processing target: {target}")
        run_spiderfoot_scan(target)


if __name__ == "__main__":
    main()