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
- Windows (PowerShell recommended)

---

## 🚀 Setup

### 1. Clone repository

```
git clone https://github.com/filipe-maschio/BlueSentinel_SOC.git
cd BlueSentinel_SOC`
```

---

### 2. Create virtual environment

#### Windows

```
python -m venv venv
.\venv\Scripts\activate
```

#### Linux / Mac

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

## 🕷️ Install SpiderFoot (required)

```
git clone https://github.com/smicallef/spiderfoot.git external/spiderfoot
```

BlueSentinel uses a local SpiderFoot checkout under:

external/spiderfoot

---

## 🔐 Environment variables

Create the `.env` file from the example:

#### Windows

```
copy .env.example .env
notepad .env
```

#### Linux / Mac

```
cp .env.example .env
nano .env
```


Inside the `.env` file, you must configure your Telegram credentials:

```
TELEGRAM_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
```

### How to get these values

- **TELEGRAM_TOKEN** → create a bot via BotFather
- **TELEGRAM_CHAT_ID** → your personal chat ID or group ID

⚠️ This step is required — without it, alerts will not be sent.

---

## 🎯 Add targets

Create the targets file from the example:

#### Windows

```
copy config\targets_for_spiderfoot.example.txt config\targets_for_spiderfoot.txt
notepad config\targets_for_spiderfoot.txt
```

#### Linux / Mac

```
cp config/targets_for_spiderfoot.example.txt config/targets_for_spiderfoot.txt
nano config/targets_for_spiderfoot.txt
```


Add your targets (emails, usernames, domains, etc).

### Rules:

- One target per line
- No commas
- No extra characters
- No spaces before or after

### Example:

```
user@example.com
anotheruser@example.com
```

⚠️ Invalid formatting may break the pipeline.

---

## ▶️ Running

### Run full pipeline (recommended)

```
python -m modules.scheduler.scheduler
```

### Run via launcher (Windows)

```
run_soc.bat
```

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
│ ├── targets_for_spiderfoot.txt _(local, not versioned)_  
│ └── targets_for_spiderfoot.example.txt  
├── data/ _(generated at runtime)_  
│ ├── spiderfoot_outputs/  
│ │ └── _target_/  
│ │ └── scan_YYYYMMDD_HHMMSS.json  
│ └── alert_history.log  
├── infrastructure/  
│ ├── **init**.py  
│ └── logging.py  
├── logs/ _(generated at runtime)_  
│ ├── launcher.log  
│ ├── execution.log  
│ ├── soc.log  
│ └── error.log  
├── modules/  
│ ├── alerting/  
│ │ ├── **init**.py  
│ │ └── alert_telegram.py  
│ ├── detection_engine/  
│ │ ├── **init**.py  
│ │ ├── compare_by_target.py  
│ │ └── detection.py  
│ ├── osint_spiderfoot/  
│ │ ├── **init**.py  
│ │ └── spiderfoot_automation.py  
│ └── scheduler/  
│ └── scheduler.py  
├── shared/  
│ ├── **init**.py  
│ ├── config.py  
│ ├── constants.py  
│ ├── paths.py  
│ ├── platform_normalizer.py  
│ └── settings.py  
├── .env.example  
├── .gitignore  
├── requirements.txt  
└── run_soc.bat

(*) Files marked as local are not versioned and must be created during setup.

---

## 📜 Logs

- `launcher.log` → .bat execution
- `execution.log` → technical debug
- `soc.log` → operational pipeline
- `error.log` → errors

---

## 🚨 Detection behavior

### Initial baseline

First run → may generate INITIAL ALERT.

### Delta detection

Subsequent runs → only new findings.

### Deduplication

Stored in `alert_history.log`.

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

### SpiderFoot not found

```
git clone https://github.com/smicallef/spiderfoot.git external\spiderfoot
```

Check:

```
external\spiderfoot\sf.py
```

---

### No Telegram alerts

Check:

- `.env`
- token/chat_id
- alert history
- new findings

---

### Pipeline stuck

SpiderFoot scans can take several minutes.

---

## 🗺️ Roadmap

### v1.3

Planned focus areas:

- Event-driven SOC logging
- Per-target timeout
- Improved persistence
- Metrics / observability

### Future

- FastAPI service
- Web dashboard
- Docker support
- Cloud deployment

---

## 📌 Status

✅ **Stable v1.2 release**
🚧 v1.3 planned

---

## 👨‍💻 Author

Developed by **Fill "Filipe Maschio"**