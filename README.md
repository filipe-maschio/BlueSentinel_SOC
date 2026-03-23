# 🛡️ BlueSentinel SOC v1.1

Automated OSINT-based Security Monitoring System (Mini SOC)

---

## 📌 Overview

BlueSentinel SOC is an automated security monitoring pipeline that:

- Collects OSINT data using SpiderFoot
- Detects new exposures over time
- Classifies risk levels (HIGH / MEDIUM / LOW)
- Sends alerts via Telegram
- Runs automatically via a scheduler
- Provides structured logging and execution control

---

## 🧠 Architecture

```
[ Scheduler ]
      ↓
[ SpiderFoot Collector ]
      ↓
[ Detection Engine ]
      ↓
[ Alerting System ]
```

---

## ⚙️ Requirements

- Python **3.11**
- Git

---

## 🚀 Setup

### 1. Clone repository

```
git clone <your-repo-url>
cd BlueSentinel_SOC
```

---

### 2. Create virtual environment

#### Windows:

```
python -m venv venv
.\venv\Scripts\activate
```

#### Linux / Mac:

```
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install dependencies

```
pip install -r requirements.txt
```

---

## 🕷️ Install SpiderFoot (REQUIRED)

```
git clone https://github.com/smicallef/spiderfoot.git external/spiderfoot
```

---

## 🔐 Environment variables

Create a `.env` file:

```
TELEGRAM_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
```

---

## 🎯 Add targets

Edit:

```
config/targets_for_spiderfoot.txt
```

Add one email per line.

---

## ▶️ Running

### Run SpiderFoot scan

```
python -m modules.osint_spiderfoot.spiderfoot_automation
```

---

### Run detection

```
python -m modules.detection_engine.compare_by_target
```

---

### Run full pipeline (recommended)

```
python -m modules.scheduler.scheduler
```

---

## ⚙️ Features (v1.1)

- Structured logging system
- Concurrency control with file locking
- Retry mechanism for Telegram alerts
- Deduplication of alerts
- Spinner-based CLI feedback (UX improvement)
- Robust error handling (no silent failures)

---

## 📂 Output

```
data/
 ├── spiderfoot_outputs/
 │    └── <target>/
 │         └── scan_YYYYMMDD_HHMMSS.json
 │
 └── alert_history.log
```

---

## ⚠️ Troubleshooting

### ❌ Module not found

Run:

```
pip install -r requirements.txt
```

---

### ❌ SpiderFoot not found

Make sure this exists:

```
external/spiderfoot/sf.py
```

If not:

```
git clone https://github.com/smicallef/spiderfoot.git external/spiderfoot
```

---

### ❌ Pipeline appears "stuck"

This is expected.

SpiderFoot can take time to execute depending on the target.

---

### ❌ Unicode / encoding errors (Windows)

Ensure no emojis are used in backend modules:

- spiderfoot_automation.py
- compare_by_target.py

---

### ❌ No alerts triggered

- Ensure at least **2 scans per target**
- Detection compares previous vs latest scan

---

### ❌ Telegram not sending

- Check `.env`
- Validate token and chat_id

---

## 🚀 Roadmap

### v1.2 (next)

- Remove subprocess (direct module integration)
- Pipeline abstraction layer
- Config centralization

### Future

- FastAPI service
- Web dashboard
- Docker support
- Cloud deployment

---

## 📌 Status

✅ Stable v1.1 (production-ready baseline)

---

## 👨‍💻 Author

Developed by **Fill "Filipe Maschio"**

If this project helped you, consider giving it a ⭐ on GitHub