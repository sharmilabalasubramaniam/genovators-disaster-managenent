import os

files_to_create = {
    "frontend/src/services/api.js": """import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

export default api;
""",
    "frontend/src/components/LoadingState.jsx": """import React from 'react';
import { Loader2 } from 'lucide-react';

export default function LoadingState() {
  return (
    <div className="flex h-full min-h-[400px] items-center justify-center">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
    </div>
  );
}
""",
    "frontend/src/components/ErrorState.jsx": """import React from 'react';
import { AlertTriangle } from 'lucide-react';

export default function ErrorState({ message }) {
  return (
    <div className="flex h-full min-h-[400px] flex-col items-center justify-center gap-4 text-center">
      <div className="rounded-full bg-red-100 p-3 text-red-600">
        <AlertTriangle className="h-8 w-8" />
      </div>
      <div>
        <h3 className="text-lg font-semibold">Something went wrong</h3>
        <p className="text-sm text-gray-500">{message || 'An unexpected error occurred.'}</p>
      </div>
    </div>
  );
}
""",
    "frontend/src/components/EmptyState.jsx": """import React from 'react';
import { FileQuestion } from 'lucide-react';

export default function EmptyState({ title, description }) {
  return (
    <div className="flex h-full min-h-[400px] flex-col items-center justify-center gap-4 text-center">
      <div className="rounded-full bg-gray-100 p-3 text-gray-400">
        <FileQuestion className="h-8 w-8" />
      </div>
      <div>
        <h3 className="text-lg font-semibold">{title || 'No results found'}</h3>
        <p className="text-sm text-gray-500">{description || 'Try adjusting your search or filters.'}</p>
      </div>
    </div>
  );
}
""",
    "frontend/src/layouts/DashboardLayout.jsx": """import React from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { HeartPulse, Home, FolderOpen, Map as MapIcon, Network, ShieldCheck, Bell, LineChart, Settings, Search, ChevronDown, UserPlus, Users, Activity } from 'lucide-react';

function NavItem({ icon: Icon, label, to, active, badge }) {
  return (
    <Link to={to} className={`flex items-center gap-4 rounded-xl px-4 py-3.5 text-[15px] font-medium transition-all ${active ? 'bg-[#2b3674] text-white' : 'text-gray-400 hover:bg-white/10 hover:text-white'}`}>
      <Icon className="h-[18px] w-[18px]" />
      {label}
      {badge && <span className="ml-auto rounded-full bg-pink-500 px-2 py-0.5 text-xs text-white">{badge}</span>}
    </Link>
  );
}

export default function DashboardLayout() {
  const location = useLocation();
  const path = location.pathname;

  return (
    <div className="flex min-h-screen bg-gray-50 font-sans text-gray-900">
      <aside className="fixed flex h-screen w-[280px] flex-col bg-[#111c44] p-6 text-white">
        <div className="mb-10 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-pink-500">
            <HeartPulse className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-base font-bold leading-tight">Verified Reunification</h2>
            <p className="text-[11px] text-gray-400">People. Evidence. Reunited.</p>
          </div>
        </div>

        <nav className="flex flex-1 flex-col gap-2">
          <NavItem icon={Home} label="Dashboard" to="/dashboard" active={path === '/dashboard'} />
          <NavItem icon={FolderOpen} label="Cases" to="/cases" active={path.startsWith('/cases')} />
          <NavItem icon={MapIcon} label="Map" to="/map" active={path === '/map'} />
          <NavItem icon={Users} label="Family" to="/family" active={path === '/family'} />
          <NavItem icon={Activity} label="Hospital" to="/hospital" active={path === '/hospital'} />
          <NavItem icon={Home} label="Shelter" to="/shelter" active={path === '/shelter'} />
          <NavItem icon={UserPlus} label="Rescue" to="/rescue" active={path === '/rescue'} />
          <NavItem icon={ShieldCheck} label="Verification" to="/verification" active={path === '/verification'} />
          <NavItem icon={Bell} label="Notifications" to="/notifications" active={path === '/notifications'} badge="3" />
          <NavItem icon={Settings} label="Settings" to="/settings" active={path === '/settings'} />
        </nav>
      </aside>

      <main className="ml-[280px] flex flex-1 flex-col gap-6 p-8">
        <header className="flex items-center justify-between">
          <div>
            <h1 className="mb-1 text-3xl font-bold capitalize">{path.split('/')[1] || 'Dashboard'}</h1>
          </div>
          <div className="flex items-center gap-6">
            <div className="relative cursor-pointer text-gray-500">
              <Bell className="h-6 w-6" />
              <span className="absolute -right-2 -top-1 rounded-full bg-pink-500 px-1.5 py-0.5 text-[10px] text-white">3</span>
            </div>
            <div className="flex cursor-pointer items-center gap-3">
              <div className="flex flex-col text-right">
                <span className="text-sm font-semibold">User</span>
                <span className="text-xs text-gray-500">Officer</span>
              </div>
            </div>
          </div>
        </header>
        <div className="flex-1">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
""",
    "frontend/src/pages/Dashboard.jsx": """import React, { useEffect, useState } from 'react';
import api from '../services/api';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';

export default function Dashboard() {
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/health')
      .then(res => {
        setStatus(res.data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  return (
    <div className="rounded-2xl bg-white p-6 shadow-sm">
      <h2 className="text-lg font-bold mb-4">System Status</h2>
      <pre className="bg-gray-100 p-4 rounded-lg">{JSON.stringify(status, null, 2)}</pre>
      <div className="mt-8">
        <p>This is the dashboard placeholder.</p>
      </div>
    </div>
  );
}
""",
    "frontend/src/pages/Cases.jsx": """import React from 'react';
export default function Cases() { return <div className="p-6 bg-white rounded-2xl">Cases Placeholder</div>; }
""",
    "frontend/src/pages/NewCase.jsx": """import React from 'react';
export default function NewCase() { return <div className="p-6 bg-white rounded-2xl">New Case Placeholder</div>; }
""",
    "frontend/src/pages/CaseDetail.jsx": """import React from 'react';
import { useParams } from 'react-router-dom';
export default function CaseDetail() { 
  const { id } = useParams();
  return <div className="p-6 bg-white rounded-2xl">Case Detail for {id}</div>; 
}
""",
    "frontend/src/pages/PlaceholderPage.jsx": """import React from 'react';
import { useLocation } from 'react-router-dom';
export default function PlaceholderPage() {
  const location = useLocation();
  return <div className="p-6 bg-white rounded-2xl capitalize">{location.pathname.replace('/', '')} Placeholder</div>;
}
""",
    "frontend/src/App.jsx": """import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import DashboardLayout from './layouts/DashboardLayout';
import Dashboard from './pages/Dashboard';
import Cases from './pages/Cases';
import NewCase from './pages/NewCase';
import CaseDetail from './pages/CaseDetail';
import PlaceholderPage from './pages/PlaceholderPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route element={<DashboardLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/cases" element={<Cases />} />
          <Route path="/cases/new" element={<NewCase />} />
          <Route path="/cases/:id" element={<CaseDetail />} />
          <Route path="/family" element={<PlaceholderPage />} />
          <Route path="/hospital" element={<PlaceholderPage />} />
          <Route path="/shelter" element={<PlaceholderPage />} />
          <Route path="/rescue" element={<PlaceholderPage />} />
          <Route path="/map" element={<PlaceholderPage />} />
          <Route path="/verification" element={<PlaceholderPage />} />
          <Route path="/notifications" element={<PlaceholderPage />} />
          <Route path="/settings" element={<PlaceholderPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
"""
}

for path, content in files_to_create.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
