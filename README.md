# 🛡️ BlueSentinel SOC v1.2  
  
Automated OSINT-based Security Monitoring System (Mini SOC)  
  
---  
  
## 📌 Overview  
  
BlueSentinel SOC is an automated security monitoring pipeline that:  
  
- Collects OSINT data using SpiderFoot  
- Stores scan results by target  
- Detects new findings and initial baseline exposures  
- Classifies findings by risk level (HIGH / MEDIUM / LOW)  
- Sends alerts via Telegram  
- Runs as a single scheduled job  
- Provides structured logging for launcher, execution, and SOC events  
  
---  
  
## 🧠 Architecture  
  
[ Scheduler / Launcher ]  
          ↓  
[ SpiderFoot Collector ]  
          ↓  
[ Detection Engine ]  
          ↓  
[ Telegram Alerting ]

---

## ⚙️ Requirements

- Python **3.11**
- Git

---

## 🚀 Setup

### 1. Clone repository

git clone  "your-repo-url"
cd BlueSentinel_SOC

---

### 2. Create virtual environment

#### Windows

python -m venv venv  
.\venv\Scripts\activate

#### Linux / Mac

python3 -m venv venv  
source venv/bin/activate

---

### 3. Install dependencies

pip install -r requirements.txt

---

## 🕷️ Install SpiderFoot (required)

git clone https://github.com/smicallef/spiderfoot.git external/spiderfoot

BlueSentinel uses a local SpiderFoot checkout under:

external/spiderfoot

---

## 🔐 Environment variables

Create a `.env` file based on `.env.example`:

TELEGRAM_TOKEN=your_token  
TELEGRAM_CHAT_ID=your_chat_id

---

## 🎯 Add targets

Edit:

config/targets_for_spiderfoot.txt

Add one target per line.

Typical example:

user@example.com  
anotheruser@example.com

---

## ▶️ Running

### Run SpiderFoot only

python -m modules.osint_spiderfoot.spiderfoot_automation

### Run detection only

python -m modules.detection_engine.detection

### Run full pipeline (recommended)

python -m modules.scheduler.scheduler

### Run via launcher (Windows)

run_soc.bat

---

## ✅ Features in v1.2

- Single-run scheduler flow
- Stable launcher execution with proper process return
- Structured logging across multiple log files
- Detection by target
- Initial baseline alerting
- Alert deduplication through alert history
- Telegram retry and timeout handling
- SOC-style Telegram message formatting
- URL stripping to avoid Telegram preview pollution
- Platform normalization for cleaner alert output
- Centralized settings, constants, and config modules

---

## 📂 Project structure

BlueSentinel_SOC/  
├── config/  
│   ├── targets_for_spiderfoot.txt  
│   └── targets_for_spiderfoot.example.txt  
├── data/  
│   ├── spiderfoot_outputs/  
│   │   └── "target"/  
│   │       └── scan_YYYYMMDD_HHMMSS.json  
│   └── alert_history.log  
├── infrastructure/  
│   ├── __init__.py  
│   └── logging.py  
├── logs/  
│   ├── launcher.log  
│   ├── execution.log  
│   ├── soc.log  
│   └── error.log  
├── modules/  
│   ├── alerting/  
│   │   ├── __init__.py  
│   │   └── alert_telegram.py  
│   ├── detection_engine/  
│   │   ├── __init__.py  
│   │   ├── compare_by_target.py  
│   │   └── detection.py  
│   ├── osint_spiderfoot/  
│   │   ├── __init__.py  
│   │   └── spiderfoot_automation.py  
│   └── scheduler/  
│       └── scheduler.py  
├── shared/  
│   ├── __init__.py  
│   ├── config.py  
│   ├── constants.py  
│   ├── paths.py  
│   ├── platform_normalizer.py  
│   └── settings.py  
├── .env.example  
├── requirements.txt  
└── run_soc.bat

---

## 📜 Logs

### `launcher.log`

Tracks the Windows launcher / batch execution lifecycle.

Examples:

- START
- BEFORE PYTHON EXECUTION
- AFTER PYTHON EXECUTION
- FINISHED

### `execution.log`

Detailed technical execution log for debugging.

### `soc.log`

Operational pipeline log focused on security workflow visibility.

### `error.log`

Errors and exceptions.

---

## 🚨 Detection behavior

### Initial baseline

If a target has no alert history yet, BlueSentinel treats the latest scan as the initial baseline and may send an **INITIAL ALERT** for alertworthy findings.

### Delta detection

If a target already has history, BlueSentinel compares the latest scan against the previous one and alerts only on new findings not already recorded.

### Deduplication

Previously alerted findings are stored in `alert_history.log` and suppressed in later runs.

---

## 📲 Telegram alert format

Alerts are formatted for analyst readability:

- HIGH / MEDIUM / LOW sections
- risk score
- cleaned platform names
- no raw URLs in the message body

This avoids noisy previews and improves triage quality.

---

## ⚠️ Troubleshooting

### Module not found

Install dependencies again:

pip install -r requirements.txt

### SpiderFoot not found

Ensure this file exists:

external/spiderfoot/sf.py

If not:

git clone https://github.com/smicallef/spiderfoot.git external/spiderfoot

### No Telegram alerts

Check:

- `.env`
- `TELEGRAM_TOKEN`
- `TELEGRAM_CHAT_ID`

Also verify whether:

- the target already has alert history
- the latest scan produced alertworthy findings
- there are actually new findings compared to the previous scan

### Pipeline appears slow

SpiderFoot scans can take several minutes depending on the target and enabled modules.

### Windows batch issues

Use the launcher with the virtualenv Python directly, as configured in `run_soc.bat`.

---

## 🗺️ Roadmap

### v1.3

Planned focus areas:

- Event-driven SOC logging
- Stronger persistence model for alert history
- Per-target timeout isolation
- Metrics and observability improvements

### Future

- FastAPI service
- Web dashboard
- Docker support
- Cloud deployment

---

## 📌 Status

✅ Stable v1.2 release candidate  
🚧 v1.3 planned

---

## 👨‍💻 Author

Developed by **Fill "Filipe Maschio"**