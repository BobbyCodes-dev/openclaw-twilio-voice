#!/usr/bin/env python3
"""
OpenClaw + Twilio Voice Webhook Server
FastAPI server that handles Twilio voice webhooks and integrates with Ollama
"""

import os
import json
import logging
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import PlainTextResponse
import httpx

# Configuration from environment
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OPENCLAW_URL = os.getenv("OPENCLAW_URL", "")
OPENCLAW_SECRET = os.getenv("OPENCLAW_SECRET", "")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def query_ollama(prompt: str, system: Optional[str] = None) -> str:
    """Send a prompt to Ollama (local or cloud) and return the response."""
    
    # Determine if using Ollama Cloud (uses OpenAI-compatible API)
    is_cloud = "api.ollama.com" in OLLAMA_URL
    
    if is_cloud:
        # Ollama Cloud uses OpenAI-compatible chat completions API
        url = f"{OLLAMA_URL}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OLLAMA_API_KEY}",
            "Content-Type": "application/json"
        }
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": False
        }
    else:
        # Local Ollama uses native API
        url = f"{OLLAMA_URL}/api/generate"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
        if system:
            payload["system"] = system
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Parse response based on API type
            if is_cloud:
                return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            else:
                return data.get("response", "").strip()
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        return "I'm having trouble thinking right now. Please try again."


async def notify_openclaw(message: str):
    """Send a notification to OpenClaw (optional)."""
    if not OPENCLAW_URL:
        return
    
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{OPENCLAW_URL}/webhook/notify",
                json={"message": message, "secret": OPENCLAW_SECRET},
                timeout=5.0
            )
    except Exception as e:
        logger.warning(f"OpenClaw notification failed: {e}")


def create_twiml_response(message: str, gather: bool = False) -> str:
    """Create a TwiML response."""
    if gather:
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">{message}</Say>
    <Gather action="/twilio/gather" numDigits="1" timeout="5">
        <Say voice="alice">Press 1 to continue, or stay on the line.</Say>
    </Gather>
    <Redirect>/twilio/voice</Redirect>
</Response>
""".strip()
    else:
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">{message}</Say>
    <Pause length="1"/>
    <Say voice="alice">Goodbye!</Say>
    <Hangup/>
</Response>
""".strip()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for FastAPI."""
    logger.info(f"Starting webhook server")
    logger.info(f"Ollama URL: {OLLAMA_URL}")
    logger.info(f"Ollama Model: {OLLAMA_MODEL}")
    yield
    logger.info("Shutting down webhook server")


app = FastAPI(
    title="OpenClaw Twilio Voice",
    description="Webhook server for Twilio voice integration with Ollama",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "openclaw-twilio-voice"}


@app.post("/twilio/voice", response_class=PlainTextResponse)
async def handle_incoming_call(
    request: Request,
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    Direction: str = Form(default="inbound")
):
    """
    Handle incoming Twilio voice calls.
    Returns TwiML with AI-generated greeting.
    """
    logger.info(f"Incoming call: {CallSid} from {From} to {To}")
    
    # Notify OpenClaw (optional)
    await notify_openclaw(f"📞 Incoming call from {From}")
    
    # Create prompt for Ollama
    system_prompt = """You are a helpful AI assistant answering phone calls.
Be friendly, concise, and professional. Keep responses under 2 sentences.
You can only speak, not hear, so ask callers to press keys for input."""
    
    user_prompt = f"""Someone is calling from phone number {From}. 
Greet them warmly and ask how you can help today. 
Mention they can say keywords like 'help', 'sales', or 'info'."""
    
    # Get AI response
    ai_response = await query_ollama(user_prompt, system=system_prompt)
    
    # Create TwiML response
    twiml = create_twiml_response(ai_response, gather=True)
    
    return PlainTextResponse(
        content=twiml,
        media_type="application/xml"
    )


@app.post("/twilio/gather", response_class=PlainTextResponse)
async def handle_gather_input(
    request: Request,
    CallSid: str = Form(...),
    From: str = Form(...),
    Digits: Optional[str] = Form(default=None),
    SpeechResult: Optional[str] = Form(default=None)
):
    """
    Handle user input (digits or speech) from Twilio.
    """
    user_input = Digits or SpeechResult or ""
    logger.info(f"Input received: {user_input} from call {CallSid}")
    
    # Process the input with Ollama
    system_prompt = """You are a helpful AI assistant on a phone call.
Be friendly and concise. Respond naturally to the user's input.
Keep responses brief (1-2 sentences max for phone calls)."""
    
    user_prompt = f"""The caller said: '{user_input}'
Respond naturally. If they said 'help' or pressed 1, offer assistance.
If they said 'sales' or pressed 2, mention you'll connect them.
If they said 'bye' or 'goodbye', say goodbye and end the call."""
    
    ai_response = await query_ollama(user_prompt, system=system_prompt)
    
    # Check if we should end the call
    end_call = any(word in user_input.lower() for word in ["bye", "goodbye", "end", "quit", "hangup"])
    
    twiml = create_twiml_response(ai_response, gather=not end_call)
    
    return PlainTextResponse(
        content=twiml,
        media_type="application/xml"
    )


@app.post("/twilio/status")
async def handle_status_callback(
    CallSid: str = Form(...),
    CallStatus: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    Duration: Optional[str] = Form(default=None)
):
    """
    Handle Twilio call status callbacks.
    """
    logger.info(f"Call {CallSid} status: {CallStatus}, duration: {Duration}s")
    
    if CallStatus in ["completed", "busy", "failed", "no-answer", "canceled"]:
        await notify_openclaw(
            f"📞 Call ended: {CallStatus} | Duration: {Duration}s"
        )
    
    return {"status": "ok"}


@app.post("/twilio/recording")
async def handle_recording(
    CallSid: str = Form(...),
    RecordingUrl: str = Form(...),
    RecordingDuration: str = Form(...),
    From: str = Form(...)
):
    """
    Handle recorded voicemail.
    """
    logger.info(f"Recording received: {RecordingUrl} ({RecordingDuration}s)")
    
    await notify_openclaw(
        f"📺 Voicemail from {From}: {RecordingDuration}s - {RecordingUrl}"
    )
    
    return PlainTextResponse(
        content="<?xml version='1.0'?><Response><Hangup/></Response>",
        media_type="application/xml"
    )


@app.post("/make-call")
async def make_outbound_call(
    to_number: str,
    message: Optional[str] = None
):
    """
    Initiate an outbound call (requires Twilio credentials).
    """
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        raise HTTPException(500, "Twilio credentials not configured")
    
    # Generate message if not provided
    if not message:
        system_prompt = "You are making an outbound call. Be brief and friendly."
        user_prompt = "Create a short greeting for an outbound call checking in on a customer."
        message = await query_ollama(user_prompt, system=system_prompt)
    
    # Call Twilio API
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Calls.json"
    
    payload = {
        "To": to_number,
        "From": TWILIO_PHONE_NUMBER,
        "Url": f"{os.getenv('PUBLIC_URL', 'http://localhost:8000')}/twilio/outbound-handler?message={message}"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data=payload,
                auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            )
            response.raise_for_status()
            return {"status": "initiated", "call": response.json()}
    except Exception as e:
        logger.error(f"Failed to initiate call: {e}")
        raise HTTPException(500, f"Call failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
