from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

from backend.services.disaster_prediction.prediction_service import PredictionService
from backend.services.disaster_prediction.model_registry import registry

router = APIRouter(
    prefix="/api/predictions",
    tags=["predictions"],
)

class PredictionRequest(BaseModel):
    model_type: str
    features: Dict[str, Any]

class PredictionResponse(BaseModel):
    model_type: str
    prediction: str
    confidence: Optional[float]
    model_status: str
    timestamp: str

@router.post("/", response_model=PredictionResponse)
def get_prediction(request: PredictionRequest):
    model_type = request.model_type.lower()
    
    # Check model status
    status = registry.get_status(model_type)
    if status == "unknown":
        raise HTTPException(status_code=400, detail=f"Unknown model type: {model_type}")
    if status != "loaded":
        raise HTTPException(status_code=503, detail=f"Model {model_type} is {status}")
        
    try:
        pred_val, confidence = PredictionService.predict(model_type, request.features)
        
        return PredictionResponse(
            model_type=model_type,
            prediction=pred_val,
            confidence=confidence,
            model_status=status,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
