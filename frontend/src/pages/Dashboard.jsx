import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import { Activity, ShieldCheck, HeartHandshake, UserX, Building2, MapPin, Search } from 'lucide-react';

function StatCard({ title, value, icon: Icon, colorClass, onClick }) {
  return (
    <div 
      onClick={onClick}
      className={`bg-white rounded-2xl p-6 shadow-sm border border-gray-100 ${onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''}`}
    >
      <div className="flex items-center gap-4">
        <div className={`h-12 w-12 rounded-full flex items-center justify-center ${colorClass}`}>
          <Icon className="h-6 w-6" />
        </div>
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <h3 className="text-2xl font-bold text-gray-900">{value}</h3>
        </div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    api.get('/dashboard/stats')
      .then(res => {
        setStats(res.data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.response?.data?.detail || err.message || "Failed to load dashboard stats");
        setLoading(false);
      });
  }, []);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;
  if (!stats) return <ErrorState message="No data available" />;

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-bold text-gray-900">Command Center Overview</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          title="Active Cases" 
          value={stats.active_cases} 
          icon={Activity} 
          colorClass="bg-blue-100 text-blue-600"
          onClick={() => navigate('/cases')}
        />
        <StatCard 
          title="Missing Persons" 
          value={stats.missing_persons} 
          icon={UserX} 
          colorClass="bg-red-100 text-red-600"
          onClick={() => navigate('/family/cases')}
        />
        <StatCard 
          title="Potential Matches" 
          value={stats.potential_matches} 
          icon={Search} 
          colorClass="bg-purple-100 text-purple-600"
          onClick={() => navigate('/cases')}
        />
        <StatCard 
          title="In Verification" 
          value={stats.in_verification} 
          icon={ShieldCheck} 
          colorClass="bg-amber-100 text-amber-600"
          onClick={() => navigate('/cases')} // Or verification queue if it existed
        />
        <StatCard 
          title="Verified" 
          value={stats.verified} 
          icon={ShieldCheck} 
          colorClass="bg-green-100 text-green-600"
          onClick={() => navigate('/cases')} 
        />
        <StatCard 
          title="Reunification (Active)" 
          value={stats.reunification_in_progress} 
          icon={HeartHandshake} 
          colorClass="bg-orange-100 text-orange-600"
        />
        <StatCard 
          title="Reunited" 
          value={stats.reunited} 
          icon={HeartHandshake} 
          colorClass="bg-emerald-100 text-emerald-600"
        />
        <StatCard 
          title="Locations Tracked" 
          value={stats.total_locations} 
          icon={MapPin} 
          colorClass="bg-indigo-100 text-indigo-600"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-gray-900">
            <Building2 className="h-5 w-5 text-primary" /> Participating Organizations
          </h3>
          <div className="flex items-center gap-4">
            <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-2xl">
              {stats.total_organizations}
            </div>
            <div>
              <p className="text-gray-600 font-medium">Hospitals, Shelters, and Rescue Teams</p>
              <p className="text-sm text-gray-500">Actively reporting found individuals.</p>
            </div>
          </div>
        </div>
        
        <div className="bg-gradient-to-br from-[#111c44] to-[#2b3674] rounded-2xl p-6 shadow-sm text-white">
          <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
            <Activity className="h-5 w-5 text-pink-500" /> Platform Status
          </h3>
          <p className="text-gray-300 text-sm mb-4">
            The Verified Reunification Network is actively processing missing person reports, running AI candidate matching, and tracking workflow states.
          </p>
          <div className="flex gap-4 text-sm font-medium">
            <div className="bg-white/10 px-3 py-1.5 rounded-lg border border-white/20">All systems operational</div>
            <div className="bg-green-500/20 text-green-300 px-3 py-1.5 rounded-lg border border-green-500/30">Secure Mode</div>
          </div>
        </div>
      </div>
    </div>
  );
}
