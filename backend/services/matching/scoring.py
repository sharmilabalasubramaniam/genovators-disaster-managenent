MATCH_WEIGHTS = {
    "name": 0.25,
    "age": 0.15,
    "gender": 0.05,
    "location": 0.15,
    "time": 0.10,
    "physical": 0.10,
    "face": 0.20
}

def calculate_confidence(score: float) -> str:
    s = score * 100
    if s < 40:
        return "LOW"
    elif s < 70:
        return "POSSIBLE"
    elif s < 85:
        return "STRONG"
    else:
        return "HIGH"

def calculate_weighted_score(signals: dict) -> float:
    total_weight = 0.0
    total_score = 0.0
    
    for key, weight in MATCH_WEIGHTS.items():
        if key in signals and signals[key] is not None:
            total_weight += weight
            total_score += signals[key] * weight
            
    if total_weight == 0:
        return 0.0
        
    # Normalize score based on available signals
    return total_score / total_weight
