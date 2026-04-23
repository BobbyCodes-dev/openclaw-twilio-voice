# Pricing Breakdown

Honest cost analysis for running OpenClaw + Twilio Voice.

## TL;DR

| Setup | Monthly Cost |
|-------|--------------|
| **Local only** (no VPS) | ~$1-5 |
| **Small VPS** (1GB RAM) | ~$6-11 |
| **Recommended** (2GB VPS) | ~$11-20 |
| **High usage** (1000+ mins) | ~$30-50 |

## Detailed Costs

### 1. Ollama (LLM Engine)

**Option A: Self-Hosted (Recommended)**

**Cost: $0**

- Runs entirely on your hardware
- No API fees, no usage limits
- Requires GPU for larger models (optional)
- CPU-only works fine for smaller models (llama3.2, phi3)

**Option B: Ollama Cloud (Convenient)**

**Cost: ~$0.50-5/month** (light usage)

- Managed cloud service at [ollama.com/cloud](https://ollama.com/cloud)
- Usage-based pricing, cheaper than OpenAI API
- No hardware requirements, works on minimal VPS
- Same models available (llama3.2, etc.)
- Requires API key

| Usage Tier | Estimated Cost |
|------------|----------------|
| Light (~1K requests/month) | **~$0.50-2/month** |
| Medium (~10K requests/month) | **~$2-5/month** |
| Heavy (~100K+ requests/month) | **~$5-20/month** |

**When to use Ollama Cloud:**
- Running on a small VPS (1GB RAM)
- Don't want to manage local models
- Need quick setup without hardware requirements
- Temporary/testing deployments

### 2. OpenClaw

**Cost: $0 (Open Source)**

- Free to use, MIT licensed
- Self-hosted, no cloud dependencies
- Optional: Sponsor on GitHub if you want

### 3. Twilio

**Base Cost: ~$1/month**

| Item | Cost |
|------|------|
| Phone number | $1.00/month |
| Incoming calls | $0.0085/min |
| Outgoing calls | $0.013/min |
| Recording (optional) | $0.0025/min |
| Transcription (optional) | $0.05/min |

**Example scenarios:**

| Usage | Estimated Cost |
|-------|----------------|
| 50 min incoming/month | $1 + $0.43 = **$1.43** |
| 100 min outgoing/month | $1 + $1.30 = **$2.30** |
| 500 min mixed/month | $1 + $5.50 = **$6.50** |

### 4. Server/VPS (Optional but Recommended)

**Cost: $0-20/month**

| Provider | Specs | Monthly |
|----------|-------|---------|
| **Local** (your machine) | Your hardware | **$0** |
| **Raspberry Pi** | 4GB RAM | **$0** (one-time ~$75) |
| **Hetzner CX11** | 1 vCPU, 2GB RAM | **$4.51** |
| **DigitalOcean Basic** | 1 vCPU, 512MB RAM | **$4.00** |
| **Linode Nanode** | 1 vCPU, 1GB RAM | **$5.00** |
| **Vultr Cloud Compute** | 1 vCPU, 1GB RAM | **$5.00** |
| **AWS t3.micro** | 2 vCPU, 1GB RAM | **~$8.50** |
| **DigitalOcean General** | 1 vCPU, 2GB RAM | **$12.00** |

**Recommendation:** Hetzner or DigitalOcean for best price/performance.

## Total Cost Examples

### Scenario A: Local Setup (No VPS)

Running everything on a home server or Raspberry Pi:

- Ollama: $0 (your hardware)
- OpenClaw: $0
- Twilio: ~$2/month (phone + light usage)
- VPS: $0
- **Total: ~$2/month**

**Pros:** Free, full control
**Cons:** Needs port forwarding, dynamic IP issues, home bandwidth

### Scenario B: Minimal Cloud Setup

Small VPS for webhook server, Ollama on local machine:

- Ollama: $0 (local)
- OpenClaw: $0
- Twilio: ~$2/month
- VPS (1GB): $5/month
- **Total: ~$7/month**

### Scenario C: Full Cloud Setup (Recommended)

Everything on a 2GB VPS:

- Ollama: $0 (runs on VPS)
- OpenClaw: $0
- Twilio: ~$5/month (medium usage)
- VPS (2GB): $12/month
- **Total: ~$17/month**

### Scenario D: Business Usage

Heavy usage, always-on reliability:

- Ollama: $0
- OpenClaw: $0
- Twilio: ~$20/month (high volume)
- VPS (4GB): $24/month
- **Total: ~$44/month**

## Cost Comparison: Alternatives

| Service | Monthly Cost | Notes |
|---------|--------------|-------|
| **This Setup** | $5-30 | Full control, no per-call AI fees |
| [Bland.ai](https://bland.ai) | ~$50-200 | $0.09/min, managed |
| [Vapi.ai](https://vapi.ai) | ~$50-150 | Per-minute pricing |
| [Retell.ai](https://retell.ai) | ~$30-100 | Per-minute pricing |
| Twilio + OpenAI | ~$50-300 | GPT-4 + voice = $$$ |
| Google Dialogflow | ~$20-100 | Per-request pricing |
| AWS Connect | ~$30-200 | Complex pricing tiers |

**Why this setup wins:**
- No per-minute AI fees (Ollama is free)
- No vendor lock-in
- Can run entirely offline
- Scales with your hardware, not your wallet

## Money-Saving Tips

1. **Start local** — Test everything before paying for VPS
2. **Use Cloudflare Tunnel** — Free SSL, no port forwarding
3. **Monitor Twilio usage** — Set up billing alerts
4. **Choose small models** — llama3.2 (3B) vs llama3 (70B) = same voice quality, less RAM
5. **Use prepaid Twilio** — Avoid surprise bills

## Free Tier Options

If you're broke but motivated:

| Component | Free Alternative |
|-----------|------------------|
| Server | Raspberry Pi or old laptop |
| Domain | DuckDNS or Cloudflare |
| SSL | Let's Encrypt (always free) |
| Tunnel | Cloudflare Tunnel (free) |
| Monitoring | UptimeRobot (free tier) |
| **Total** | **$1/month** (Twilio number only) |

## Billing Alerts

Set up Twilio billing alerts to avoid surprises:

1. Go to [Twilio Console → Billing](https://console.twilio.com)
2. Set up "Usage Triggers"
3. Alert at $5, $10, $25 usage

## Questions?

Open an issue if you find cheaper alternatives or have cost optimization ideas.
