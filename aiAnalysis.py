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
    Analyze the Indian stock symbol '{symbol}' and provide a score (0-100) for the following categories:
    1. Customer Satisfaction (How happy are the customers with their products/services?)
    2. Moat Analysis (How strong is their competitive advantage or brand?)
    3. Tailwind Sector Score (Does the sector like AI, Green Energy, Defense, etc., have strong growth prospects?)
    4. Management Quality Score (Is the management honest, vision-driven, and shareholder-friendly?)

    Provide the output strictly in JSON format with the following keys:
    "customer_satisfaction": (integer),
    "moat": (integer),
    "tailwind": (integer),
    "management_quality": (integer),
    "notes": (string, detailed summary covering Moat, Customer Satisfaction, Tailwinds, and Management Quality)

    Be detailed in the 'notes' section. Mention specific competitive advantages, market sentiment, and sector outlook.
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
                    {"role": "system", "content": "You are a professional financial analyst specialized in Indian markets. Your analysis is thorough and data-driven."},
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
    # Expanded pre-calculated data with detailed notes
    knowledge_base = {
        "RELIANCE": {
            "customer_satisfaction": 90, "moat": 88, "tailwind": 92, "management_quality": 90,
            "notes": "MOAT: Unparalleled ecosystem dominance through Jio (data leadership) and Retail (physical footprint). Massive refining scale provides cost advantages. CUSTOMER SAT: High loyalty in Jio due to aggressive pricing and 5G rollout. TAILWINDS: Pivot to Green Hydrogen and Solar provides long-term growth; Retail growth in Tier-2/3 cities is a major driver. MGMT: Visionary leadership with a track record of successful capital allocation."
        },
        "TCS": {
            "customer_satisfaction": 92, "moat": 95, "tailwind": 88, "management_quality": 95,
            "notes": "MOAT: Gigantic switching costs for Fortune 500 clients; deep institutional memory. Brand association with Tata Group provides trust. CUSTOMER SAT: Consistent #1 ranking in European customer satisfaction surveys for IT services. TAILWINDS: Strong pipeline in Cloud migration and Enterprise AI (OpenAI partnership). MGMT: Conservative yet highly stable management with excellent capital return (dividends/buybacks)."
        },
        "INFY": {
            "customer_satisfaction": 82, "moat": 80, "tailwind": 85, "management_quality": 82,
            "notes": "MOAT: Strong digital transformation brand with proprietary tools like Finacle. Narrower moat than TCS due to higher attrition sensitivity. CUSTOMER SAT: Strong focus on CX/UX but faces tough competition. TAILWINDS: AI-first strategy is gaining momentum; 90% of top clients engaged in AI. MGMT: Technocratic leadership but has historically faced occasional internal friction."
        },
        "HDFCBANK": {
            "customer_satisfaction": 72, "moat": 94, "tailwind": 85, "management_quality": 88,
            "notes": "MOAT: Largest private bank network in India; low-cost CASA deposits. Post-merger synergy with HDFC Ltd allows massive cross-selling. CUSTOMER SAT: Mixed reviews due to legacy digital infrastructure issues, but remains the 'gold standard' for reliability in loans. TAILWINDS: India's credit growth story and increasing financialization of savings. MGMT: Proven execution but faces near-term pressure of integrating a massive merger."
        },
        "ICICIBANK": {
            "customer_satisfaction": 80, "moat": 92, "tailwind": 88, "management_quality": 90,
            "notes": "MOAT: Highly digitized retail lending platform (iMobile Pay). Strong capital adequacy and balanced risk portfolio. CUSTOMER SAT: Superior tech experience compared to peers; high 'Millennial' adoption. TAILWINDS: Strong retail credit demand and best-in-class asset quality. MGMT: Under Sandeep Bakhshi, management has transformed the culture into a highly risk-focused and performance-oriented machine."
        }
    }
    
    default_scores = {
        "customer_satisfaction": 70,
        "moat": 65,
        "tailwind": 75,
        "management_quality": 75,
        "notes": "MOAT: Moderate brand presence but faces sector competition. CUSTOMER SAT: Average market perception. TAILWINDS: Sector growth is stable but not disruptive. MGMT: Standard compliance and governance-led management."
    }
    
    return knowledge_base.get(symbol.upper(), default_scores)
    
    return knowledge_base.get(symbol.upper(), default_scores)
    
    return knowledge_base.get(symbol.upper(), default_scores)
