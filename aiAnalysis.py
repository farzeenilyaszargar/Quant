import os
import json
import requests

def load_env():
    env_vars = {}
    try:
        with open(".env", "r") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    env_vars[key] = value
    except FileNotFoundError:
        pass
    return env_vars

ENV = load_env()
DEEPSEEK_API_KEY = ENV.get("DEEPSEEK_API_KEY", "")

def get_ai_analysis(symbol):
    """
    Calls DeepSeek API to get qualitative scores for:
    - Customer Satisfaction
    - Moat Analysis
    - Tailwind Sector Score
    """
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "your_api_key_here":
        print(f"Warning: DeepSeek API key not set in .env. Using fallback for {symbol}.")
        return get_fallback_scores(symbol)

    prompt = f"""
    Analyze the Indian stock symbol '{symbol}' and provide a score (0-100) for the following categories. 
    YOU MUST BE EXTREMELY SKEPTICAL AND STINGY WITH HIGH SCORES. 
    
    SCORING RUBRIC:
    - 90-100: Reserved for generational, world-class monopolies (e.g., Google, Apple, or Asian Paints in India).
    - 75-89: Very strong, dominant players with clear competitive advantages.
    - 50-74: Average, standard businesses with significant competition.
    - Below 50: Weak players, commoditized businesses, or management with red flags.

    CATEGORIES:
    1. Customer Satisfaction (Actual verified happiness, brand loyalty, and recurring NPS)
    2. Moat Analysis (Strict barriers to entry: Network effects, high switching costs, or legal monopolies. Branding alone is NOT a moat.)
    3. Tailwind Sector Score (Structural growth trends: AI, Energy, Defense. Be critical of over-hyped sectors.)
    4. Management Quality Score (Check past transparency, capital allocation history, and promoter integrity. Penalize high promoter pledging.)

    Provide the output strictly in JSON format with the following keys:
    "customer_satisfaction": (integer),
    "moat": (integer),
    "tailwind": (integer),
    "management_quality": (integer),
    "notes": (string, detailed summary covering Moat, Customer Satisfaction, Tailwinds, and Management Quality)

    Be brutally honest and detailed in the 'notes' section.
    Only return the JSON.
    """

    try:
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are a cynical and extremely conservative hedge fund analyst. Your job is to find reasons NOT to buy a stock. You are stingy with praise and only give high qualitative scores to companies with unquestionable, objective dominance."},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            return json.loads(content)
        else:
            print(f"DeepSeek API Error: {response.status_code} - {response.text}")
            return get_fallback_scores(symbol)
            
    except Exception as e:
        print(f"AI Analysis Exception for {symbol}: {e}")
        return get_fallback_scores(symbol)

def get_fallback_scores(symbol):
    # Conservative pre-calculated data
    knowledge_base = {
        "RELIANCE": {
            "customer_satisfaction": 80, "moat": 85, "tailwind": 85, "management_quality": 82,
            "notes": "MOAT: Massive capital scale and vertical integration. Jio is a network-effect leader but faces tight regulation and RCom legacy issues. Retailing is competitive. MGMT: Visionary but highly complex holding structure."
        },
        "TCS": {
            "customer_satisfaction": 88, "moat": 90, "tailwind": 75, "management_quality": 92,
            "notes": "MOAT: Deep switching costs and high-trust 'Tata' brand. Best-in-class operational margins. TAILWINDS: IT sector growth is slowing; faces AI disruption risk. MGMT: Gold standard for governance."
        },
        "HDFCBANK": {
            "customer_satisfaction": 65, "moat": 85, "tailwind": 80, "management_quality": 82,
            "notes": "MOAT: Largest private deposit base. Post-merger integration is a huge operational risk. CUSTOMER SAT: Digital infrastructure remains a weak point; high friction in customer service. MGMT: Solid track record but currently in a 'prove it' phase post-merger."
        }
    }
    
    default_scores = {
        "customer_satisfaction": 40,
        "moat": 35,
        "tailwind": 50,
        "management_quality": 45,
        "notes": "MOAT: Weak or undefined. Operates in a crowded, commoditized market. CUSTOMER SAT: Unremarkable. MGMT: Standard compliance without significant alpha-driven vision. High potential for capital misallocation."
    }
    
    return knowledge_base.get(symbol.upper(), default_scores)
    
    return knowledge_base.get(symbol.upper(), default_scores)
    
    return knowledge_base.get(symbol.upper(), default_scores)
