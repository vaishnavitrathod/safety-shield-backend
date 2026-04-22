"""
analyzer.py
===========
Two-stage threat analysis pipeline:

Stage 1 — Fast regex pre-check (instant, no API cost)
Stage 2 — Claude AI deep analysis (called via Anthropic SDK)

If ANTHROPIC_API_KEY is not set, falls back to regex-only mode.
"""

import re
import os
import json
import anthropic

# ─────────────────────────────────────────────
#  REGEX PATTERNS  (Stage 1 — fast pre-check)
# ─────────────────────────────────────────────
THREAT_PATTERNS = [
    (r"send\s*(me\s*)?(some\s*)?(pics?|photos?|images?|nudes?|selfies?)", "grooming", 82),
    (r"don'?t\s*tell\s*(anyone|nobody|no\s*one)", "manipulation", 74),
    (r"keep\s*(this|it|us)\s*(secret|between\s*us)", "manipulation", 74),
    (r"no\s*one\s*(has\s*to\s*)?(needs\s*to\s*)?know", "manipulation", 74),
    (r"you\s*(can\s*)?trust\s*me", "manipulation", 65),
    (r"send\s*(me\s*)?(your\s*)?(address|location|number|phone)", "location_extraction", 80),
    (r"where\s*(do\s*)?(you\s*)?(live|stay|are\s*right\s*now)", "location_extraction", 78),
    (r"i\s*(will|'ll|gonna|am\s*going\s*to)\s*(hurt|kill|rape|harm|beat|slap|touch)\s*(you|her)", "physical_threat", 97),
    (r"i\s*know\s*where\s*you\s*(live|work|go\s*to\s*school)", "stalking", 88),
    (r"meet\s*(me|up)\s*(alone|in\s*person|secretly)", "grooming", 85),
    (r"how\s*old\s*are\s*you", "grooming", 68),
    (r"\b(help\s*me|save\s*me|sos|emergency|in\s*danger|being\s*(followed|attacked|harassed))\b", "sos_distress", 95),
    (r"(blackmail|i\s*have\s*your\s*(photos?|videos?)|i'?ll\s*(leak|share|post))", "blackmail", 92),
    (r"(stalk|follow(ing)?\s*(you|her)|watching\s*(you|her))", "stalking", 86),
    (r"\b(rape|molest|assault|kidnap|abduct)\b", "physical_threat", 97),
]

# Maps threat_type → human-readable categories
CATEGORIES = {
    "grooming": ["grooming", "child safety", "exploitation"],
    "manipulation": ["manipulation", "psychological abuse"],
    "location_extraction": ["location extraction", "privacy violation"],
    "physical_threat": ["physical threat", "violence"],
    "stalking": ["stalking", "surveillance"],
    "sos_distress": ["distress signal", "emergency"],
    "blackmail": ["blackmail", "coercion", "extortion"],
}


def regex_analyze(message: str) -> dict | None:
    """
    Run regex patterns against the message.
    Returns a result dict if matched, else None.
    """
    text = message.lower()
    best = None

    for pattern, threat_type, base_score in THREAT_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            if best is None or base_score > best["fake_score"]:
                best = {
                    "level": "HIGH" if base_score >= 80 else "MEDIUM",
                    "fake_score": base_score,
                    "threat_type": threat_type,
                    "reason": f"Message matches a known {threat_type.replace('_', ' ')} pattern.",
                    "categories": CATEGORIES.get(threat_type, [threat_type]),
                    "reasons": [f"Pattern matched: {threat_type.replace('_', ' ')}"],
                    "source": "regex",
                }

    return best


def ai_analyze(message: str, history: list) -> dict:
    """
    Send message + recent history to Claude for deep intent analysis.
    Returns normalised result dict.
    """
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    # Build conversation context string
    context = ""
    if history:
        recent = history[-4:]
        context = "\n".join(
            f"{'Stranger' if m.get('role') == 'user' else 'User'}: {m.get('content', '')}"
            for m in recent
        )
        context = f"\n\nConversation context (last {len(recent)} messages):\n{context}"

    prompt = f"""You are an AI safety engine protecting women and children from online threats.
Analyze the following message for threats: grooming, manipulation, physical threats, stalking, 
location extraction, blackmail, or distress signals.{context}

New message to analyze: "{message}"

Respond ONLY with valid JSON matching this exact schema (no markdown, no explanation):
{{
  "level": "HIGH" | "MEDIUM" | "LOW",
  "fake_score": <integer 0-100>,
  "threat_type": "grooming" | "manipulation" | "physical_threat" | "stalking" | "location_extraction" | "blackmail" | "sos_distress" | "none",
  "reason": "<one clear sentence explaining the verdict>",
  "categories": ["<tag1>", "<tag2>"],
  "reasons": ["<short reason 1>", "<short reason 2>"]
}}

Scoring guide:
- HIGH (80-100): Direct threats, grooming attempts, SOS signals, blackmail
- MEDIUM (50-79): Suspicious intent, isolation tactics, boundary-testing
- LOW (0-49): Safe or ambiguous — no clear threat"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    # Strip markdown fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    result = json.loads(raw)
    result["source"] = "ai"
    return result


def analyze_message(message: str, history: list = None) -> dict:
    """
    Main entry point.
    Runs Stage 1 (regex). If HIGH threat found, returns immediately.
    Otherwise runs Stage 2 (AI) if API key is available.
    Falls back gracefully to regex-only if AI is unavailable.
    """
    if history is None:
        history = []

    # Stage 1 — regex
    regex_result = regex_analyze(message)

    # Short-circuit on clear HIGH threat (no need to spend API tokens)
    if regex_result and regex_result["level"] == "HIGH":
        return regex_result

    # Stage 2 — AI (requires ANTHROPIC_API_KEY)
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        try:
            ai_result = ai_analyze(message, history)
            # If AI says safe but regex flagged medium, trust the regex
            if regex_result and ai_result.get("level") == "LOW":
                return regex_result
            return ai_result
        except Exception as e:
            print(f"[analyzer] AI analysis failed: {e}")
            # Fall through to regex result

    # Stage 1 only — return regex result or safe default
    if regex_result:
        return regex_result

    return {
        "level": "LOW",
        "fake_score": 10,
        "threat_type": "none",
        "reason": "No threat patterns detected in this message.",
        "categories": [],
        "reasons": [],
        "source": "regex",
    }
