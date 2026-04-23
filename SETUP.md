# Setup Guide

Complete step-by-step installation for OpenClaw + Twilio Voice.

## Prerequisites

- Linux server (Ubuntu 22.04+ recommended) or local machine
- Python 3.9+ installed
- Docker & Docker Compose
- A domain name (optional but recommended for SSL)

## Step 1: Set Up Ollama

Choose **Option A** (Self-hosted) or **Option B** (Ollama Cloud).

### Option A: Self-Hosted Ollama (Recommended)

Runs on your own hardware. Free, but requires sufficient RAM/CPU.

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model (llama3.2 works well for voice)
ollama pull llama3.2

# Verify it works
ollama run llama3.2 "Say hello"
```

### Option B: Ollama Cloud (Convenient)

Managed cloud service. Good for small VPS or when you don't want to run models locally.

1. Sign up at [ollama.com/cloud](https://ollama.com/cloud)
2. Generate an API key from your dashboard
3. Add the API key to your `.env` file (see Step 4)
4. No local Ollama installation needed

**When to use Ollama Cloud:**
- Small VPS (1GB RAM insufficient for local models)
- Want zero hardware management
- Testing or temporary setups

## Step 2: Install OpenClaw

```bash
# Clone OpenClaw repository
git clone https://github.com/openclaw-io/openclaw.git ~/openclaw
cd ~/openclaw

# Start with Docker Compose
docker-compose up -d

# Verify OpenClaw is running
curl http://localhost:8080/health
```

## Step 3: Configure Telegram Bot (Optional but Recommended)

```bash
# Create a bot with @BotFather on Telegram
# Save the token

# Edit OpenClaw config
cd ~/openclaw/config
cp config.example.yaml config.yaml
# Edit config.yaml with your bot token

# Restart OpenClaw
docker-compose restart
```

## Step 4: Install Webhook Server

```bash
# Clone this repo
git clone https://github.com/BobbyCodes-dev/openclaw-twilio-voice.git
cd openclaw-twilio-voice

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with your credentials
```

## Step 5: Set Up Twilio

See [docs/twilio-setup.md](docs/twilio-setup.md) for detailed instructions.

Quick summary:

1. Create account at [twilio.com](https://twilio.com)
2. Buy a phone number ($1/month)
3. Get your Account SID and Auth Token
4. Configure webhook URLs

## Step 6: Configure Environment

Edit `.env` with your actual values:

```bash
# Twilio
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+15551234567

# Ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# OpenClaw
OPENCLAW_URL=http://localhost:8080
OPENCLAW_SECRET=your_openclaw_secret_here

# Your server (for webhook URL)
PUBLIC_URL=https://your-domain-or-ip
```

## Step 7: Run the Server

```bash
# Start the webhook server
python src/webhook-server.py

# Or use a production server
uvicorn src.webhook-server:app --host 0.0.0.0 --port 8000
```

## Step 8: Configure Twilio Webhooks

1. Go to [Twilio Console](https://console.twilio.com)
2. Click your phone number
3. Under "Voice & Fax", set:
   - **A call comes in:** Webhook → `https://your-domain/twilio/voice`
   - **HTTP:** POST

## Step 9: Test the Setup

```bash
# Test webhook endpoint
curl -X POST https://your-domain/twilio/voice \
  -d "From=+15551234567" \
  -d "CallSid=test123"

# Make a test call
python examples/make-test-call.py
```

## Production Deployment

### Option A: Systemd Service

Create `/etc/systemd/system/twilio-webhook.service`:

```ini
[Unit]
Description=Twilio Webhook Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/openclaw-twilio-voice
Environment=PATH=/opt/openclaw-twilio-voice/venv/bin
ExecStart=/opt/openclaw-twilio-voice/venv/bin/uvicorn webhook-server:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable twilio-webhook
sudo systemctl start twilio-webhook
```

### Option B: Docker Deployment

```bash
docker build -t twilio-webhook .
docker run -d -p 8000:8000 --env-file .env twilio-webhook
```

### Option C: PM2 (Node.js style)

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.webhook-server:app --bind 0.0.0.0:8000
```

## SSL with Let's Encrypt (Recommended)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

Or use Cloudflare Tunnel for free SSL without port forwarding.

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand how it works
- Check [docs/troubleshooting.md](docs/troubleshooting.md) if issues arise
- Customize the voice prompts in `src/webhook-server.py`

## Updating

```bash
cd openclaw-twilio-voice
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart twilio-webhook
```
