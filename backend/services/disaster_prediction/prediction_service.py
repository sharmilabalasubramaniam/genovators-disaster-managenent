import numpy as np
from .model_registry import registry
import pandas as pd

class PredictionService:
    # Model required features based on our inspection
    REQUIRED_FEATURES = {
        "cyclone": ['wind_speed_kmh', 'pressure_hpa', 'rainfall_mm', 'temperature_c', 'humidity_pct', 'sea_surface_temp_c', 'wind_gust_kmh'],
        "earthquake": ['magnitude', 'depth_km', 'latitude', 'longitude', 'previous_earthquakes', 'distance_fault_km', 'ground_shaking'],
        "flood": ['rainfall_mm', 'river_level_m', 'soil_moisture_pct', 'humidity_pct', 'temperature_c', 'elevation_m', 'historical_flood_count'],
        "landslide": ['rainfall_mm', 'slope_degree', 'soil_moisture_pct', 'elevation_m', 'soil_stability', 'vegetation_index', 'previous_landslides']
    }

    @staticmethod
    def validate_inputs(model_type: str, features: dict):
        if model_type not in PredictionService.REQUIRED_FEATURES:
            raise ValueError(f"Unknown model type: {model_type}")
        
        required = PredictionService.REQUIRED_FEATURES[model_type]
        missing = [f for f in required if f not in features]
        if missing:
            raise ValueError(f"Missing required features for {model_type} model: {', '.join(missing)}")
            
        # Ensure all inputs are numeric
        try:
            for f in required:
                float(features[f])
        except (ValueError, TypeError):
            raise ValueError(f"All features must be numeric. Invalid value found in features.")

    @staticmethod
    def predict(model_type: str, features: dict):
        status = registry.get_status(model_type)
        if status != "loaded":
            raise RuntimeError(f"{model_type.capitalize()} model is {status}")
            
        PredictionService.validate_inputs(model_type, features)
        model = registry.get_model(model_type)
        
        # Prepare input preserving feature names to avoid sklearn warnings
        required = PredictionService.REQUIRED_FEATURES[model_type]
        input_data = {f: [float(features[f])] for f in required}
        df = pd.DataFrame(input_data)
        
        prediction = model.predict(df)[0]
        
        confidence = None
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(df)[0]
            confidence = float(np.max(proba))
            
        # Map prediction to string if it's numeric, or keep as string
        pred_str = str(prediction)
        # Just return what the model gave us
        return pred_str, confidence
