import os
import json
import time
import re
from collections import defaultdict
from modules.alerting.alert_telegram import send_telegram_alert
from shared.paths import DATA_DIR


DATA_PATH = DATA_DIR


def load_alert_history():
    history_path = os.path.join(DATA_PATH, "alert_history.log")

    if not os.path.exists(history_path):
        return set()

    history = set()

    with open(history_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            # esperado: target|item
            history.add(line)

    return history
    

def clean_text(text):
    # 🔥 remove <SFURL>
    text = re.sub(r"<SFURL>(.*?)</SFURL>", r"\1", text)
    return text


def print_target_header(target, index):
    print("\n####################################")
    print(f"#           TARGET # {index}             #")
    print("####################################")
    print(f"🧠 {target}\n")


def group_files_by_target():
    base_path = os.path.join(DATA_PATH, "spiderfoot_outputs")

    groups = {}

    for target in os.listdir(base_path):
        target_path = os.path.join(base_path, target)

        if not os.path.isdir(target_path):
            continue

        files = [
            f for f in os.listdir(target_path)
            if f.endswith(".json")
        ]

        if len(files) < 2:
            continue

        groups[target] = {
            "path": target_path,
            "files": files
        }

    return groups


def load_json(path):
    data = []

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            line = line.rstrip(",")
            line = line.replace("[]", "")

            try:
                parsed = json.loads(line)

                if isinstance(parsed, dict):
                    data.append(parsed)

            except Exception:
                print(f"⚠️ Skipping invalid line: {line[:80]}...")

    return data


def extract_entities(data):
    entities = set()

    for item in data:
        if isinstance(item, dict):
            value = item.get("data")

            if value:
                value = clean_text(value)
                entities.add(value)

    return entities


def compare_files(target_path, old_file, new_file):
    old_data = load_json(os.path.join(target_path, old_file))
    new_data = load_json(os.path.join(target_path, new_file))

    if not old_data or not new_data:
        print("⚠️ Invalid data detected, skipping comparison...")
        return set()

    old_entities = extract_entities(old_data)
    new_entities = extract_entities(new_data)

    return new_entities - old_entities


def classify_risk(item):
    item_lower = item.lower()

    if any(x in item_lower for x in [
        "leak", "breach", "password",
        "collection", "combo", "dump"
    ]):
        return "HIGH"

    if any(x in item_lower for x in [
        "account", "user", "profile"
    ]):
        return "MEDIUM"

    return "LOW"


def calculate_risk_score(high, medium, low):
    return (high * 10) + (medium * 5) + (low * 1)


def save_alert(target, items):
    history_path = os.path.join(DATA_PATH, "alert_history.log")

    with open(history_path, "a", encoding="utf-8") as f:
        for item in items:
            f.write(f"{target}|{item}\n")


def main():
    groups = group_files_by_target()
    alert_history = load_alert_history()
    
    for idx, (target, data) in enumerate(groups.items(), start=1):

        target_path = data["path"]
        files = data["files"]

        print_target_header(target, idx)

        files.sort()

        if len(files) < 2:
            continue

        old_file = files[-2]
        new_file = files[-1]

        print(f"Comparing:\n - {old_file}\n - {new_file}")

        new_items = compare_files(target_path, old_file, new_file)

        filtered_items = set()

        for item in new_items:
            key = f"{target}|{item}"

            if key not in alert_history:
                filtered_items.add(item)

        new_items = filtered_items

        if not new_items:
            print("✅ No changes detected")
            continue

        high_items = []
        medium_items = []
        low_items = []

        for item in new_items:
            risk = classify_risk(item)

            if risk == "HIGH":
                high_items.append(item)
            elif risk == "MEDIUM":
                medium_items.append(item)
            else:
                low_items.append(item)

        score = calculate_risk_score(
            len(high_items),
            len(medium_items),
            len(low_items)
        )

        message = f"🚨 ALERT - {target}\n\n"

        if high_items:
            message += f"🔴 HIGH ({len(high_items)})\n"
            for item in high_items:
                message += f"- {item}\n"
            message += "\n"

        if medium_items:
            message += f"🟡 MEDIUM ({len(medium_items)})\n"
            for item in medium_items:
                message += f"- {item}\n"
            message += "\n"

        if low_items:
            message += f"🟢 LOW ({len(low_items)})\n"
            for item in low_items:
                message += f"- {item}\n"
            message += "\n"

        message += f"📊 Risk Score: {score}\n"

        print(message)

        send_telegram_alert(message)
        save_alert(target, new_items)

        time.sleep(2)


if __name__ == "__main__":
    main()