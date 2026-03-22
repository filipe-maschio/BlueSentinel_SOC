import os
import sys
import subprocess
from datetime import datetime
from shared.paths import DATA_DIR, TARGETS_FILE, SPIDERFOOT_PATH


def sanitize_target(target):
    return target.replace("@", "_").replace(".", "_")


def load_targets():
    if not os.path.exists(TARGETS_FILE):
        print(f"❌ Targets file not found: {TARGETS_FILE}")
        return []

    with open(TARGETS_FILE, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def run_scan(target):
    print(f"[+] Running scan for: {target}")

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

            # 🔥 AQUI ESTÁ A CHAVE
            env["PYTHONPATH"] = spiderfoot_dir

            result = subprocess.run(
                [
                    sys.executable,
                    SPIDERFOOT_PATH,  # 🔥 USAR CAMINHO COMPLETO
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
            print(f"❌ Error running scan for {target}")
            print(result.stderr[:500])
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