import time
import schedule
import subprocess
import sys
from datetime import datetime

RUNNING = False


def run_pipeline():
    global RUNNING

    if RUNNING:
        print()
        print("⚠️ Pipeline already running. Skipping...\n")
        return

    RUNNING = True

    print("\n=====================================")
    print(" 🚀  BlueSentinel SOC Pipeline START")
    print(f" 🕒  {datetime.now()}")
    print("=====================================\n")

    try:
        # 1. OSINT (SpiderFoot)
        subprocess.run([
            sys.executable,
            "-m",
            "modules.osint_spiderfoot.spiderfoot_automation"
        ], check=True)

        # 2. Detection + Alert
        subprocess.run([
            sys.executable,
            "-m",
            "modules.detection_engine.compare_by_target"
        ], check=True)

        print("\n✅ Pipeline finished successfully\n")

    except subprocess.CalledProcessError as e:
        print(f"❌ Subprocess error: {e}")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    finally:
        RUNNING = False


def main():
    print()
    print("🧠 BlueSentinel SOC Scheduler started...\n")

    # 🔥 PRODUÇÃO: roda 1x por semana
    schedule.every().sunday.at("10:00").do(run_pipeline)

    # 🔥 TESTE: executa ao iniciar
    run_pipeline()

    while True:
        schedule.run_pending()
        time.sleep(10)


if __name__ == "__main__":
    main()