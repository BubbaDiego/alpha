# 📡 XCom Core Specification

> Version: `v1.0`
> Author: `CoreOps 🥷`
> Scope: Notification system for email, SMS, voice and sound alerts.

---

## 📂 Module Structure
```txt
xcom/
├── xcom_core.py                   # 🚦 Dispatches notifications
├── xcom_config_service.py         # ⚙️ Loads provider settings
├── email_service.py               # 📧 SMTP email sender
├── sms_service.py                 # 💬 SMS via carrier gateway
├── voice_service.py               # 📞 Twilio voice calls
├── sound_service.py               # 🔊 Local audio playback
└── check_twilio_heartbeat_service.py  # ❤️ Twilio credential check
```

### 🔧 `XComCore`
Central orchestrator that sends notifications using configured providers.

```python
XComCore(dl_sys_data_manager)
```
- Initializes `XComConfigService` with a DataLocker system manager.
- Maintains an in-memory log of dispatched messages.

**send_notification**
```python
send_notification(level, subject, body, recipient="", initiator="system") -> dict
```
- Retrieves provider configs (`email`, `sms`, `api`).
- Based on `level` dispatches to `SMSService`, `VoiceService`, `EmailService` and
  optionally plays a sound.
- Results and errors are logged and written to the `xcom_monitor` ledger.

### 🛠️ Support Services
- **EmailService** – sends plaintext mail through an SMTP server.
- **SMSService** – uses EmailService to deliver SMS messages via a carrier gateway.
- **VoiceService** – wraps Twilio's client to place a voice call that reads the
  supplied message.
- **SoundService** – plays an MP3 file on the local system as an audible alert.
- **CheckTwilioHeartbeatService** – validates Twilio credentials and can trigger
  a test call in non-dry-run mode.

### 🧰 Configuration
`XComConfigService` resolves provider settings from the database or environment
variables. Placeholders like `${SMTP_SERVER}` fall back to corresponding
environment variables. The service returns merged dictionaries for each provider
so that `XComCore` has immediate access to required credentials such as
`SMTP_*` and `TWILIO_*` values.

### 🧩 Integrations
- `system_bp` exposes routes to update XCom settings and to send test messages.
- `XComMonitor` periodically calls `send_notification` as a heartbeat.
- `operations_console.py` uses XComCore for manual operations and testing.

### ✅ Design Notes
- Logging goes through `core.logging` with success or error emojis.
- Ledger writes include metadata like initiator, recipient and result status.
- The module keeps service classes small so other parts of the project can reuse
  them without pulling in the entire notification stack.
