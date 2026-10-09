import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Loader2, Thermometer, Wind, Cloud, Navigation, AlertTriangle, MapPin, Clock } from 'lucide-react';

export default function DisasterPulse() {
  const [weather, setWeather] = useState(null);
  const [earthquakes, setEarthquakes] = useState(null);
  const [loadingWeather, setLoadingWeather] = useState(false);
  const [loadingEq, setLoadingEq] = useState(false);
  const [weatherError, setWeatherError] = useState(null);
  const [eqError, setEqError] = useState(null);
  
  // Defaulting to Coimbatore, India
  const [lat, setLat] = useState("11.0168");
  const [lon, setLon] = useState("76.9558");

  const fetchWeather = async () => {
    setLoadingWeather(true);
    setWeatherError(null);
    try {
      const res = await api.get(`/external/weather?latitude=${lat}&longitude=${lon}`);
      if (res.data.error) {
        setWeatherError(res.data.error);
      } else {
        setWeather(res.data);
      }
    } catch (err) {
      setWeatherError('Failed to fetch weather data.');
    }
    setLoadingWeather(false);
  };

  const fetchEarthquakes = async () => {
    setLoadingEq(true);
    setEqError(null);
    try {
      const res = await api.get(`/external/earthquakes?limit=10`);
      if (res.data.error) {
        setEqError(res.data.error);
      } else {
        setEarthquakes(res.data);
      }
    } catch (err) {
      setEqError('Failed to fetch earthquake data.');
    }
    setLoadingEq(false);
  };

  useEffect(() => {
    fetchWeather();
    fetchEarthquakes();
  }, []);

  const handleFetchWeather = (e) => {
    e.preventDefault();
    fetchWeather();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Real-Time Disaster Pulse</h1>
      </div>
      <p className="text-gray-600">Live situational awareness using verified external sources.</p>

      {/* Location Input Form */}
      <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
        <h3 className="font-semibold text-lg mb-2">Location Query</h3>
        <form onSubmit={handleFetchWeather} className="flex gap-4 items-end">
          <div>
            <label className="block text-sm text-gray-700">Latitude</label>
            <input type="number" step="any" value={lat} onChange={(e) => setLat(e.target.value)} className="mt-1 p-2 border rounded" required />
          </div>
          <div>
            <label className="block text-sm text-gray-700">Longitude</label>
            <input type="number" step="any" value={lon} onChange={(e) => setLon(e.target.value)} className="mt-1 p-2 border rounded" required />
          </div>
          <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Update Weather</button>
        </form>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* LIVE WEATHER SECTION */}
        <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
          <div className="bg-blue-50 px-4 py-3 border-b flex justify-between items-center">
            <h2 className="font-semibold text-lg text-blue-900 flex items-center gap-2">
              <Cloud className="w-5 h-5" /> Live Weather
            </h2>
            <span className="text-xs font-bold px-2 py-1 bg-blue-200 text-blue-800 rounded uppercase">REAL EXTERNAL DATA: Open-Meteo</span>
          </div>
          <div className="p-6">
            {loadingWeather ? (
              <div className="flex items-center justify-center h-32"><Loader2 className="w-8 h-8 animate-spin text-blue-500" /></div>
            ) : weatherError ? (
              <div className="text-red-500 bg-red-50 p-3 rounded">{weatherError}</div>
            ) : weather ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-50 p-3 rounded-lg flex items-center gap-3">
                    <Thermometer className="w-6 h-6 text-orange-500" />
                    <div>
                      <p className="text-sm text-gray-500">Temperature</p>
                      <p className="text-xl font-bold">{weather.temperature}°C</p>
                    </div>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-lg flex items-center gap-3">
                    <Wind className="w-6 h-6 text-blue-500" />
                    <div>
                      <p className="text-sm text-gray-500">Wind Speed</p>
                      <p className="text-xl font-bold">{weather.wind_speed} km/h</p>
                    </div>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-lg flex items-center gap-3">
                    <Navigation className="w-6 h-6 text-indigo-500" />
                    <div>
                      <p className="text-sm text-gray-500">Wind Direction</p>
                      <p className="text-xl font-bold">{weather.wind_direction}°</p>
                    </div>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-lg flex items-center gap-3">
                    <Cloud className="w-6 h-6 text-gray-500" />
                    <div>
                      <p className="text-sm text-gray-500">Weather Code</p>
                      <p className="text-xl font-bold">{weather.weather_code}</p>
                    </div>
                  </div>
                </div>
                <div className="text-xs text-gray-400 mt-4 flex items-center gap-1">
                  <Clock className="w-4 h-4" /> Observed: {new Date(weather.observation_time).toLocaleString()}
                </div>
              </div>
            ) : null}
          </div>
        </div>

        {/* RECENT EARTHQUAKES SECTION */}
        <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
          <div className="bg-red-50 px-4 py-3 border-b flex justify-between items-center">
            <h2 className="font-semibold text-lg text-red-900 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" /> Recent Earthquakes
            </h2>
            <span className="text-xs font-bold px-2 py-1 bg-red-200 text-red-800 rounded uppercase">REAL EXTERNAL DATA: USGS</span>
          </div>
          <div className="p-0">
            {loadingEq ? (
              <div className="flex items-center justify-center h-32"><Loader2 className="w-8 h-8 animate-spin text-red-500" /></div>
            ) : eqError ? (
              <div className="m-6 text-red-500 bg-red-50 p-3 rounded">{eqError}</div>
            ) : earthquakes?.events?.length > 0 ? (
              <ul className="divide-y divide-gray-200">
                {earthquakes.events.map((eq, i) => (
                  <li key={i} className="p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-semibold text-gray-900 flex items-center gap-2">
                          <MapPin className="w-4 h-4 text-gray-500" /> {eq.place}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">{new Date(eq.timestamp).toLocaleString()}</p>
                      </div>
                      <div className="flex flex-col items-end">
                        <span className={`px-2 py-1 rounded text-sm font-bold ${eq.magnitude > 4 ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'}`}>
                          M {eq.magnitude.toFixed(1)}
                        </span>
                        <span className="text-xs text-gray-400 mt-1">{eq.latitude.toFixed(2)}, {eq.longitude.toFixed(2)}</span>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="m-6 text-gray-500">No recent earthquakes found.</div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
