from datetime import datetime

def compare_time(time1: datetime, time2: datetime) -> float:
    if not time1 or not time2:
        return None
        
    diff = abs((time1 - time2).total_seconds())
    
    # Example logic:
    # Under 2 hours -> 1.0
    # Under 12 hours -> 0.8
    # Under 48 hours -> 0.5
    # Above -> 0.2
    hours = diff / 3600
    
    if hours <= 2:
        return 1.0
    elif hours <= 12:
        return 0.8
    elif hours <= 48:
        return 0.5
    else:
        return 0.2
