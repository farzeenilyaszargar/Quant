
def calculate_dcf(fcf, growth_rate=0.08, terminal_growth=0.015, discount_rate=0.18, years=10):
    """
    Stricter DCF calculation with growth decay.
    fcf: Current Free Cash Flow (Cr)
    growth_rate: Initial growth rate (capped at 25%)
    terminal_growth: Rate after projection (stricter 1.5%)
    discount_rate: Increased to 18% for conservative safety
    """
    if fcf <= 0:
        return 0
    
    # Cap excessive growth rates
    working_growth = min(0.25, growth_rate)
    decay_factor = 0.9  # Growth slows down by 10% every year
    
    projected_fcf = []
    current_fcf = fcf
    for i in range(1, years + 1):
        current_fcf *= (1 + working_growth)
        projected_fcf.append(current_fcf)
        working_growth *= decay_factor  # Step-down growth modeling
    
    # Discounted cash flows
    discounted_fcf = [val / (1 + discount_rate)**(i+1) for i, val in enumerate(projected_fcf)]
    
    # Terminal Value
    terminal_value = (projected_fcf[-1] * (1 + terminal_growth)) / (discount_rate - terminal_growth)
    discounted_terminal_value = terminal_value / (1 + discount_rate)**years
    
    intrinsic_value = sum(discounted_fcf) + discounted_terminal_value
    return intrinsic_value

def calculate_weighted_score(metrics):
    """
    w = 0.3 * DCF Score + 0.2 * CAGR Revenue Growth & Profit Score + 0.1 * ROCE + 
        0.15 * Customer Satisfaction & MOAT Analysis + 0.05 * DII & FII Activity & D/E + 
        0.1 * Tailwind Sectors + 0.1 * Management Quality Score
    """
    # Assuming metrics contains scores from 0-100 for each category
    dcf_score = metrics.get('dcf_score', 0)
    growth_score = metrics.get('growth_score', 0)
    roce_score = metrics.get('roce_score', 0)
    moat_score = metrics.get('moat_score', 0)
    fii_dii_de_score = metrics.get('fii_dii_de_score', 0)
    tailwind_score = metrics.get('tailwind_score', 0)
    management_score = metrics.get('management_score', 0)
    
    score = (
        0.3 * dcf_score + 
        0.2 * growth_score + 
        0.1 * roce_score + 
        0.15 * moat_score + 
        0.05 * fii_dii_de_score + 
        0.1 * tailwind_score +
        0.1 * management_score
    )
    return round(score, 2)
