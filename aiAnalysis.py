"""
aiAnalysis.py
--------------
Fetches qualitative scores (Moat, Customer Satisfaction, Tailwind, Management)
from the DeepSeek API for each stock symbol. Falls back to conservative defaults
when the API key is unavailable.

Environment:
    DEEPSEEK_API_KEY  –  Set in .env file at the project root.
"""

import json
import os

import requests

# Load .env manually (avoids requiring python-dotenv)
def _load_env(path: str = ".env") -> dict:
    env = {}
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, _, value = line.partition("=")
                    env[key.strip()] = value.strip()
    except FileNotFoundError:
        pass
    return env


_ENV = _load_env()
_API_KEY = _ENV.get("DEEPSEEK_API_KEY", "")

_SYSTEM_PROMPT = (
    "You are a cynical and extremely conservative hedge fund analyst. "
    "Your job is to find reasons NOT to buy a stock. "
    "You are stingy with praise and only award high scores to companies "
    "with unquestionable, objective market dominance."
)

_USER_PROMPT_TEMPLATE = """
Analyze the Indian stock '{symbol}' and score each category from 0 to 100.
Be brutally skeptical. High scores are rare.

RUBRIC:
  90–100  World-class monopoly (e.g., Google, Asian Paints)
  75–89   Dominant with clear competitive advantages
  50–74   Average, significant competition
  0–49    Weak, commoditized, or governance red flags

CATEGORIES:
  1. customer_satisfaction – Verified brand loyalty and repeat purchase behaviour
  2. moat – Structural barriers: network effects, switching costs, legal monopoly. Brand alone is NOT a moat.
  3. tailwind – Structural growth sector (AI, Defence, EV). Penalise over-hyped themes.
  4. management_quality – Capital allocation track record, promoter integrity, pledging level

Respond ONLY in valid JSON with exactly these keys:
{{"customer_satisfaction": int, "moat": int, "tailwind": int, "management_quality": int, "notes": string}}

The "notes" must cover all four dimensions concisely but critically.
"""

# Curated overrides for large well-known stocks
_KNOWLEDGE_BASE: dict[str, dict] = {
    "RELIANCE": {
        "customer_satisfaction": 80, "moat": 85, "tailwind": 85, "management_quality": 82,
        "notes": "Massive capital scale and vertical integration. Jio leads via network effects but faces regulatory risk. Retail is heavily competitive. Management structure is complex.",
    },
    "TCS": {
        "customer_satisfaction": 88, "moat": 90, "tailwind": 72, "management_quality": 92,
        "notes": "Deep switching costs and Tata brand trust. Best-in-class margins. IT growth slowing; AI disruption risk high. Gold standard governance.",
    },
    "HDFCBANK": {
        "customer_satisfaction": 65, "moat": 85, "tailwind": 80, "management_quality": 82,
        "notes": "Largest private deposit base. Post-merger integration risk with HDFC Ltd. Digital infrastructure lags peers. Solid track record but in a 'prove it' phase.",
    },
    "INFY": {
        "customer_satisfaction": 82, "moat": 80, "tailwind": 72, "management_quality": 85,
        "notes": "Strong client relationships and global delivery model. IT sector headwinds from AI and macro. Well-governed.",
    },
    "ASIANPAINT": {
        "customer_satisfaction": 92, "moat": 88, "tailwind": 68, "management_quality": 88,
        "notes": "Dominant brand loyalty, dealer network moat. Decorative paints market maturation limits tailwinds. Excellent capital allocators.",
    },
}

_DEFAULT_SCORES: dict = {
    "customer_satisfaction": 40,
    "moat": 35,
    "tailwind": 50,
    "management_quality": 45,
    "notes": (
        "No distinct moat identified. Operates in a commoditised, competitive market. "
        "Customer satisfaction is unremarkable. Management shows standard governance "
        "without a track record of exceptional capital allocation."
    ),
}


def get_ai_analysis(symbol: str) -> dict:
    """
    Returns qualitative scores for the given stock symbol.

    Tries DeepSeek API first, falls back to knowledge base or defaults.

    Returns:
        Dict with keys: customer_satisfaction, moat, tailwind, management_quality, notes.
    """
    # Hard-coded overrides take priority
    if symbol.upper() in _KNOWLEDGE_BASE:
        return _KNOWLEDGE_BASE[symbol.upper()]

    if not _API_KEY:
        print(f"  [AI] No API key – using defaults for {symbol}.")
        return dict(_DEFAULT_SCORES)

    try:
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {_API_KEY}",
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": _USER_PROMPT_TEMPLATE.format(symbol=symbol)},
                ],
                "response_format": {"type": "json_object"},
            },
            timeout=30,
        )

        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            return json.loads(content)

        print(f"  [AI] API error {response.status_code} for {symbol}. Using defaults.")
    except Exception as e:
        print(f"  [AI] Exception for {symbol}: {e}. Using defaults.")

    return dict(_DEFAULT_SCORES)
