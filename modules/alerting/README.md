# 📡 Alerting Module

Handles sending alerts via Telegram.

---

## ⚙️ Features

- Retry mechanism
- Timeout handling
- Message truncation (Telegram limit)
- Error logging

---

## 🔁 Retry Strategy

- Max retries: 5
- Delay: 2 seconds

---

## 🔐 Environment Variables

```
TELEGRAM_TOKEN
TELEGRAM_CHAT_ID
```

---

## ▶️ Usage

```
from modules.alerting.alert_telegram import send_telegram_alert
```