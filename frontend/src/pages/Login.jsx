import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Logo from '../components/Logo';
import { Lock, User, AlertCircle, Loader2 } from 'lucide-react';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Backend URL config
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await axios.post(`${API_URL}/api/v1/auth/login`, {
        username,
        password,
      });

      const { access_token, role, username: resUser } = response.data;
      
      // Store in session
      localStorage.setItem('token', access_token);
      localStorage.setItem('role', role);
      localStorage.setItem('username', resUser);

      navigate('/dashboard');
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Connection to security server failed. Verify uvicorn is running.');
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

          <h2 className="text-2xl font-bold text-center text-white mb-2">Secure Gateway Login</h2>
          <p className="text-xs text-neutral-400 text-center mb-6">Enter credentials to authenticate session token.</p>

          {error && (
            <div className="bg-red-950/40 border border-red-500/20 px-4 py-3 rounded-lg flex items-center gap-3 mb-6">
              <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
              <span className="text-xs text-red-200">{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
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
                  placeholder="e.g. admin"
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

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-green-500 hover:bg-green-400 disabled:bg-neutral-800 text-black disabled:text-neutral-500 font-bold py-3 rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-green-500/10 cursor-pointer transition-all active:scale-[0.98]"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> Verifying Credentials...
                </>
              ) : (
                'Authenticate'
              )}
            </button>
          </form>

          {/* Quick Access Details */}
          <div className="mt-8 pt-6 border-t border-neutral-900 text-center">
            <span className="text-xs text-neutral-500">Need an analyst profile? </span>
            <Link to="/register" className="text-xs text-green-400 hover:underline">Register Account</Link>
          </div>
          
          <div className="mt-4 bg-neutral-900/60 p-3 rounded-lg border border-neutral-800/40 text-[10px] text-neutral-500 space-y-1">
            <div className="font-bold text-neutral-400">Quick Test Credentials:</div>
            <div>&bull; Admin: <code className="text-green-400">admin</code> / <code className="text-green-400">AdminPassword123!</code></div>
            <div>&bull; Analyst: <code className="text-green-400">analyst</code> / <code className="text-green-400">AnalystPassword123!</code></div>
            <div>&bull; Developer: <code className="text-green-400">developer</code> / <code className="text-green-400">DeveloperPassword123!</code></div>
          </div>
        </div>
      </div>
    </div>
  );
}
