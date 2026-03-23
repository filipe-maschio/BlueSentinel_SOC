import os
import json
import time
import re
import logging
from filelock import FileLock

from modules.alerting.alert_telegram import send_telegram_alert
from shared.paths import DATA_DIR

log = logging.getLogger(__name__)

DATA_PATH = DATA_DIR


def load_alert_history():
    history_path = os.path.join(DATA_PATH, "alert_history.log")

    if not os.path.exists(history_path):
        log.info("No alert history found, starting fresh")
        return set()

    history = set()

    try:
        with open(history_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    history.add(line)
    except Exception as e:
        log.exception(f"Failed to load alert history: {e}")

    return history


def clean_text(text):
    return re.sub(r"<SFURL>(.*?)</SFURL>", r"\1", text)


def print_target_header(target, index):
    print("\n####################################")
    print(f"#           TARGET # {index}             #")
    print("####################################")
    print(f"{target}\n")


def group_files_by_target():
    base_path = os.path.join(DATA_PATH, "spiderfoot_outputs")

    if not os.path.exists(base_path):
        log.warning(f"SpiderFoot output path not found: {base_path}")
        return {}

    groups = {}

    try:
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

    except Exception as e:
        log.exception(f"Error grouping files: {e}")

    return groups


def load_json(path):
    data = []

    try:
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

                except Exception as e:
                    log.warning(f"Skipping invalid JSON line: {e}")

    except Exception as e:
        log.exception(f"Failed to read file {path}: {e}")

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
        log.warning(f"Invalid data for files: {old_file}, {new_file}")
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
    lock = FileLock(history_path + ".lock")

    try:
        with lock:
            with open(history_path, "a", encoding="utf-8") as f:
                for item in items:
                    f.write(f"{target}|{item}\n")

    except Exception as e:
        log.exception(f"Failed to save alert history: {e}")


def main():
    log.info("Starting detection engine")

    groups = group_files_by_target()
    alert_history = load_alert_history()

    for idx, (target, data) in enumerate(groups.items(), start=1):

        target_path = data["path"]
        files = data["files"]

        print_target_header(target, idx)

        files.sort()

        if len(files) < 2:
            log.warning(f"Not enough files for target {target}")
            continue

        old_file = files[-2]
        new_file = files[-1]

        print(f"Comparing:\n - {old_file}\n - {new_file}")

        new_items = compare_files(target_path, old_file, new_file)

        filtered_items = {
            item for item in new_items
            if f"{target}|{item}" not in alert_history
        }

        if not filtered_items:
            log.info(f"No changes detected for {target}")
            continue

        high_items, medium_items, low_items = [], [], []

        for item in filtered_items:
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

        message_lines = [f"ALERT - {target}", ""]

        if high_items:
            message_lines.append(f"HIGH ({len(high_items)})")
            message_lines.extend(f"- {item}" for item in high_items)
            message_lines.append("")

        if medium_items:
            message_lines.append(f"MEDIUM ({len(medium_items)})")
            message_lines.extend(f"- {item}" for item in medium_items)
            message_lines.append("")

        if low_items:
            message_lines.append(f"LOW ({len(low_items)})")
            message_lines.extend(f"- {item}" for item in low_items)
            message_lines.append("")

        message_lines.append(f"Risk Score: {score}")

        message = "\n".join(message_lines)

        print(message)

        try:
            send_telegram_alert(message)
            save_alert(target, filtered_items)
        except Exception as e:
            log.exception(f"Failed to send/save alert for {target}: {e}")

        time.sleep(2)


if __name__ == "__main__":
    main()