import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Mail, Lock, User, Shield, AlertCircle, Loader2 } from 'lucide-react';

export default function Register() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [roleId, setRoleId] = useState(3);
  const [roles, setRoles] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    axios.get(`${API_URL}/api/v1/users/roles`)
      .then((res) => {
        setRoles(res.data);
        const devRole = res.data.find(r => r.name === 'DEVELOPER');
        if (devRole) setRoleId(devRole.id);
      })
      .catch((err) => {
        console.error('Failed to retrieve security roles:', err);
        setRoles([
          { id: 1, name: 'ADMIN', description: 'System Administrator' },
          { id: 2, name: 'SECURITY_ANALYST', description: 'Analyst' },
          { id: 3, name: 'DEVELOPER', description: 'Developer' }
        ]);
      });
  }, []);

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await axios.post(`${API_URL}/api/v1/auth/register`, {
        username,
        email,
        password,
        role_id: parseInt(roleId)
      });
      navigate('/login');
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Account generation failed. Please verify API backend is online.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center items-center px-6 selection:bg-green-100 selection:text-green-900">
      <div className="w-full max-w-md">
        
        {/* Logo Banner */}
        <div className="flex justify-center mb-8">
          <Link to="/">
            <div className="flex items-center gap-3 select-none">
              <svg className="w-10 h-10" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M100 20C135 20 170 30 170 30V100C170 145 135 175 100 185C65 175 30 145 30 100V30C30 30 65 20 100 20Z" stroke="#22C55E" strokeWidth="8" strokeLinecap="round" strokeLinejoin="round" fill="#F0FDF4" />
                <circle cx="100" cy="55" r="5" fill="#4ADE80" />
                <circle cx="70" cy="90" r="5" fill="#4ADE80" />
                <circle cx="130" cy="90" r="5" fill="#4ADE80" />
                <circle cx="100" cy="125" r="5" fill="#4ADE80" />
                <line x1="100" y1="55" x2="70" y2="90" stroke="#22C55E" strokeWidth="2" strokeDasharray="3 3" />
                <line x1="100" y1="55" x2="130" y2="90" stroke="#22C55E" strokeWidth="2" strokeDasharray="3 3" />
                <line x1="70" y1="90" x2="100" y2="125" stroke="#22C55E" strokeWidth="2" strokeDasharray="3 3" />
                <line x1="130" y1="90" x2="100" y2="125" stroke="#22C55E" strokeWidth="2" strokeDasharray="3 3" />
                <line x1="100" y1="55" x2="100" y2="125" stroke="#22C55E" strokeWidth="1" />
                <circle cx="100" cy="95" r="30" stroke="#4ADE80" strokeWidth="6" fill="none" strokeDasharray="90 10" />
                <line x1="121" y1="116" x2="140" y2="135" stroke="#4ADE80" strokeWidth="6" strokeLinecap="round" />
              </svg>
              <span className="font-extrabold text-2xl tracking-tight text-green-950">
                RiskLens<span className="text-green-600">AI</span>
              </span>
            </div>
          </Link>
        </div>

        {/* Card */}
        <div className="glass-panel border border-green-200 p-8 rounded-3xl shadow-lg relative bg-white">
          <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-green-500 to-emerald-400 rounded-t-3xl"></div>

          <h2 className="text-2xl font-bold text-center text-green-950 mb-2">Create Security Account</h2>
          <p className="text-xs text-neutral-500 text-center mb-6 font-medium">Register a new profile to access the platform.</p>

          {error && (
            <div className="bg-red-50 border border-red-200 px-4 py-3 rounded-xl flex items-center gap-3 mb-6">
              <AlertCircle className="w-5 h-5 text-red-500 shrink-0" />
              <span className="text-xs text-red-800 font-semibold">{error}</span>
            </div>
          )}

          <form onSubmit={handleRegister} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-green-800 uppercase tracking-wider mb-1.5">Username</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-green-700">
                  <User className="w-4 h-4" />
                </span>
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-slate-50 border border-green-100 focus:border-green-500 rounded-xl py-2.5 pl-10 pr-4 text-sm text-green-950 placeholder-neutral-400 outline-none transition-all focus:bg-white"
                  placeholder="e.g. analyst1"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-green-800 uppercase tracking-wider mb-1.5">Email Address</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-green-700">
                  <Mail className="w-4 h-4" />
                </span>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-slate-50 border border-green-100 focus:border-green-500 rounded-xl py-2.5 pl-10 pr-4 text-sm text-green-950 placeholder-neutral-400 outline-none transition-all focus:bg-white"
                  placeholder="e.g. user@domain.com"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-green-800 uppercase tracking-wider mb-1.5">Password</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-green-700">
                  <Lock className="w-4 h-4" />
                </span>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-slate-50 border border-green-100 focus:border-green-500 rounded-xl py-2.5 pl-10 pr-4 text-sm text-green-950 placeholder-neutral-400 outline-none transition-all focus:bg-white"
                  placeholder="&bull;&bull;&bull;&bull;&bull;&bull;&bull;&bull;&bull;&bull;"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-green-800 uppercase tracking-wider mb-1.5">Security Role Profile</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-green-700">
                  <Shield className="w-4 h-4" />
                </span>
                <select
                  value={roleId}
                  onChange={(e) => setRoleId(e.target.value)}
                  className="w-full bg-slate-50 border border-green-100 focus:border-green-500 rounded-xl py-2.5 pl-10 pr-4 text-sm text-green-950 outline-none transition-all focus:bg-white cursor-pointer select-none"
                >
                  {roles.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.name.replace('_', ' ')}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-green-500 hover:bg-green-650 disabled:bg-slate-200 text-white disabled:text-neutral-400 font-bold py-3 rounded-xl flex items-center justify-center gap-2 shadow-md shadow-green-500/10 cursor-pointer transition-all active:scale-[0.98]"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> Seeding Account...
                </>
              ) : (
                'Generate Credentials'
              )}
            </button>
          </form>

          {/* Sign In link */}
          <div className="mt-8 pt-6 border-t border-green-100 text-center">
            <span className="text-xs text-neutral-500 font-medium">Already registered? </span>
            <Link to="/login" className="text-xs text-green-600 font-bold hover:underline">Log In</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
