# 🛡️ BlueSentinel SOC

Automated OSINT-based Security Monitoring System (Mini SOC)

---

## Overview

BlueSentinel SOC is an automated pipeline that:

- Collects OSINT data using SpiderFoot;
- Detects new exposures over time;
- Classifies risk levels (HIGH / MEDIUM / LOW);
- Sends alerts via Telegram;
- Runs automatically via scheduler.

---

## Architecture

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

## Features

- Continuous OSINT monitoring;
- Risk classification engine;
- Telegram alerting with retry;
- Deduplication (no alert spam);
- Historical scan tracking;
- Automated scheduling.

---

## Project Structure

```
modules/
 ├── osint_spiderfoot/
 ├── detection_engine/
 ├── alerting/
 └── scheduler/

data/
 ├── spiderfoot_outputs/
 └── alerts/

config/
 └── targets_for_spiderfoot.txt
```

---

## Setup

### 1. Clone repository

```
git clone <your-repo-url>
cd BlueSentinel_SOC
```

---

### 2. Create virtual environment

```
python -m venv venv
.\venv\Scripts\activate
```

---

### 3. Install dependencies

```
pip install -r requirements.txt
```

---

### 4. Configure environment variables

Create `.env`:

```
TELEGRAM_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
```

---

### 5. Add targets

Edit:

```
config/targets_for_spiderfoot.txt
```

Add one email address per line. Do not use commas or colons.

---

## Running

### Manual pipeline

```
python -m modules.osint_spiderfoot.spiderfoot_automation
python -m modules.detection_engine.compare_by_target
```

---

### Scheduler

```
python -m modules.scheduler.scheduler
```

---

## Roadmap

- OSINT collection;
- Detection engine;
- Risk classification;
- Telegram alerting;
- Deduplication system;
- Docker support;
- Dashboard;
- Cloud deployment.

---

## Status

Functional automated SOC pipeline.

---

## Author

Developed by **Fill "Filipe Maschio"**

If this project helped you, give it a star on GitHub ⭐