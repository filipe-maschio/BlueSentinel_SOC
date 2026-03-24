import re


PLATFORM_ALIASES = {
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


GENERIC_PREFIXES = (
    "account on external site",
    "account discovered:",
)

LOWERCASE_WORDS = {"and", "or", "of", "on", "in", "for", "the"}


def clean_whitespace(text: str) -> str:
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def remove_sfurl_tags(text: str) -> str:
    return re.sub(r"<SFURL>(.*?)</SFURL>", r"\1", text, flags=re.IGNORECASE)


def remove_urls(text: str) -> str:
    text = re.sub(r"http[s]?://\S+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"www\.\S+", "", text, flags=re.IGNORECASE)
    text = re.sub(
        r"\b\S+\.(com|net|org|io|me|co|gov|edu|app|tv|gg|fm)\S*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    return clean_whitespace(text)


def strip_category_suffix(text: str) -> str:
    return re.sub(r"\s*\(category:.*?\)", "", text, flags=re.IGNORECASE).strip()


def strip_generic_prefixes(text: str) -> str:
    result = text.strip()
    lowered = result.lower()

    for prefix in GENERIC_PREFIXES:
        if lowered.startswith(prefix):
            result = result[len(prefix):].strip(" :-")
            lowered = result.lower()

    return result


def smart_title(text: str) -> str:
    words = text.split()
    normalized = []

    for word in words:
        if not word:
            continue

        if word.lower() in LOWERCASE_WORDS:
            normalized.append(word.lower())
            continue

        if "." in word or word.isupper():
            normalized.append(word)
            continue

        normalized.append(word.capitalize())

    return " ".join(normalized).strip(" -:")


def normalize_platform_name(name: str) -> str:
    name = clean_whitespace(name)
    name = remove_urls(name)
    name = strip_category_suffix(name)
    name = strip_generic_prefixes(name)
    name = clean_whitespace(name)

    if not name:
        return "Unknown Platform"

    lowered = name.lower()

    if lowered in PLATFORM_ALIASES:
        return PLATFORM_ALIASES[lowered]

    if "youtube" in lowered:
        return "YouTube"
    if "telegram" in lowered:
        return "Telegram"
    if "instagram" in lowered:
        return "Instagram"
    if "reddit" in lowered:
        return "Reddit"
    if "tiktok" in lowered:
        return "TikTok"
    if "garmin" in lowered:
        return "Garmin Connect"
    if "twitch" in lowered:
        return "Twitch"

    return smart_title(name)


def extract_platform_name(text: str) -> str:
    text = remove_sfurl_tags(text)
    text = clean_whitespace(text)
    text = remove_urls(text)

    parts = re.split(r"\s*\(category:.*?\)", text, flags=re.IGNORECASE)
    candidate = parts[0].strip() if parts else text.strip()

    candidate = clean_whitespace(candidate)
    return normalize_platform_name(candidate)