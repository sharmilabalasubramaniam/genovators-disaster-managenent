import React, { useState } from 'react';
import api from '../services/api';

const MODEL_FEATURES = {
  cyclone: [
    { name: 'wind_speed_kmh', label: 'Wind Speed', units: 'km/h', min: 0, max: 400 },
    { name: 'pressure_hpa', label: 'Pressure', units: 'hPa', min: 850, max: 1100 },
    { name: 'rainfall_mm', label: 'Rainfall', units: 'mm', min: 0, max: 1500 },
    { name: 'temperature_c', label: 'Temperature', units: '°C', min: -50, max: 60 },
    { name: 'humidity_pct', label: 'Humidity', units: '%', min: 0, max: 100 },
    { name: 'sea_surface_temp_c', label: 'Sea Surface Temp', units: '°C', min: -5, max: 40 },
    { name: 'wind_gust_kmh', label: 'Wind Gust', units: 'km/h', min: 0, max: 500 }
  ],
  earthquake: [
    { name: 'magnitude', label: 'Magnitude', units: 'Richter', min: 0, max: 10 },
    { name: 'depth_km', label: 'Depth', units: 'km', min: 0, max: 800 },
    { name: 'latitude', label: 'Latitude', units: 'deg', min: -90, max: 90 },
    { name: 'longitude', label: 'Longitude', units: 'deg', min: -180, max: 180 },
    { name: 'previous_earthquakes', label: 'Previous Earthquakes', units: 'count', min: 0, max: 100 },
    { name: 'distance_fault_km', label: 'Distance to Fault', units: 'km', min: 0, max: 1000 },
    { name: 'ground_shaking', label: 'Ground Shaking (PGA)', units: 'g', min: 0, max: 5 }
  ],
  flood: [
    { name: 'rainfall_mm', label: 'Rainfall', units: 'mm', min: 0, max: 1500 },
    { name: 'river_level_m', label: 'River Level', units: 'm', min: 0, max: 50 },
    { name: 'soil_moisture_pct', label: 'Soil Moisture', units: '%', min: 0, max: 100 },
    { name: 'humidity_pct', label: 'Humidity', units: '%', min: 0, max: 100 },
    { name: 'temperature_c', label: 'Temperature', units: '°C', min: -50, max: 60 },
    { name: 'elevation_m', label: 'Elevation', units: 'm', min: -400, max: 9000 },
    { name: 'historical_flood_count', label: 'Historical Floods', units: 'count', min: 0, max: 100 }
  ],
  landslide: [
    { name: 'rainfall_mm', label: 'Rainfall', units: 'mm', min: 0, max: 1500 },
    { name: 'slope_degree', label: 'Slope Degree', units: '°', min: 0, max: 90 },
    { name: 'soil_moisture_pct', label: 'Soil Moisture', units: '%', min: 0, max: 100 },
    { name: 'elevation_m', label: 'Elevation', units: 'm', min: -400, max: 9000 },
    { name: 'soil_stability', label: 'Soil Stability Index', units: 'index', min: 0, max: 1 },
    { name: 'vegetation_index', label: 'Vegetation Index (NDVI)', units: 'index', min: -1, max: 1 },
    { name: 'previous_landslides', label: 'Previous Landslides', units: 'count', min: 0, max: 100 }
  ]
};

const DisasterPredictions = () => {
  const [modelType, setModelType] = useState('flood');
  const [inputs, setInputs] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const currentFeatures = MODEL_FEATURES[modelType];

  const handleInputChange = (e, featureName) => {
    setInputs({
      ...inputs,
      [featureName]: e.target.value
    });
  };

  const handleModelChange = (e) => {
    setModelType(e.target.value);
    setInputs({});
    setResult(null);
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Clean up and parse inputs
      const features = {};
      for (const feature of currentFeatures) {
        if (inputs[feature.name] === undefined || inputs[feature.name] === '') {
          throw new Error(`Please provide a value for ${feature.label}`);
        }
        features[feature.name] = parseFloat(inputs[feature.name]);
      }

      const res = await api.post('/api/predictions/', {
        model_type: modelType,
        features: features
      });
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Error fetching prediction');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Disaster Predictions</h1>
      <p className="mb-6 text-gray-600">Run actual ML model inference to get real risk predictions.</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <form onSubmit={handleSubmit}>
            <div className="mb-6">
              <label className="block text-sm font-bold text-gray-700 mb-2">DISASTER TYPE</label>
              <select 
                value={modelType} 
                onChange={handleModelChange}
                className="w-full border-gray-300 rounded-md shadow-sm p-2 border font-medium text-lg"
              >
                <option value="cyclone">Cyclone</option>
                <option value="earthquake">Earthquake</option>
                <option value="flood">Flood</option>
                <option value="landslide">Landslide</option>
              </select>
            </div>

            <h3 className="text-sm font-bold text-gray-700 mb-3 border-b pb-2">INPUT PARAMETERS</h3>
            <div className="space-y-4 mb-6">
              {currentFeatures.map(feature => (
                <div key={feature.name}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {feature.label} {feature.units && <span className="text-gray-500 font-normal">({feature.units})</span>}
                  </label>
                  <input
                    type="number"
                    step="any"
                    value={inputs[feature.name] || ''}
                    onChange={(e) => handleInputChange(e, feature.name)}
                    min={feature.min}
                    max={feature.max}
                    placeholder={`e.g. ${(feature.min + feature.max) / 2 || 0}`}
                    className="w-full border-gray-300 rounded-md shadow-sm p-2 border"
                  />
                </div>
              ))}
            </div>

            <button 
              type="submit" 
              disabled={loading}
              className="w-full bg-blue-600 text-white font-bold px-4 py-3 rounded-md hover:bg-blue-700 disabled:bg-blue-300 transition-colors"
            >
              {loading ? 'Running Prediction...' : 'RUN PREDICTION'}
            </button>
          </form>
        </div>

        <div>
          <h2 className="text-xl font-bold mb-4">RESULT</h2>
          
          {error && (
            <div className="p-4 bg-red-50 text-red-700 rounded-md border border-red-200">
              <h3 className="font-bold mb-1">Error</h3>
              <p>{error}</p>
            </div>
          )}

          {result && (
            <div className="p-6 bg-blue-50 text-blue-900 rounded-md border border-blue-200 shadow-sm">
              <div className="mb-4">
                <span className="block text-sm text-blue-700 font-bold mb-1 uppercase">Risk / Prediction</span>
                <span className="text-3xl font-black capitalize">{result.prediction}</span>
              </div>
              
              <div className="mb-4">
                <span className="block text-sm text-blue-700 font-bold mb-1 uppercase">Confidence</span>
                <span className="text-xl">
                  {result.confidence !== null && result.confidence !== undefined 
                    ? `${(result.confidence * 100).toFixed(1)}%` 
                    : 'Not available'}
                </span>
              </div>

              <div className="text-sm text-blue-800 space-y-1 pt-4 border-t border-blue-200">
                <p><span className="font-semibold">Model:</span> {result.model_type} Prediction Model</p>
                <p><span className="font-semibold">Model Status:</span> {result.model_status === 'loaded' ? 'Loaded Successfully' : result.model_status}</p>
                <p><span className="font-semibold">Timestamp:</span> {new Date(result.timestamp).toLocaleString()}</p>
              </div>
            </div>
          )}
          
          {!result && !error && !loading && (
            <div className="p-8 text-center text-gray-500 border-2 border-dashed border-gray-300 rounded-lg">
              Select a model and run prediction to see results.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DisasterPredictions;
