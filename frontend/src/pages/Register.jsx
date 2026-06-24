import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Logo from '../components/Logo';
import { Mail, Lock, User, Shield, AlertCircle, Loader2 } from 'lucide-react';

export default function Register() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [roleId, setRoleId] = useState(3); // Default to Developer
  const [roles, setRoles] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    // Fetch roles list on load
    axios.get(`${API_URL}/api/v1/users/roles`)
      .then((res) => {
        setRoles(res.data);
        // Find Developer role ID as default
        const devRole = res.data.find(r => r.name === 'DEVELOPER');
        if (devRole) setRoleId(devRole.id);
      })
      .catch((err) => {
        console.error('Failed to retrieve security roles:', err);
        // Fallback static
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
    <div className="min-h-screen bg-neutral-950 flex flex-col justify-center items-center px-6 selection:bg-green-500 selection:text-black">
      <div className="w-full max-w-md">
        
        {/* Logo Banner */}
        <div className="flex justify-center mb-8">
          <Link to="/">
            <Logo />
          </Link>
        </div>

        {/* Card */}
        <div className="dark-glass-panel border border-emerald-950 p-8 rounded-2xl shadow-2xl relative">
          <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-green-500 to-emerald-400 rounded-t-2xl"></div>

          <h2 className="text-2xl font-bold text-center text-white mb-2">Create Security Account</h2>
          <p className="text-xs text-neutral-400 text-center mb-6">Register a new profile to access the platform.</p>

          {error && (
            <div className="bg-red-950/40 border border-red-500/20 px-4 py-3 rounded-lg flex items-center gap-3 mb-6">
              <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
              <span className="text-xs text-red-200">{error}</span>
            </div>
          )}

          <form onSubmit={handleRegister} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-neutral-400 uppercase tracking-wider mb-1.5">Username</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-neutral-500">
                  <User className="w-4 h-4" />
                </span>
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-neutral-900 border border-neutral-800 focus:border-green-500 rounded-xl py-2.5 pl-10 pr-4 text-sm text-white placeholder-neutral-600 outline-none transition-all"
                  placeholder="e.g. analyst1"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-neutral-400 uppercase tracking-wider mb-1.5">Email Address</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-neutral-500">
                  <Mail className="w-4 h-4" />
                </span>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-neutral-900 border border-neutral-800 focus:border-green-500 rounded-xl py-2.5 pl-10 pr-4 text-sm text-white placeholder-neutral-600 outline-none transition-all"
                  placeholder="e.g. user@domain.com"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-neutral-400 uppercase tracking-wider mb-1.5">Password</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-neutral-500">
                  <Lock className="w-4 h-4" />
                </span>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-neutral-900 border border-neutral-800 focus:border-green-500 rounded-xl py-2.5 pl-10 pr-4 text-sm text-white placeholder-neutral-600 outline-none transition-all"
                  placeholder="&bull;&bull;&bull;&bull;&bull;&bull;&bull;&bull;&bull;&bull;"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-neutral-400 uppercase tracking-wider mb-1.5">Security Role Profile</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-neutral-500">
                  <Shield className="w-4 h-4" />
                </span>
                <select
                  value={roleId}
                  onChange={(e) => setRoleId(e.target.value)}
                  className="w-full bg-neutral-900 border border-neutral-800 focus:border-green-500 rounded-xl py-2.5 pl-10 pr-4 text-sm text-white outline-none transition-all appearance-none cursor-pointer"
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
              className="w-full bg-green-500 hover:bg-green-400 disabled:bg-neutral-800 text-black disabled:text-neutral-500 font-bold py-3 rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-green-500/10 cursor-pointer transition-all active:scale-[0.98]"
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
          <div className="mt-8 pt-6 border-t border-neutral-900 text-center">
            <span className="text-xs text-neutral-500">Already registered? </span>
            <Link to="/login" className="text-xs text-green-400 hover:underline">Log In</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
