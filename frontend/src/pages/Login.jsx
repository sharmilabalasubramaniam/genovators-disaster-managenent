import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff, Users, ShieldCheck, Leaf } from 'lucide-react';
import api from '../services/api';
import SahyatLogo from '../components/SahyatLogo';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const res = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      
      localStorage.setItem('token', res.data.access_token);
      
      const userRes = await api.get('/auth/me');
      localStorage.setItem('user', JSON.stringify(userRes.data));
      
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-white font-sans text-gray-900 flex flex-col justify-between">
      
      {/* Background Image Container */}
      <div 
        className="absolute inset-0 w-full h-[85vh] bg-cover bg-center bg-no-repeat z-0"
        style={{ backgroundImage: 'url("/assets/login-bg.jpg")', backgroundPosition: 'center 20%' }}
      >
        {/* Subtle white gradient overlay to ensure text readability */}
        <div className="absolute inset-0 bg-white/40 md:bg-white/30 backdrop-blur-[1px]"></div>
      </div>

      {/* Main Content Area */}
      <div className="relative z-10 flex flex-col items-center pt-[5vh] sm:pt-[8vh] flex-grow">
        
        {/* Logo */}
        <div className="mb-2">
          <SahyatLogo variant="full" className="drop-shadow-lg" />
        </div>

        {/* Welcome Text */}
        <div className="text-center mb-8">
          <h2 className="text-[#0a2540] text-3xl md:text-4xl font-extrabold tracking-tight mb-2 drop-shadow-sm">Welcome Back</h2>
          <p className="text-[#3b4c68] font-medium drop-shadow-sm text-sm md:text-base">Sign in to continue to SAHYAT</p>
        </div>

        {/* Login Form */}
        <div className="w-full max-w-md px-6">
          {error && (
            <div className="mb-6 rounded-lg bg-red-50/90 backdrop-blur border border-red-200 p-3 text-sm text-red-600 shadow-sm text-center font-medium">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="flex flex-col gap-5">
            {/* Email Field */}
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <Mail className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="block w-full pl-11 pr-4 py-3.5 rounded-xl border border-gray-200 bg-white/90 backdrop-blur-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 focus:outline-none transition-all shadow-sm font-medium"
                placeholder="Email"
                required
              />
            </div>

            {/* Password Field */}
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <Lock className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="block w-full pl-11 pr-12 py-3.5 rounded-xl border border-gray-200 bg-white/90 backdrop-blur-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200 focus:outline-none transition-all shadow-sm font-medium"
                placeholder="Password"
                required
              />
              <button 
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600 focus:outline-none"
              >
                {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
              </button>
            </div>

            {/* Sign In Button */}
            <button
              type="submit"
              disabled={loading}
              className="mt-2 w-full flex justify-center py-4 rounded-xl bg-[#0a2540] text-white font-bold text-lg hover:bg-[#113155] focus:outline-none focus:ring-4 focus:ring-blue-200 transition-all shadow-lg disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          {/* Quick Login (Auto-fill) for Demo Purposes */}
          <div className="mt-8 flex justify-center gap-3">
            {['Admin', 'Officer'].map(role => (
              <button
                key={role}
                type="button"
                onClick={() => {
                  setUsername(`${role.toLowerCase()}@sahyat.demo`);
                  setPassword('password123');
                }}
                className="text-xs font-semibold text-gray-500 bg-white/60 hover:bg-white/90 px-3 py-1.5 rounded-full border border-gray-200 shadow-sm backdrop-blur transition-all"
              >
                Use {role}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Features Area */}
      <div 
        className="relative z-20 w-full bg-white pt-10 pb-8 px-4"
        style={{
          borderTopLeftRadius: '50% 40px',
          borderTopRightRadius: '50% 40px',
          boxShadow: '0 -10px 30px rgba(0,0,0,0.05)'
        }}
      >
        <div className="max-w-4xl mx-auto grid grid-cols-3 gap-4 md:gap-8 divide-x divide-gray-100">
          
          <div className="flex flex-col items-center text-center px-2">
            <Users className="h-8 w-8 text-blue-500 mb-2" strokeWidth={2.5} />
            <h4 className="font-bold text-[#0a2540] text-sm md:text-base mb-1">Reunite</h4>
            <p className="text-xs md:text-sm text-gray-500 font-medium leading-tight max-w-[200px]">Bringing people back together</p>
          </div>
          
          <div className="flex flex-col items-center text-center px-2">
            <ShieldCheck className="h-8 w-8 text-blue-600 mb-2" strokeWidth={2.5} />
            <h4 className="font-bold text-[#0a2540] text-sm md:text-base mb-1">Respond</h4>
            <p className="text-xs md:text-sm text-gray-500 font-medium leading-tight max-w-[200px]">Faster, smarter disaster action</p>
          </div>
          
          <div className="flex flex-col items-center text-center px-2">
            <Leaf className="h-8 w-8 text-teal-600 mb-2" strokeWidth={2.5} />
            <h4 className="font-bold text-[#0a2540] text-sm md:text-base mb-1">Restore</h4>
            <p className="text-xs md:text-sm text-gray-500 font-medium leading-tight max-w-[200px]">Stronger, safer communities</p>
          </div>
          
        </div>
      </div>
      
    </div>
  );
}
