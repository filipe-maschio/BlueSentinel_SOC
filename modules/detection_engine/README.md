# 🧠 Detection Engine

Responsible for identifying new exposures and generating alerts.

---

## 🔍 What it does

- Compares latest scan vs previous scan
- Extracts entities from SpiderFoot output
- Identifies new findings
- Classifies risk
- Filters already alerted items (deduplication)
- Sends alerts

---

## ⚙️ Flow

```
Load scans → Extract entities → Compare → Filter (dedup) → Classify → Alert
```

---

## 🧠 Risk Classification

|Type|Examples|Level|
|---|---|---|
|Critical|leak, breach, password, combo|HIGH|
|Exposure|account, profile|MEDIUM|
|Generic|others|LOW|

---

## 🚫 Deduplication Logic

Each alert is uniquely identified by:

```
target|item
```

Previously alerted items are ignored.

---

## 📂 Data Used

- `data/spiderfoot_outputs/`
- `data/alert_history.log`

---

## ▶️ Run

```
python -m modules.detection_engine.compare_by_target
```