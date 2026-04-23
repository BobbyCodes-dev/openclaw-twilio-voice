# Architecture

How OpenClaw + Twilio Voice works under the hood.

## High-Level Flow

```
┌────────────────────────────────────────────────────────────────────┐
│  INCOMING CALL                                           │
└───────────────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────────────┐
│  TWILIO (Phone Network)                                  │
│  • Receives PSTN call                                    │
│  • Converts to webhook                                   │
│  • Handles voice stream                                  │
└───────────────────────────────────────────────────────────────────┘
         │
         ▼ HTTP POST
┌────────────────────────────────────────────────────────────────────┐
│  WEBHOOK SERVER (FastAPI)                                │
│  • Receives Twilio request                               │
│  • Extracts caller info                                  │
│  • Queries Ollama for response                           │
│  • Generates TwiML                                       │
└───────────────────────────────────────────────────────────────────┘
         │
         ▼ HTTP
┌────────────────────────────────────────────────────────────────────┐
│  OLLAMA (LLM Server)                                     │
│  • Runs llama3.2, phi3, or similar                       │
│  • Processes natural language                            │
│  • Returns text response                                 │
└───────────────────────────────────────────────────────────────────┘
         │
         ▼ HTTP (TwiML)
┌────────────────────────────────────────────────────────────────────┐
│  TWILIO ← Response                                       │
│  • Receives TwiML                                      │
│  • Converts to speech (TTS)                              │
│  • Plays to caller                                       │
└───────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Twilio (Voice Gateway)

**Role:** Bridge between PSTN (phone network) and your webhook

**Key Concepts:**
- **TwiML** — XML instructions for Twilio ("Say this", "Gather input", "Record")
- **Webhook** — HTTP endpoint Twilio calls when something happens
- **Call SID** — Unique identifier for each call

**Pricing:** $1/month for number + per-minute charges

### 2. Webhook Server (FastAPI)

**Role:** Receive requests, talk to Ollama, return TwiML

**Endpoints:**
```
POST /twilio/voice      → Handle incoming calls
POST /twilio/gather     → Process caller input
POST /twilio/status     → Call status callbacks
POST /twilio/recording  → Handle recordings
```

**Processing Flow:**
1. Receive webhook from Twilio
2. Extract caller ID, call SID, input
3. Build prompt for Ollama
4. Send request to Ollama API
5. Receive AI response
6. Format as TwiML
7. Return to Twilio

### 3. Ollama (LLM Engine)

**Role:** Generate AI responses

**API:**
```bash
POST http://localhost:11434/api/generate
{
  "model": "llama3.2",
  "prompt": "User said: 'Hello'. Respond naturally.",
  "stream": false
}
```

**Models:**
| Model | Size | Quality | Speed |
|-------|------|---------|-------|
| llama3.2 | 3B | Good | Fast |
| phi3 | 3.8B | Good | Fast |
| llama3.1 | 8B | Better | Medium |
| llama3 | 70B | Best | Slow |

### 4. OpenClaw (Optional Integration)

**Role:** Telegram alerts, session management

**Integration:**
```python
# Send Telegram alert when call comes in
await notify_openclaw(
    message=f"📞 Incoming call from {caller}"
)
```

## Data Flow (Detailed)

### Incoming Call

```
1. Caller dials +15551234567
2. Twilio receives call
3. Twilio POSTs to /twilio/voice:
   {
     "CallSid": "CAxx...",
     "From": "+15559998888",
     "To": "+15551234567",
     "Direction": "inbound"
   }
4. Server queries Ollama:
   POST /api/generate
   { "prompt": "Someone called. What do you say?" }
5. Ollama returns: "Hello! How can I help you today?"
6. Server returns TwiML:
   <?xml version="1.0"?>
   <Response>
     <Say>Hello! How can I help you today?</Say>
   </Response>
7. Twilio speaks the response
```

### Outbound Call

```
1. Your app POSTs to Twilio /Calls.json
2. Twilio dials the number
3. When answered, Twilio hits your webhook
4. Same flow as incoming (steps 3-7)
```

## Security Considerations

### Authentication

**Twilio Webhook Validation:**
```python
from twilio.request_validator import RequestValidator

validator = RequestValidator(TWILIO_AUTH_TOKEN)
is_valid = validator.validate(
    url, request.form, request.headers.get('X-Twilio-Signature')
)
```

**Rate Limiting:**
```python
from slowapi import Limiter

limiter = Limiter(key_func=lambda: request.form.get('From'))
```

### Network

**Recommended Setup:**
- Webhook server behind HTTPS (Let's Encrypt or Cloudflare)
- Ollama on localhost or private network only
- Firewall: Port 8000 (webhook) and 11434 (Ollama, if remote)
- No credentials in URL/query params

### Environment

```bash
# .env — Never commit this!
TWILIO_AUTH_TOKEN=secret
OPENCLAW_SECRET=secret
OLLAMA_URL=http://localhost:11434  # Localhost = safe
```

## TwiML Reference

Common TwiML verbs:

```xml
<!-- Speak text -->
<Say voice="alice">Hello, world!</Say>

<!-- Collect digits -->
<Gather action="/handle-input" numDigits="1">
  <Say>Press 1 for sales, 2 for support</Say>
</Gather>

<!-- Redirect to another handler -->
<Redirect>/next-step</Redirect>

<!-- Record audio -->
<Record action="/handle-recording" maxLength="60"/>

<!-- Pause -->
<Pause length="2"/>

<!-- Hang up -->
<Hangup/>
```

## Scaling Considerations

### Single User / Home Setup

- Raspberry Pi 4 (4GB) works fine
- SQLite for call logs
- Local Ollama with small models
- Cloudflare Tunnel for public access

### Small Business

- 2GB VPS recommended
- PostgreSQL for call logs
- Ollama on same server or GPU box
- Let's Encrypt SSL

### High Volume

- Multiple webhook servers behind load balancer
- Separate Ollama inference cluster
- Redis for session state
- CDN for static assets

## Monitoring

Key metrics to track:

| Metric | How to Monitor |
|--------|----------------|
| Call volume | Twilio dashboard |
| Response time | Server logs |
| Ollama latency | Built-in metrics |
| Error rate | Log aggregation |
| Cost | Twilio billing alerts |

## Troubleshooting Architecture

**Problem: Calls fail immediately**
→ Check webhook URL is publicly accessible
→ Verify SSL certificate
→ Check Twilio webhook config

**Problem: Long silence before response**
→ Ollama response time too slow
→ Solution: Use smaller model or add caching

**Problem: "Application error" from Twilio**
→ Server crashed or returned invalid TwiML
→ Check server logs

**Problem: Calls connect but hang up**
→ TwiML syntax error
→ Content-Type header wrong (must be text/xml)
