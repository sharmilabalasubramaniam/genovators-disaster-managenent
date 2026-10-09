import urllib.request
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def fetch_weather(latitude: float, longitude: float):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            current = data.get("current_weather", {})
            return {
                "latitude": latitude,
                "longitude": longitude,
                "temperature": current.get("temperature", 0.0),
                "wind_speed": current.get("windspeed", 0.0),
                "wind_direction": current.get("winddirection", 0.0),
                "weather_code": current.get("weathercode", 0),
                "observation_time": current.get("time", "")
            }
    except Exception as e:
        logger.error(f"Open-Meteo API error: {e}")
        return None

def fetch_earthquakes(limit: int = 10):
    url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&limit={limit}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            events = []
            for feature in data.get("features", []):
                props = feature.get("properties", {})
                geom = feature.get("geometry", {})
                coords = geom.get("coordinates", [0.0, 0.0])
                
                # Timestamp is in milliseconds
                time_ms = props.get("time")
                dt = datetime.utcfromtimestamp(time_ms / 1000.0).isoformat() + "Z" if time_ms else ""
                
                events.append({
                    "magnitude": props.get("mag", 0.0),
                    "place": props.get("place", "Unknown"),
                    "timestamp": dt,
                    "longitude": coords[0] if len(coords) > 0 else 0.0,
                    "latitude": coords[1] if len(coords) > 1 else 0.0
                })
            return events
    except Exception as e:
        logger.error(f"USGS API error: {e}")
        return None
