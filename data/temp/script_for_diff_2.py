import subprocess
import os
import sys
from datetime import datetime
from shared.paths import DATA_DIR, TARGETS_FILE, SPIDERFOOT_PATH


def sanitize_target(target):
    """
    Converts target into safe folder name.
    Example:
    email@gmail.com -> email_gmail_com
    """
    return target.replace("@", "_").replace(".", "_")


def load_targets():
    """
    Load targets from config file
    """
    if not os.path.exists(TARGETS_FILE):
        print(f"❌ Targets file not found: {TARGETS_FILE}")
        return []

    with open(TARGETS_FILE, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def run_scan(target):
    print(f"[+] Running scan for: {target}")

    safe_target = sanitize_target(target)

    # 🔥 NEW STRUCTURE: data/spiderfoot_outputs/<target>/
    target_folder = os.path.join(DATA_DIR, "spiderfoot_outputs", safe_target)
    os.makedirs(target_folder, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    output_file = os.path.join(
        target_folder,
        f"scan_{timestamp}.json"
    )

    command = [
        sys.executable,          # ensures venv is used
        SPIDERFOOT_PATH,
        "-s", target,
        "-o", "json"
    ]

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            result = subprocess.run(
                command,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                timeout=300
            )

        if result.returncode != 0:
            print(f"❌ Error running scan for {target}")
            print(result.stderr[:300])  # truncate output
        else:
            print(f"✅ Scan saved: {output_file}")

    except subprocess.TimeoutExpired:
        print(f"⏱️ Timeout running scan for {target}")

    except Exception as e:
        print(f"❌ Unexpected error for {target}: {e}")


def main():
    print("\n🕷️ SpiderFoot Automation Started\n")

    targets = load_targets()

    if not targets:
        print("⚠️ No targets found. Exiting...")
        return

    for target in targets:
        print(f"\n🎯 Processing target: {target}")
        run_scan(target)

    print("\n✅ SpiderFoot Automation Finished\n")


if __name__ == "__main__":
    main()