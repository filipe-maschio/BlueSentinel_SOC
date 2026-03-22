# 🕷️ SpiderFoot Automation

Runs OSINT scans using SpiderFoot.

---

## ⚙️ Features

- Multi-target support
- Output per target
- Timestamped scans
- Timeout protection

---

## 📂 Output Structure

```
data/spiderfoot_outputs/<target>/
    scan_YYYYMMDD_HHMMSS.json
```

---

## ▶️ Run

```
python -m modules.osint_spiderfoot.spiderfoot_automation
```