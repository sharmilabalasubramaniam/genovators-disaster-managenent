import difflib

def compare_names(name1: str, name2: str) -> float:
    if not name1 or not name2:
        return 0.0
    
    n1 = name1.lower().strip()
    n2 = name2.lower().strip()
    
    # Exact match
    if n1 == n2:
        return 1.0
        
    # Check if one is contained in another (e.g. "Arjun" in "Arjun Kumar")
    if n1 in n2 or n2 in n1:
        # Boost score slightly if there's a strong containment
        base_score = difflib.SequenceMatcher(None, n1, n2).ratio()
        return min(base_score + 0.2, 1.0)
        
    return difflib.SequenceMatcher(None, n1, n2).ratio()
