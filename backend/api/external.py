from fastapi import APIRouter, HTTPException, Query
from typing import Union
from backend.schemas.external import WeatherData, EarthquakeData, ErrorResponse
from backend.services.external_data_service import fetch_weather, fetch_earthquakes

router = APIRouter(prefix="/api/external", tags=["external"])

@router.get("/weather", response_model=Union[WeatherData, ErrorResponse])
def get_weather(latitude: float = Query(...), longitude: float = Query(...)):
    data = fetch_weather(latitude, longitude)
    if not data:
        return {"source": "Open-Meteo", "error": "Failed to fetch weather data or service unavailable"}
    return WeatherData(**data)

@router.get("/earthquakes", response_model=Union[EarthquakeData, ErrorResponse])
def get_earthquakes(limit: int = Query(10, le=100)):
    events = fetch_earthquakes(limit)
    if events is None:
        return {"source": "USGS", "error": "Failed to fetch earthquake data or service unavailable"}
    return EarthquakeData(events=events)
