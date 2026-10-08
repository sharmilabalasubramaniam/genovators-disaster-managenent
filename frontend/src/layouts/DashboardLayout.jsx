import React from 'react';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { HeartPulse, Home, FolderOpen, Map as MapIcon, ShieldCheck, Bell, Settings, UserPlus, Users, Activity, LogOut } from 'lucide-react';
import api from '../services/api';
import Chatbot from '../components/Chatbot';

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
  const navigate = useNavigate();
  const [unreadCount, setUnreadCount] = React.useState(0);
  
  const userStr = localStorage.getItem('user');
  const user = userStr ? JSON.parse(userStr) : { name: 'User', role: 'Unknown' };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  React.useEffect(() => {
    api.get('/notifications/unread')
      .then(res => setUnreadCount(res.data.length))
      .catch(err => console.error(err));
  }, [path]);

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
          <NavItem icon={Activity} label="Predictions" to="/predictions" active={path === '/predictions'} />
          <NavItem icon={Bell} label="Notifications" to="/notifications" active={path === '/notifications'} badge={unreadCount > 0 ? unreadCount : null} />
        </nav>
      </aside>

      <main className="ml-[280px] flex flex-1 flex-col gap-6 p-8">
        <header className="flex items-center justify-between">
          <div>
            <h1 className="mb-1 text-3xl font-bold capitalize">{path.split('/')[1] || 'Dashboard'}</h1>
          </div>
          <div className="flex items-center gap-6">
            <div className="relative cursor-pointer text-gray-500" onClick={() => navigate('/notifications')}>
              <Bell className="h-6 w-6" />
              {unreadCount > 0 && <span className="absolute -right-2 -top-1 rounded-full bg-pink-500 px-1.5 py-0.5 text-[10px] text-white">{unreadCount}</span>}
            </div>
            <div className="flex items-center gap-4">
              <div className="flex flex-col text-right">
                <span className="text-sm font-semibold">{user.name || user.username}</span>
                <span className="text-xs text-gray-500 capitalize">{user.role?.toLowerCase()}</span>
              </div>
              <button onClick={handleLogout} className="text-gray-400 hover:text-red-500 transition-colors">
                <LogOut className="h-5 w-5" />
              </button>
            </div>
          </div>
        </header>
        <div className="flex-1">
          <Outlet />
        </div>
      </main>
      <Chatbot />
    </div>
  );
}
