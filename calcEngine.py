
def calculate_dcf(fcf, growth_rate=0.08, terminal_growth=0.02, discount_rate=0.15, years=7):
    """
    Simple DCF calculation.
    fcf: Current Free Cash Flow (Cr)
    growth_rate: Expected annual growth rate for the next 'years'
    terminal_growth: Rate at which company grows after 'years'
    discount_rate: WACC or desired return
    """
    if fcf <= 0:
        return 0
    
    projected_fcf = []
    for i in range(1, years + 1):
        projected_fcf.append(fcf * (1 + growth_rate)**i)
    
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
