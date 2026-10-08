import os
import joblib
import logging

logger = logging.getLogger(__name__)

class ModelRegistry:
    _instance = None
    _models = {}
    _model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "ml_models", "disaster_models_unzipped")
    
    _model_files = {
        "cyclone": "cyclone_model.joblib",
        "earthquake": "earthquake_model.joblib",
        "flood": "flood_model.joblib",
        "landslide": "landslide_model.joblib"
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.load_all_models()
        return cls._instance

    def load_all_models(self):
        for model_type, filename in self._model_files.items():
            path = os.path.join(self._model_dir, filename)
            try:
                if os.path.exists(path):
                    self._models[model_type] = joblib.load(path)
                    logger.info(f"Successfully loaded {model_type} model.")
                else:
                    logger.warning(f"Model file not found: {path}")
                    self._models[model_type] = None
            except Exception as e:
                logger.error(f"Error loading {model_type} model from {path}: {e}")
                self._models[model_type] = None

    def get_model(self, model_type: str):
        return self._models.get(model_type)

    def get_status(self, model_type: str) -> str:
        if model_type not in self._model_files:
            return "unknown"
        if self._models.get(model_type) is not None:
            return "loaded"
        return "unavailable"

registry = ModelRegistry()
