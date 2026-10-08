import difflib

def compare_location(loc1: str, loc2: str) -> float:
    if not loc1 or not loc2:
        return None
        
    l1 = loc1.lower().strip()
    l2 = loc2.lower().strip()
    
    if l1 == l2:
        return 1.0
        
    return difflib.SequenceMatcher(None, l1, l2).ratio()
