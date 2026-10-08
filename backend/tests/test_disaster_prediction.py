import pytest
from backend.services.disaster_prediction.prediction_service import PredictionService
from backend.services.disaster_prediction.model_registry import registry
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_cyclone_prediction():
    features = {
        'wind_speed_kmh': 120,
        'pressure_hpa': 980,
        'rainfall_mm': 150,
        'temperature_c': 28,
        'humidity_pct': 85,
        'sea_surface_temp_c': 29,
        'wind_gust_kmh': 140
    }
    response = client.post("/api/predictions/", json={"model_type": "cyclone", "features": features})
    assert response.status_code == 200
    data = response.json()
    assert data["model_status"] == "loaded"
    assert "prediction" in data
    assert "confidence" in data

def test_missing_feature():
    features = {
        'wind_speed_kmh': 120,
        # missing 'pressure_hpa'
    }
    response = client.post("/api/predictions/", json={"model_type": "cyclone", "features": features})
    assert response.status_code == 422
    data = response.json()
    assert "Missing required features" in data["detail"]

def test_unknown_model():
    response = client.post("/api/predictions/", json={"model_type": "unknown", "features": {}})
    assert response.status_code == 400
    assert "Unknown model type" in response.json()["detail"]
