import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import MarkerClusterGroup from 'react-leaflet-cluster';
import 'leaflet/dist/leaflet.css';
import api from '../services/api';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import VoiceInput from '../components/VoiceInput';
import { ArrowLeft, MapPin, Clock, AlertTriangle, Search, Filter } from 'lucide-react';
import L from 'leaflet';

// Fix Leaflet's default icon path issues in React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const getMarkerColor = (type) => {
  switch (type?.toUpperCase()) {
    case 'LAST_SEEN':
    case 'LAST KNOWN':
      return 'red';
    case 'RESCUE':
      return 'orange';
    case 'HOSPITAL':
      return 'blue';
    case 'SHELTER':
    case 'CURRENT':
      return 'green';
    default:
      return 'gray';
  }
};

// Create custom colored markers
const createIcon = (color) => {
  return new L.Icon({
    iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color}.png`,
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  });
};

export default function MapView() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  let caseId = id || searchParams.get('caseId');
  if (caseId === 'undefined' || caseId === 'null') caseId = null;
  const navigate = useNavigate();
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('All'); // All, Missing, Identified, Reunited

  useEffect(() => {
    setLoading(true);
    const endpoint = caseId ? `/locations/case/${caseId}` : `/locations/`;
    api.get(endpoint)
      .then(res => {
        setLocations(caseId ? (res.data.locations || []) : res.data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.response?.data?.detail || err.message || "Failed to load locations");
        setLoading(false);
      });
  }, [caseId]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  const validLocations = locations.filter(loc => loc.latitude && loc.longitude);
  
  // Apply search and filters (only relevant for global map)
  const filteredLocations = validLocations.filter(loc => {
    if (caseId) return true;
    
    // Status filter
    if (filterStatus !== 'All') {
      if (filterStatus === 'Missing' && loc.status !== 'New' && loc.status !== 'In Progress') return false;
      if (filterStatus === 'Identified' && loc.status !== 'Verified' && loc.status !== 'Reunification Ready') return false;
      if (filterStatus === 'Reunited' && loc.status !== 'Reunified') return false;
    }
    
    // Search
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      if (!loc.case_id?.toLowerCase().includes(q) && !loc.name?.toLowerCase().includes(q)) {
        return false;
      }
    }
    
    return true;
  });

  if (filteredLocations.length === 0 && caseId) {
    return (
      <div className="space-y-6">
        <button onClick={() => navigate(-1)} className="flex items-center text-gray-600 hover:text-gray-900">
          <ArrowLeft className="h-4 w-4 mr-2" /> Back to Case
        </button>
        <ErrorState message="No recorded locations are available for this case." />
      </div>
    );
  }

  const center = filteredLocations.length > 0 ? [filteredLocations[0].latitude, filteredLocations[0].longitude] : [20.5937, 78.9629];
  const polylinePositions = caseId ? filteredLocations.map(loc => [loc.latitude, loc.longitude]) : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between space-y-4 sm:space-y-0 sm:space-x-4">
        <div className="flex items-center space-x-4">
          {caseId && (
            <button onClick={() => navigate(-1)} className="p-2 hover:bg-gray-100 rounded-full transition-colors">
              <ArrowLeft className="h-5 w-5 text-gray-600" />
            </button>
          )}
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
              {caseId ? `Location History: ${caseId}` : 'Reunification Map'}
            </h1>
          </div>
        </div>

        {!caseId && (
          <div className="flex flex-col sm:flex-row items-center gap-3">
            <div className="flex items-center gap-2 max-w-sm w-full bg-white p-1 rounded-md border border-gray-300">
              <Search className="h-4 w-4 text-gray-400 ml-2" />
              <input
                type="text"
                placeholder="Search case ID or location..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full p-1 text-sm focus:outline-none"
              />
              <VoiceInput onResult={(text) => setSearchQuery(text)} />
            </div>
            
            <div className="flex items-center gap-2 bg-white rounded-md border border-gray-300 p-1.5">
              <Filter className="h-4 w-4 text-gray-500" />
              <select 
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="text-sm focus:outline-none bg-transparent"
              >
                <option value="All">All</option>
                <option value="Missing">Missing</option>
                <option value="Identified">Identified</option>
                <option value="Reunited">Reunited</option>
              </select>
            </div>
          </div>
        )}
      </div>

      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-md flex items-start gap-3">
        <AlertTriangle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-sm text-yellow-800 font-medium">Recorded disaster events — not continuous GPS tracking.</p>
          <p className="text-xs text-yellow-700 mt-1">This map connects discrete known locations (e.g., last seen, rescue site, hospital) based on submitted reports.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Map Container */}
        <div className="lg:col-span-2 h-[500px] rounded-2xl overflow-hidden shadow-sm border border-gray-100 z-0 relative">
          <MapContainer center={center} zoom={13} style={{ height: '100%', width: '100%', zIndex: 0 }}>
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {caseId && polylinePositions.length > 1 && (
              <Polyline 
                positions={polylinePositions} 
                color="blue" 
                weight={3} 
                opacity={0.5} 
                dashArray="10, 10" 
              />
            )}
            
            <MarkerClusterGroup chunkedLoading>
              {filteredLocations.map((loc, idx) => (
                <Marker 
                  key={idx} 
                  position={[loc.latitude, loc.longitude]}
                  icon={createIcon(getMarkerColor(loc.type))}
                >
                  <Popup>
                    <div className="p-1 min-w-[150px]">
                      {loc.case_id && (
                        <p className="font-bold text-primary mb-1">{loc.case_id}</p>
                      )}
                      <p className="font-bold uppercase text-xs text-gray-500 mb-1">{loc.type}</p>
                      <p className="font-semibold text-gray-900">{loc.name}</p>
                      {loc.status && (
                         <p className="text-xs font-semibold mt-1">Status: {loc.status}</p>
                      )}
                      <p className="text-xs text-gray-500 mt-1">Source: {loc.source}</p>
                      <p className="text-xs text-gray-500">{new Date(loc.timestamp).toLocaleString()}</p>
                      {loc.case_id && (
                        <button 
                          onClick={() => navigate(`/cases/${loc.case_id}`)}
                          className="mt-2 text-xs bg-primary text-white px-2 py-1 rounded w-full"
                        >
                          View Case
                        </button>
                      )}
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MarkerClusterGroup>
          </MapContainer>
        </div>

        {/* Timeline */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 h-[500px] overflow-y-auto">
          <h2 className="text-lg font-bold mb-6 flex items-center gap-2">
            <MapPin className="h-5 w-5 text-primary" /> Chronological Path
          </h2>
          
          <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gray-200">
            {filteredLocations.map((loc, idx) => (
              <div key={idx} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group">
                <div className={`flex items-center justify-center w-10 h-10 rounded-full border border-white shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10 bg-white`}>
                  <MapPin className="h-5 w-5 text-gray-500" />
                </div>
                <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded border border-gray-200 bg-white shadow-sm">
                  <div className="flex items-center justify-between space-x-2 mb-1">
                    <div className="font-bold text-gray-900 uppercase text-xs">{loc.type}</div>
                    {loc.case_id && <div className="text-xs font-bold text-primary">{loc.case_id}</div>}
                  </div>
                  <div className="text-sm font-medium text-gray-800 mb-1">
                    {loc.name}
                  </div>
                  <div className="text-xs text-gray-500 flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {new Date(loc.timestamp).toLocaleString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
