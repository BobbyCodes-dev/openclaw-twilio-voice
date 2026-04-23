# OpenClaw + Twilio Voice

> Turn your AI assistant into a voice-enabled system that can make and receive phone calls.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What This Does

This setup combines:
- **OpenClaw** — Open-source AI assistant framework
- **Twilio** — Voice/SMS API for phone calls
- **Ollama** — Self-hosted LLM (runs locally) or Ollama Cloud (managed)

Your AI assistant can:
- ✅ Receive incoming calls and respond intelligently
- ✅ Make outbound calls with scripted or dynamic content
- ✅ Handle voice conversations using any Ollama model
- ✅ Integrate with your existing workflows (Telegram, n8n, etc.)

## Who It's For

- **Solopreneurs** — Add phone presence without hiring
- **Small businesses** — Automate appointment reminders, FAQs
- **Developers** — Build voice-enabled AI tools
- **Homelab enthusiasts** — Self-hosted voice AI on your hardware

## Quick Start

```bash
# 1. Clone this repo
git clone https://github.com/BobbyCodes-dev/openclaw-twilio-voice.git
cd openclaw-twilio-voice

# 2. Copy environment template
cp .env.example .env
# Edit .env with your credentials

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the webhook server
python src/webhook-server.py

# 5. Configure Twilio webhook URL
# Point your Twilio number to: https://your-server/twilio/voice
```

## Architecture Overview

```
Incoming Call → Twilio → Your Webhook → OpenClaw → Ollama → Voice Response
                                    ↓
                              Telegram Bot (alerts/logs)
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed diagrams.

## Documentation

| File | Purpose |
|------|---------|
| [SETUP.md](SETUP.md) | Complete installation guide |
| [PRICING.md](PRICING.md) | Cost breakdown & alternatives |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical deep-dive |
| [docs/twilio-setup.md](docs/twilio-setup.md) | Twilio account setup |
| [docs/openclaw-config.md](docs/openclaw-config.md) | OpenClaw configuration |
| [docs/troubleshooting.md](docs/troubleshooting.md) | Common issues & fixes |

## Example Usage

```python
from twilio.rest import Client

# Make an outbound AI call
client = Client(TWILIO_SID, TWILIO_TOKEN)
call = client.calls.create(
    to="+15551234567",
    from_=TWILIO_PHONE,
    url="https://your-server/twilio/outbound"
)
```

## Cost

Realistic monthly cost: **$5-30**

- Ollama (self-hosted): $0
- OpenClaw: Free/open source
- Twilio: ~$1/month + $0.013/min for calls
- VPS: $5-20/month (optional)

See [PRICING.md](PRICING.md) for full breakdown.

## Requirements

- Linux server or local machine
- Python 3.9+
- Docker (for OpenClaw)
- Twilio account
- Ollama installed

## Support

- Open an issue for bugs or questions
- Check [docs/troubleshooting.md](docs/troubleshooting.md) first

## License

MIT — See [LICENSE](LICENSE)
