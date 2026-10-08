import difflib

def compare_age(age1, age2) -> float:
    if age1 is None or age2 is None:
        return None # Missing signal
    
    try:
        a1 = int(age1)
        a2 = int(age2)
    except ValueError:
        return None
        
    diff = abs(a1 - a2)
    if diff == 0:
        return 1.0
    elif diff <= 5:
        return 0.8
    elif diff <= 10:
        return 0.5
    elif diff <= 15:
        return 0.2
    else:
        return 0.0

def compare_gender(g1: str, g2: str) -> float:
    if not g1 or not g2 or g1 == "Unknown" or g2 == "Unknown":
        return None
        
    return 1.0 if g1.lower().strip() == g2.lower().strip() else 0.0

def compare_physical(desc1: str, desc2: str) -> float:
    if not desc1 or not desc2:
        return None
        
    d1 = desc1.lower()
    d2 = desc2.lower()
    
    return difflib.SequenceMatcher(None, d1, d2).ratio()
