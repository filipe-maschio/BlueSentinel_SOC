import os
import json
import time
import re
import logging

from filelock import FileLock

from modules.alerting.alert_telegram import send_telegram_alert
from shared.config import DETECTION_TARGET_DELAY
from shared.constants import (
    STATUS_SUCCESS,
    STATUS_ERROR,
    STATUS_NO_CHANGES,
    RISK_HIGH,
    RISK_MEDIUM,
    RISK_LOW,
)
from shared.paths import (
    ALERT_HISTORY_FILE,
    ALERT_HISTORY_LOCK_FILE,
    SPIDERFOOT_OUTPUTS_DIR,
)
from shared.platform_normalizer import extract_platform_name, remove_urls


log = logging.getLogger(__name__)


def format_duration(duration_seconds):
    minutes = int(duration_seconds // 60)
    seconds = int(duration_seconds % 60)
    return f"{minutes}m{seconds:02d}s"


def build_detection_result(
    target,
    status,
    duration,
    old_file=None,
    new_file=None,
    new_items_count=0,
    high_count=0,
    medium_count=0,
    low_count=0,
    risk_score=0,
    alert_sent=False,
    error=None,
):
    return {
        "target": target,
        "status": status,
        "duration": duration,
        "old_file": old_file,
        "new_file": new_file,
        "new_items_count": new_items_count,
        "high_count": high_count,
        "medium_count": medium_count,
        "low_count": low_count,
        "risk_score": risk_score,
        "alert_sent": alert_sent,
        "error": error,
    }


def load_alert_history():
    if not os.path.exists(ALERT_HISTORY_FILE):
        log.info("[Detection] No alert history found, starting fresh")
        return set()

    history = set()

    try:
        with open(ALERT_HISTORY_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    history.add(line)
    except Exception:
        log.exception("[Detection] Failed to load alert history")

    return history


def clean_text(text):
    text = re.sub(r"<SFURL>(.*?)</SFURL>", r"\1", text)
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_target(target):
    return target.strip().lower()


def normalize_finding(item_type, item_data):
    return {
        "type": clean_text(item_type).strip(),
        "data": clean_text(item_data).strip(),
    }


def normalize_alert_key(target, finding):
    normalized_target = normalize_target(target)
    normalized_type = finding["type"].lower()
    normalized_data = finding["data"].lower()
    return f"{normalized_target}|{normalized_type}|{normalized_data}"


def has_alert_history_for_target(target, alert_history):
    prefix = f"{normalize_target(target)}|"
    return any(key.startswith(prefix) for key in alert_history)


def log_target_header(target, index):
    log.info(f"[Detection] ===== TARGET #{index} | {target} =====")


def group_files_by_target():
    base_path = SPIDERFOOT_OUTPUTS_DIR

    if not os.path.exists(base_path):
        log.warning(f"[Detection] SpiderFoot output path not found: {base_path}")
        return {}

    groups = {}

    try:
        for target in os.listdir(base_path):
            target_path = os.path.join(base_path, target)

            if not os.path.isdir(target_path):
                continue

            files = sorted(
                f for f in os.listdir(target_path)
                if f.endswith(".json")
            )

            if not files:
                continue

            groups[target] = {
                "path": target_path,
                "files": files,
            }

    except Exception:
        log.exception("[Detection] Error grouping files")

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

                if not line:
                    continue

                try:
                    parsed = json.loads(line)
                    if isinstance(parsed, dict):
                        data.append(parsed)
                except Exception as exc:
                    log.warning(f"[Detection] Skipping invalid JSON line in {path}: {exc}")

    except Exception:
        log.exception(f"[Detection] Failed to read file: {path}")

    return data


def extract_findings(data):
    findings = {}

    for item in data:
        if not isinstance(item, dict):
            continue

        item_type = item.get("type")
        item_data = item.get("data")

        if not item_type or not item_data:
            continue

        finding = normalize_finding(item_type, item_data)
        finding_key = (finding["type"].lower(), finding["data"].lower())

        findings[finding_key] = finding

    return findings


def compare_files(target_path, old_file, new_file):
    old_data = load_json(os.path.join(target_path, old_file))
    new_data = load_json(os.path.join(target_path, new_file))

    if not old_data or not new_data:
        log.warning(f"[Detection] Invalid data for files: {old_file}, {new_file}")
        return []

    old_findings = extract_findings(old_data)
    new_findings = extract_findings(new_data)

    new_keys = set(new_findings.keys()) - set(old_findings.keys())
    return [new_findings[key] for key in sorted(new_keys)]


def extract_initial_findings(target_path, scan_file):
    data = load_json(os.path.join(target_path, scan_file))

    if not data:
        log.warning(f"[Detection] Invalid data for initial scan: {scan_file}")
        return []

    return list(extract_findings(data).values())


def classify_risk(finding):
    item_type = finding["type"].lower()
    item_data = finding["data"].lower()

    if item_type in {
        "hacked email address",
        "breached account",
        "breach",
        "data leak",
    }:
        return RISK_HIGH

    if any(x in item_data for x in [
        "password",
        "collection",
        "combo",
        "dump",
        "leak",
        "breach",
    ]):
        return RISK_HIGH

    if item_type in {
        "account on external site",
        "username",
        "user",
        "profile",
    }:
        return RISK_MEDIUM

    return RISK_LOW


def is_alertworthy_on_first_scan(finding):
    item_type = finding["type"].lower()
    item_data = finding["data"].lower()

    if item_type in {
        "hacked email address",
        "breached account",
        "breach",
        "data leak",
    }:
        return True

    return any(term in item_data for term in [
        "password",
        "collection",
        "combo",
        "dump",
        "leak",
        "breach",
    ])


def calculate_risk_score(high, medium, low):
    return (high * 10) + (medium * 5) + (low * 1)


def save_alert(target, findings):
    lock = FileLock(ALERT_HISTORY_LOCK_FILE)

    try:
        with lock:
            with open(ALERT_HISTORY_FILE, "a", encoding="utf-8") as f:
                for finding in findings:
                    f.write(normalize_alert_key(target, finding) + "\n")
    except Exception:
        log.exception(f"[Detection] Failed to save alert history for target: {target}")
        raise


def render_finding(finding):
    return f'[{finding["type"]}] {finding["data"]}'


def remove_urls(text: str) -> str:
    text = re.sub(r"http[s]?://\S+", "", text)
    text = re.sub(r"www\.\S+", "", text)
    text = re.sub(r"\b\S+\.(com|net|org|io|me|co|gov|edu)\S*", "", text)
    return text.strip()


def remove_urls(text: str) -> str:
    """
    Remove URLs completas e fragmentos comuns que possam gerar preview no Telegram.
    """
    text = re.sub(r"http[s]?://\S+", "", text)
    text = re.sub(r"www\.\S+", "", text)
    text = re.sub(r"\b\S+\.(com|net|org|io|me|co|gov|edu)\S*", "", text, flags=re.IGNORECASE)
    return text.strip()


def normalize_platform_name(name: str) -> str:
    """
    Padroniza nomes de plataformas para exibição mais profissional.
    """
    name = clean_text(name)
    name = remove_urls(name)

    # remove conteúdos entre parênteses
    name = re.sub(r"\s*\(.*?\)\s*", " ", name)

    # remove prefixos genéricos
    generic_prefixes = [
        "account on external site",
        "account discovered:",
    ]
    lowered = name.lower().strip()
    for prefix in generic_prefixes:
        if lowered.startswith(prefix):
            name = name[len(prefix):].strip(" :-")
            lowered = name.lower().strip()

    # normalizações específicas
    replacements = {
        "garmin connect": "Garmin Connect",
        "telegram": "Telegram",
        "instagram": "Instagram",
        "reddit": "Reddit",
        "youtube user2": "YouTube",
        "youtube": "YouTube",
        "tiktok": "TikTok",
        "last.fm": "Last.fm",
        "chess.com": "Chess.com",
        "duolingo": "Duolingo",
        "flickr": "Flickr",
        "flipboard": "Flipboard",
        "imgur": "Imgur",
        "mcuuid": "MCUUID",
        "periscope": "Periscope",
        "pinterest": "Pinterest",
        "pornhub": "Pornhub",
        "redgifs": "RedGIFs",
        "scribd": "Scribd",
        "steam": "Steam",
        "truckersmp": "TruckersMP",
        "twitch": "Twitch",
        "tumblr": "Tumblr",
        "untappd": "Untappd",
    }

    key = name.lower().strip()
    if key in replacements:
        return replacements[key]

    # fallback: Title Case razoável
    words = name.split()
    normalized_words = []
    for word in words:
        if word.lower() in {"and", "or", "of", "on", "in", "for", "the"}:
            normalized_words.append(word.lower())
        else:
            normalized_words.append(word.capitalize())

    cleaned = " ".join(normalized_words).strip(" -:")
    return cleaned if cleaned else "Unknown Platform"


def extract_platform_name(text: str) -> str:
    """
    Tenta extrair apenas o nome da plataforma a partir do campo data.
    Exemplos:
    - 'Telegram (Category: social) https://t.me/x' -> 'Telegram'
    - 'Garmin connect (Category: health) ...' -> 'Garmin Connect'
    """
    text = clean_text(text)
    text = remove_urls(text)

    # pega só a parte antes de "(Category:"
    category_split = re.split(r"\s*\(category:.*?\)", text, flags=re.IGNORECASE)
    base = category_split[0].strip() if category_split else text.strip()

    # remove sobras estranhas
    base = re.sub(r"\s+", " ", base).strip(" -:")

    return normalize_platform_name(base)


def simplify_finding(finding):
    item_type = finding["type"].lower()
    original_data = finding["data"]

    clean_data = clean_text(original_data)
    clean_data = remove_urls(clean_data)

    domain_match = re.search(r"\[(.*?)\]", original_data)
    domain = domain_match.group(1).strip() if domain_match else None

    if item_type == "hacked email address":
        if domain:
            return f"Email exposed in breach ({domain})"
        return "Email exposed in breach"

    if item_type == "account on external site":
        platform = extract_platform_name(original_data)
        return f"Account discovered: {platform}"

    if item_type == "username":
        return f"Username discovered: {clean_data}"

    if item_type == "email address":
        return f"Email discovered: {clean_data}"

    return clean_data


def build_alert_message(target, high_items, medium_items, low_items, score, is_initial_scan=False):
    lines = []

    if is_initial_scan:
        lines.append(f"🚨 INITIAL ALERT — {target}")
    else:
        lines.append(f"🚨 ALERT — {target}")

    lines.append("")

    if high_items:
        lines.append(f"🔴 HIGH RISK ({len(high_items)})")
        for item in high_items:
            lines.append(f"• {simplify_finding(item)}")
        lines.append("")

    if medium_items:
        lines.append(f"🟠 MEDIUM RISK ({len(medium_items)})")
        for item in medium_items:
            lines.append(f"• {simplify_finding(item)}")
        lines.append("")

    if low_items:
        lines.append(f"🟢 LOW RISK ({len(low_items)})")
        for item in low_items:
            lines.append(f"• {simplify_finding(item)}")
        lines.append("")

    lines.append(f"📊 Risk Score: {score}")

    if is_initial_scan:
        lines.append("")
        lines.append("🧠 Context: First baseline detection")

    return "\n".join(lines)


def build_and_send_alert(target, candidate_items, duration, old_file=None, new_file=None, is_initial_scan=False):
    high_items, medium_items, low_items = [], [], []

    for item in candidate_items:
        risk = classify_risk(item)

        if risk == RISK_HIGH:
            high_items.append(item)
        elif risk == RISK_MEDIUM:
            medium_items.append(item)
        else:
            low_items.append(item)

    score = calculate_risk_score(
        len(high_items),
        len(medium_items),
        len(low_items),
    )

    message = build_alert_message(
        target=target,
        high_items=high_items,
        medium_items=medium_items,
        low_items=low_items,
        score=score,
        is_initial_scan=is_initial_scan,
    )

    log.info(
        f"[Detection] Alert generated | target={target} | "
        f"new_items={len(candidate_items)} | "
        f"high={len(high_items)} | "
        f"medium={len(medium_items)} | "
        f"low={len(low_items)} | "
        f"risk_score={score} | "
        f"initial_scan={is_initial_scan}"
    )

    send_telegram_alert(message)
    save_alert(target, candidate_items)

    return build_detection_result(
        target=target,
        status=STATUS_SUCCESS,
        duration=duration,
        old_file=old_file,
        new_file=new_file,
        new_items_count=len(candidate_items),
        high_count=len(high_items),
        medium_count=len(medium_items),
        low_count=len(low_items),
        risk_score=score,
        alert_sent=True,
        error=None,
    )


def process_initial_target(target, target_path, files, alert_history, start_time):
    scan_file = files[-1]

    log.info(
        f"[Detection] Initial baseline mode | target={target} | "
        f"scan_file={scan_file} | files_available={len(files)}"
    )

    findings = extract_initial_findings(target_path, scan_file)

    alertworthy_items = [
        item for item in findings
        if is_alertworthy_on_first_scan(item)
    ]

    filtered_items = list(alertworthy_items)

    log.info(
        f"[Detection] Initial baseline check | target={target} | "
        f"findings_total={len(findings)} | "
        f"alertworthy={len(alertworthy_items)} | "
        f"to_alert={len(filtered_items)}"
    )

    for item in alertworthy_items:
        key = normalize_alert_key(target, item)
        log.info(
            f"[Detection] Initial baseline item | target={target} | "
            f'in_history={key in alert_history} | item={repr(render_finding(item))}'
        )

    duration = time.time() - start_time

    if not filtered_items:
        log.info(
            f"[Detection] No alertworthy findings on initial baseline | "
            f"target={target} | duration={duration:.2f}s ({format_duration(duration)})"
        )

        return build_detection_result(
            target=target,
            status=STATUS_NO_CHANGES,
            duration=duration,
            old_file=None,
            new_file=scan_file,
            new_items_count=0,
            alert_sent=False,
            error=None,
        )

    result = build_and_send_alert(
        target=target,
        candidate_items=filtered_items,
        duration=duration,
        old_file=None,
        new_file=scan_file,
        is_initial_scan=True,
    )

    log.info(
        f"[Detection] Initial baseline processed successfully | "
        f"target={target} | new_items={len(filtered_items)} | "
        f"duration={duration:.2f}s ({format_duration(duration)})"
    )

    return result


def process_delta_target(target, target_path, files, alert_history, start_time):
    old_file = files[-2]
    new_file = files[-1]

    log.info(
        f"[Detection] Comparing files | target={target} | "
        f"old_file={old_file} | new_file={new_file}"
    )

    new_items = compare_files(target_path, old_file, new_file)

    filtered_items = [
        item for item in new_items
        if normalize_alert_key(target, item) not in alert_history
    ]

    log.info(
        f"[Detection] Dedupe check | target={target} | "
        f"new_items_raw={len(new_items)} | "
        f"already_alerted={len(new_items) - len(filtered_items)} | "
        f"new_items_after_dedupe={len(filtered_items)}"
    )

    for item in new_items:
        key = normalize_alert_key(target, item)
        log.info(
            f"[Detection] Dedupe item | target={target} | "
            f'in_history={key in alert_history} | item={repr(render_finding(item))}'
        )

    duration = time.time() - start_time

    if not filtered_items:
        log.info(
            f"[Detection] No changes detected | target={target} | "
            f"duration={duration:.2f}s ({format_duration(duration)})"
        )

        return build_detection_result(
            target=target,
            status=STATUS_NO_CHANGES,
            duration=duration,
            old_file=old_file,
            new_file=new_file,
            new_items_count=0,
            alert_sent=False,
            error=None,
        )

    result = build_and_send_alert(
        target=target,
        candidate_items=filtered_items,
        duration=duration,
        old_file=old_file,
        new_file=new_file,
        is_initial_scan=False,
    )

    log.info(
        f"[Detection] Target processed successfully | "
        f"target={target} | new_items={len(filtered_items)} | "
        f"duration={duration:.2f}s ({format_duration(duration)})"
    )

    return result


def process_target(target, data, alert_history, index):
    start_time = time.time()

    target_path = data["path"]
    files = sorted(data["files"])

    log_target_header(target, index)

    try:
        has_target_history = has_alert_history_for_target(target, alert_history)

        log.info(
            f"[Detection] Target state | target={target} | "
            f"files_count={len(files)} | has_alert_history={has_target_history}"
        )

        if not files:
            duration = time.time() - start_time

            log.warning(
                f"[Detection] No scan files available | target={target} | "
                f"duration={duration:.2f}s ({format_duration(duration)})"
            )

            return build_detection_result(
                target=target,
                status=STATUS_NO_CHANGES,
                duration=duration,
                error=None,
            )

        if not has_target_history:
            return process_initial_target(
                target=target,
                target_path=target_path,
                files=files,
                alert_history=alert_history,
                start_time=start_time,
            )

        if len(files) < 2:
            duration = time.time() - start_time

            log.info(
                f"[Detection] Waiting for second scan to compare | target={target} | "
                f"new_file={files[-1]} | duration={duration:.2f}s ({format_duration(duration)})"
            )

            return build_detection_result(
                target=target,
                status=STATUS_NO_CHANGES,
                duration=duration,
                old_file=None,
                new_file=files[-1],
                new_items_count=0,
                alert_sent=False,
                error=None,
            )

        return process_delta_target(
            target=target,
            target_path=target_path,
            files=files,
            alert_history=alert_history,
            start_time=start_time,
        )

    except Exception as exc:
        duration = time.time() - start_time

        log.exception(f"[Detection] Failed processing target: {target}")

        return build_detection_result(
            target=target,
            status=STATUS_ERROR,
            duration=duration,
            old_file=files[-2] if len(files) >= 2 else None,
            new_file=files[-1] if files else None,
            error=str(exc),
        )


def run_detection_by_target():
    log.info("[Detection] Starting compare-by-target strategy")

    groups = group_files_by_target()
    alert_history = load_alert_history()

    if not groups:
        log.warning("[Detection] No valid target groups found")
        return []

    results = []

    for idx, (target, data) in enumerate(groups.items(), start=1):
        result = process_target(target, data, alert_history, idx)
        results.append(result)
        time.sleep(DETECTION_TARGET_DELAY)

    return results


def main():
    return run_detection_by_target()


if __name__ == "__main__":
    main()