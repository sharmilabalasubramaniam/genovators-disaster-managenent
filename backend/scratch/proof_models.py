import json
from backend.services.disaster_prediction.prediction_service import PredictionService
from backend.services.disaster_prediction.model_registry import registry

scenarios = {
    "cyclone": [
        {"name": "Normal/Low Risk", "features": {'wind_speed_kmh': 20, 'pressure_hpa': 1010, 'rainfall_mm': 5, 'temperature_c': 25, 'humidity_pct': 50, 'sea_surface_temp_c': 22, 'wind_gust_kmh': 25}},
        {"name": "High Risk", "features": {'wind_speed_kmh': 200, 'pressure_hpa': 950, 'rainfall_mm': 300, 'temperature_c': 28, 'humidity_pct': 90, 'sea_surface_temp_c': 29, 'wind_gust_kmh': 250}},
        {"name": "Different Valid", "features": {'wind_speed_kmh': 80, 'pressure_hpa': 990, 'rainfall_mm': 50, 'temperature_c': 26, 'humidity_pct': 70, 'sea_surface_temp_c': 26, 'wind_gust_kmh': 90}}
    ],
    "earthquake": [
        {"name": "Normal/Low Risk", "features": {'magnitude': 2.0, 'depth_km': 100, 'latitude': 0, 'longitude': 0, 'previous_earthquakes': 0, 'distance_fault_km': 500, 'ground_shaking': 0.01}},
        {"name": "High Risk", "features": {'magnitude': 8.5, 'depth_km': 10, 'latitude': 35, 'longitude': 140, 'previous_earthquakes': 5, 'distance_fault_km': 5, 'ground_shaking': 1.5}},
        {"name": "Different Valid", "features": {'magnitude': 5.5, 'depth_km': 50, 'latitude': 35, 'longitude': 140, 'previous_earthquakes': 2, 'distance_fault_km': 50, 'ground_shaking': 0.2}}
    ],
    "flood": [
        {"name": "Normal/Low Risk", "features": {'rainfall_mm': 5, 'river_level_m': 1, 'soil_moisture_pct': 30, 'humidity_pct': 40, 'temperature_c': 20, 'elevation_m': 100, 'historical_flood_count': 0}},
        {"name": "High Risk", "features": {'rainfall_mm': 400, 'river_level_m': 15, 'soil_moisture_pct': 95, 'humidity_pct': 90, 'temperature_c': 25, 'elevation_m': 5, 'historical_flood_count': 10}},
        {"name": "Different Valid", "features": {'rainfall_mm': 100, 'river_level_m': 5, 'soil_moisture_pct': 60, 'humidity_pct': 70, 'temperature_c': 22, 'elevation_m': 50, 'historical_flood_count': 2}}
    ],
    "landslide": [
        {"name": "Normal/Low Risk", "features": {'rainfall_mm': 5, 'slope_degree': 5, 'soil_moisture_pct': 20, 'elevation_m': 500, 'soil_stability': 0.9, 'vegetation_index': 0.8, 'previous_landslides': 0}},
        {"name": "High Risk", "features": {'rainfall_mm': 300, 'slope_degree': 60, 'soil_moisture_pct': 95, 'elevation_m': 2000, 'soil_stability': 0.1, 'vegetation_index': 0.1, 'previous_landslides': 5}},
        {"name": "Different Valid", "features": {'rainfall_mm': 100, 'slope_degree': 30, 'soil_moisture_pct': 50, 'elevation_m': 1000, 'soil_stability': 0.5, 'vegetation_index': 0.4, 'previous_landslides': 1}}
    ]
}

def run_tests():
    for model_type, tests in scenarios.items():
        print(f"================ {model_type.upper()} ====================")
        model = registry.get_model(model_type)
        print(f"Model framework/type: {type(model)}")
        for test in tests:
            print(f"\n--- {test['name']} ---")
            print(f"Input features: {test['features']}")
            pred, conf = PredictionService.predict(model_type, test['features'])
            print(f"Actual model.predict() output: {pred}")
            print(f"Confidence: {conf}")

if __name__ == "__main__":
    run_tests()
