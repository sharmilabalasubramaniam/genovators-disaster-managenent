from pydantic import BaseModel, Field
from typing import List, Optional

class WeatherData(BaseModel):
    source: str = "Open-Meteo"
    data_type: str = "REAL_EXTERNAL_DATA"
    latitude: float
    longitude: float
    temperature: float
    wind_speed: float
    wind_direction: float
    weather_code: int
    observation_time: str

class EarthquakeEvent(BaseModel):
    magnitude: float
    place: str
    timestamp: str
    latitude: float
    longitude: float

class EarthquakeData(BaseModel):
    source: str = "USGS"
    data_type: str = "REAL_EXTERNAL_DATA"
    events: List[EarthquakeEvent]

class ErrorResponse(BaseModel):
    source: str
    error: str
