# 🛡️ BlueSentinel SOC v1.0

Automated OSINT-based Security Monitoring System (Mini SOC)

---

## 📌 Overview

BlueSentinel SOC is an automated pipeline that:

* Collects OSINT data using SpiderFoot
* Detects new exposures over time
* Classifies risk levels (HIGH / MEDIUM / LOW)
* Sends alerts via Telegram
* Runs automatically via scheduler

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

* Python **3.11**
* Git

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

Create `.env`:

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

### Run full pipeline

```
python -m modules.scheduler.scheduler
```

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

### SpiderFoot not found

Make sure you installed:

```
external/spiderfoot/sf.py
```

---

### No alerts triggered

* Ensure at least 2 scans exist per target
* Detection compares previous vs latest scan

---

### Telegram not sending

* Check `.env`
* Validate token and chat_id

---

## 🚀 Roadmap

* Docker support
* API (FastAPI)
* Dashboard
* Cloud deployment

---

## 📌 Status

Stable v1.0 baseline

---

## 👨‍💻 Author

Developed by **Fill "Filipe Maschio"**

If this project helped you, give it a star ⭐
