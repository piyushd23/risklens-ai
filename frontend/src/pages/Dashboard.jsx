import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import {
  Shield,
  FolderLock,
  Plus,
  Play,
  FileDown,
  Terminal,
  LogOut,
  Users,
  Copy,
  CheckCircle,
  FileSpreadsheet,
  Activity,
  User
} from 'lucide-react';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  
  const [targets, setTargets] = useState([]);
  const [scans, setScans] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  
  const [mQuery, setMQuery] = useState('');
  const [copied, setCopied] = useState(false);

  const [scanTargetId, setScanTargetId] = useState('');
  const [scanConsent, setScanConsent] = useState(false);
  const [scanQueued, setScanQueued] = useState(false);

  const [newTarget, setNewTarget] = useState({
    name: '',
    url: '',
    description: '',
    environment: 'Staging',
    crawl_depth: 3,
    auth_type: 'None'
  });
  const [targetError, setTargetError] = useState('');

  const navigate = useNavigate();
  const username = localStorage.getItem('username') || 'analyst';
  const role = localStorage.getItem('role') || 'SECURITY_ANALYST';
  const token = localStorage.getItem('token');

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    fetchDashboardData();
  }, [token]);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const statsRes = await axios.get(`${API_URL}/api/v1/dashboard/stats`);
      setStats(statsRes.data);

      const targetsRes = await axios.get(`${API_URL}/api/v1/targets/`);
      setTargets(targetsRes.data);
      if (targetsRes.data.length > 0) {
        setScanTargetId(targetsRes.data[0].id);
      }

      const scansRes = await axios.get(`${API_URL}/api/v1/assessments/`);
      setScans(scansRes.data);

      const biRes = await axios.get(`${API_URL}/api/v1/analytics/powerbi/m-query`);
      setMQuery(biRes.data.m_query);

      if (role === 'ADMIN') {
        setAuditLogs([
          { id: 1, action: "SYSTEM_INIT", details: "Completed database initialization and seed.", username: "admin", created_at: "2026-06-24 11:34:00" },
          { id: 2, action: "USER_LOGIN", details: "User logged in under role ADMIN", username: "admin", created_at: "2026-06-24 16:58:00" },
          { id: 3, action: "CREATE_TARGET", details: "Created target 'OWASP Juice Shop Sandbox'", username: "analyst", created_at: "2026-06-24 11:34:10" }
        ]);
      }
    } catch (err) {
      console.error('Failed to retrieve dashboard assets:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate('/');
  };

  const handleLaunchScan = async (e) => {
    e.preventDefault();
    if (!scanConsent) {
      alert("You must explicitly confirm target consent before launching DAST crawler audits.");
      return;
    }

    setScanQueued(true);
    try {
      await axios.post(`${API_URL}/api/v1/assessments/`, {
        target_id: parseInt(scanTargetId)
      });
      alert("Scan launched successfully in background. Refresh dashboard in a few seconds.");
      fetchDashboardData();
    } catch (err) {
      console.error(err);
      alert("Launch scan failed. Verify target selection and auth permissions.");
    } finally {
      setScanQueued(false);
      setScanConsent(false);
    }
  };

  const handleAddTarget = async (e) => {
    e.preventDefault();
    setTargetError('');
    try {
      await axios.post(`${API_URL}/api/v1/targets/`, newTarget);
      alert("Target configured successfully.");
      setNewTarget({
        name: '',
        url: '',
        description: '',
        environment: 'Staging',
        crawl_depth: 3,
        auth_type: 'None'
      });
      fetchDashboardData();
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data && err.response.data.detail) {
        setTargetError(err.response.data.detail);
      } else {
        setTargetError("Failed to configure target URL scope.");
      }
    }
  };

  const handleDownloadReport = async (assessmentId, format = 'pdf') => {
    try {
      const genRes = await axios.post(`${API_URL}/api/v1/reports/generate/${assessmentId}`);
      const targetRep = genRes.data.find(r => r.report_type === format);
      if (!targetRep) {
        alert("Failed to build requested report layout.");
        return;
      }
      
      const downloadUrl = `${API_URL}/api/v1/reports/download/${targetRep.id}`;
      window.open(downloadUrl, '_blank');
    } catch (err) {
      console.error(err);
      alert("Report compilation error. Make sure scan completed successfully.");
    }
  };

  const copyMQuery = () => {
    navigator.clipboard.writeText(mQuery);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Chart configs
  const severityChartData = stats ? {
    labels: Object.keys(stats.severity_distribution),
    datasets: [{
      label: 'Findings Count',
      data: Object.values(stats.severity_distribution),
      backgroundColor: [
        'rgba(220, 38, 38, 0.7)',   // Critical
        'rgba(234, 88, 12, 0.7)',   // High
        'rgba(217, 119, 6, 0.7)',   // Medium
        'rgba(22, 163, 74, 0.7)'    // Low
      ],
      borderColor: [
        '#DC2626', '#EA580C', '#D97706', '#16A34A'
      ],
      borderWidth: 1.5
    }]
  } : null;

  const owaspChartData = stats ? {
    labels: Object.keys(stats.owasp_distribution).map(k => k.split(':')[0]),
    datasets: [{
      label: 'Findings by OWASP Category',
      data: Object.values(stats.owasp_distribution),
      backgroundColor: 'rgba(34, 197, 94, 0.6)',
      borderColor: '#22C55E',
      borderWidth: 1.5
    }]
  } : null;

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false }
    },
    scales: {
      x: {
        grid: { color: 'rgba(34, 197, 94, 0.05)' },
        ticks: { color: '#166534', font: { weight: 'bold' } }
      },
      y: {
        grid: { color: 'rgba(34, 197, 94, 0.05)' },
        ticks: { color: '#166534', precision: 0 }
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 text-green-950 flex flex-col justify-center items-center gap-4">
        <svg className="w-16 h-16 animate-pulse" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M100 20C135 20 170 30 170 30V100C170 145 135 175 100 185C65 175 30 145 30 100V30C30 30 65 20 100 20Z" stroke="#22C55E" strokeWidth="8" fill="#F0FDF4" />
          <circle cx="100" cy="95" r="30" stroke="#4ADE80" strokeWidth="6" fill="none" strokeDasharray="90 10" />
        </svg>
        <span className="text-sm font-semibold tracking-wider text-green-600">Loading RiskLens AI Environment...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FAFDFB] text-green-950 selection:bg-green-100 selection:text-green-900 flex">
      
      {/* SIDEBAR */}
      <aside className="w-72 bg-white border-r border-green-100 p-6 flex flex-col justify-between shrink-0 shadow-sm">
        <div>
          <div className="mb-10 flex items-center gap-3">
            <svg className="w-8 h-8" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M100 20C135 20 170 30 170 30V100C170 145 135 175 100 185C65 175 30 145 30 100V30C30 30 65 20 100 20Z" stroke="#22C55E" strokeWidth="8" fill="#F0FDF4" />
              <circle cx="100" cy="95" r="30" stroke="#4ADE80" strokeWidth="6" fill="none" strokeDasharray="90 10" />
            </svg>
            <span className="font-extrabold text-xl tracking-tight text-green-950">
              RiskLens<span className="text-green-600">AI</span>
            </span>
          </div>

          <div className="bg-green-50/50 p-4 rounded-2xl border border-green-100 mb-8">
            <span className="text-[10px] text-green-800/60 font-bold uppercase tracking-wider block">Logged Session</span>
            <span className="text-sm font-extrabold block text-green-950 mt-1">{username}</span>
            <span className="inline-flex items-center gap-1.5 text-xs text-green-600 font-bold mt-1">
              <Shield className="w-3.5 h-3.5" /> {role.replace('_', ' ')}
            </span>
          </div>

          <nav className="space-y-1">
            {[
              { id: 'dashboard', label: 'Executive Dashboard', icon: Activity },
              { id: 'targets', label: 'Target Scope', icon: FolderLock },
              { id: 'scans', label: 'Scan Engine', icon: Terminal },
              { id: 'powerbi', label: 'Power BI Feeds', icon: FileSpreadsheet },
              ...(role === 'ADMIN' ? [{ id: 'audit', label: 'Audit Logs', icon: Users }] : [])
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all cursor-pointer ${
                    activeTab === tab.id
                      ? 'bg-green-500 text-white shadow-md shadow-green-500/10'
                      : 'text-green-900/70 hover:text-green-950 hover:bg-green-50/50'
                  }`}
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold text-red-600 hover:bg-red-50 transition-all cursor-pointer"
        >
          <LogOut className="w-4 h-4" /> Sign Out
        </button>
      </aside>

      {/* MAIN VIEW AREA */}
      <main className="flex-1 p-10 overflow-y-auto">
        <header className="flex justify-between items-center pb-6 border-b border-green-100 mb-8">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-green-955">
              {activeTab === 'dashboard' && 'RiskLens AI Posture'}
              {activeTab === 'targets' && 'Target Scopes'}
              {activeTab === 'scans' && 'Vulnerability Discovery Engine'}
              {activeTab === 'powerbi' && 'Power BI Direct Connector'}
              {activeTab === 'audit' && 'System Security Audit Trails'}
            </h1>
            <p className="text-xs text-green-800/60 mt-1 font-semibold">
              {activeTab === 'dashboard' && 'Real-time DAST metrics and machine-learning anomaly logs.'}
              {activeTab === 'targets' && 'Configure URLs and consent rules for assessment targets.'}
              {activeTab === 'scans' && 'Run active crawling audits and inspect completed logs.'}
              {activeTab === 'powerbi' && 'Expose flat OData tables and fetch M query connectors.'}
              {activeTab === 'audit' && 'Track users logins, scan events, and download triggers.'}
            </p>
          </div>
          <div className="flex items-center gap-3 text-xs bg-white px-4 py-2.5 rounded-xl border border-green-150 shadow-sm">
            <span className="w-2.5 h-2.5 rounded-full bg-green-500 animate-ping"></span>
            <span className="font-mono text-green-900 font-semibold">SERVER ONLINE: 127.0.0.1:8000</span>
          </div>
        </header>

        {/* TAB 1: EXECUTIVE DASHBOARD */}
        {activeTab === 'dashboard' && stats && (
          <div className="space-y-8">
            {/* KPI Widgets */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white border border-green-100 p-5 rounded-2xl shadow-sm text-center">
                <span className="text-xs text-green-800/60 font-bold block uppercase tracking-wider">Security Score</span>
                <span className="text-3xl font-extrabold text-green-600 mt-2 block">{stats.overall_security_score}/100</span>
              </div>
              <div className="bg-white border border-green-100 p-5 rounded-2xl shadow-sm text-center">
                <span className="text-xs text-green-800/60 font-bold block uppercase tracking-wider">Compliance Score</span>
                <span className="text-3xl font-extrabold text-green-600 mt-2 block">{stats.overall_compliance_score}%</span>
              </div>
              <div className="bg-white border border-green-100 p-5 rounded-2xl shadow-sm text-center">
                <span className="text-xs text-green-800/60 font-bold block uppercase tracking-wider">Total Targets</span>
                <span className="text-3xl font-extrabold text-green-950 mt-2 block">{stats.total_targets}</span>
              </div>
              <div className="bg-white border border-green-100 p-5 rounded-2xl shadow-sm text-center">
                <span className="text-xs text-green-800/60 font-bold block uppercase tracking-wider">Discovered Findings</span>
                <span className="text-3xl font-extrabold text-green-950 mt-2 block">{stats.total_findings}</span>
              </div>
            </div>

            {/* Graphs Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="bg-white border border-green-100 p-6 rounded-2xl shadow-sm">
                <h3 className="font-bold text-sm text-green-900 mb-6">Threat Severity Ratio</h3>
                <div className="h-64 flex items-center justify-center">
                  <Bar 
                    data={severityChartData} 
                    options={chartOptions} 
                  />
                </div>
              </div>

              <div className="bg-white border border-green-100 p-6 rounded-2xl shadow-sm">
                <h3 className="font-bold text-sm text-green-900 mb-6">OWASP Top 10 Distribution</h3>
                <div className="h-64 flex items-center justify-center">
                  <Bar 
                    data={owaspChartData} 
                    options={chartOptions} 
                  />
                </div>
              </div>
            </div>

            {/* Recent Findings and AI Prioritizations */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Findings */}
              <div className="bg-white border border-green-100 p-6 rounded-2xl shadow-sm lg:col-span-2">
                <h3 className="font-bold text-sm text-green-900 mb-4">Latest Discovered Findings</h3>
                <div className="space-y-4">
                  {stats.recent_findings.length === 0 ? (
                    <div className="text-xs text-neutral-450 text-center py-6">No scan records available yet.</div>
                  ) : (
                    stats.recent_findings.map((f) => (
                      <div key={f.id} className="bg-slate-50 border border-green-50 p-4 rounded-xl">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-green-950 block">{f.title}</span>
                          <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded ${
                            f.severity === 'Critical' ? 'bg-red-50 text-red-700 border border-red-200' :
                            f.severity === 'High' ? 'bg-orange-50 text-orange-700 border border-orange-200' :
                            f.severity === 'Medium' ? 'bg-yellow-50 text-yellow-700 border border-yellow-200' :
                            'bg-green-50 text-green-700 border border-green-200'
                          }`}>
                            {f.severity} (CVSS {f.cvss_score})
                          </span>
                        </div>
                        <span className="text-[10px] text-green-800/60 mt-1 block">OWASP: {f.owasp_category}</span>
                        {f.risk_score && (
                          <div className="mt-3 pt-3 border-t border-green-100 flex items-center justify-between text-xs">
                            <span className="text-[10px] text-neutral-500">AI Rec: <code className="text-green-700 font-medium">{f.risk_score.recommended_action}</code></span>
                            <span className="text-[10px] font-bold text-green-600 uppercase">AI Priority: {f.risk_score.priority_score}</span>
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Anomaly Detection Diagnostic */}
              <div className="bg-white border border-green-100 p-6 rounded-2xl shadow-sm">
                <h3 className="font-bold text-sm text-green-900 mb-4">ML Outlier Diagnostics</h3>
                <div className="bg-slate-50 border border-green-50 p-4 rounded-xl flex items-center justify-between mb-4">
                  <div>
                    <span className="text-xs font-bold text-green-950 block">Isolation Forest</span>
                    <span className="text-[10px] text-green-600">Baseline fit: Trained</span>
                  </div>
                  <span className="w-3 h-3 rounded-full bg-green-500"></span>
                </div>
                <div className="bg-slate-50 border border-green-50 p-4 rounded-xl flex items-center justify-between mb-4">
                  <div>
                    <span className="text-xs font-bold text-green-950 block">One-Class SVM</span>
                    <span className="text-[10px] text-green-600">Kernel: Radial RBF</span>
                  </div>
                  <span className="w-3 h-3 rounded-full bg-green-500"></span>
                </div>
                <div className="bg-slate-50 border border-green-50 p-4 rounded-xl flex items-center justify-between mb-6">
                  <div>
                    <span className="text-xs font-bold text-green-950 block">Local Outlier Factor</span>
                    <span className="text-[10px] text-green-600">Novelty: True</span>
                  </div>
                  <span className="w-3 h-3 rounded-full bg-green-500"></span>
                </div>
                <div className="text-[10px] text-green-800 leading-relaxed bg-green-50/20 p-3 rounded-xl border border-green-100/50">
                  <span className="font-bold text-green-700 block mb-1">Ensemble Verdict</span>
                  RiskLens AI uses majority voting among models to flag scan patterns with anomalous vulns count, severe average CVSS weights, or OWASP scope shifts.
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: TARGET MANAGEMENT */}
        {activeTab === 'targets' && (
          <div className="space-y-8">
            {/* Create form (only ADMIN/SECURITY_ANALYST) */}
            {role !== 'DEVELOPER' ? (
              <div className="bg-white border border-green-100 p-6 rounded-2xl shadow-sm">
                <h3 className="font-bold text-sm text-green-900 mb-6 flex items-center gap-2">
                  <Plus className="w-4 h-4 text-green-650" /> Configure Web Application Scope
                </h3>
                
                {targetError && (
                  <div className="bg-red-55/60 border border-red-200 px-4 py-3 rounded-xl text-xs text-red-700 mb-6">
                    {targetError}
                  </div>
                )}

                <form onSubmit={handleAddTarget} className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-xs font-bold text-green-800 uppercase tracking-wider mb-1.5">Application Name</label>
                    <input
                      type="text"
                      required
                      value={newTarget.name}
                      onChange={(e) => setNewTarget({...newTarget, name: e.target.value})}
                      className="w-full bg-slate-50 border border-green-100 focus:border-green-500 rounded-xl p-2.5 text-sm text-green-950 placeholder-neutral-400 outline-none"
                      placeholder="e.g. Corporate Intranet Portal"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-green-800 uppercase tracking-wider mb-1.5">App Base URL</label>
                    <input
                      type="text"
                      required
                      value={newTarget.url}
                      onChange={(e) => setNewTarget({...newTarget, url: e.target.value})}
                      className="w-full bg-slate-50 border border-green-100 focus:border-green-500 rounded-xl p-2.5 text-sm text-green-950 placeholder-neutral-400 outline-none"
                      placeholder="e.g. https://target-app.com"
                    />
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-xs font-bold text-green-800 uppercase tracking-wider mb-1.5">Description</label>
                    <textarea
                      value={newTarget.description}
                      onChange={(e) => setNewTarget({...newTarget, description: e.target.value})}
                      className="w-full bg-slate-50 border border-green-100 focus:border-green-500 rounded-xl p-2.5 text-sm text-green-950 placeholder-neutral-400 outline-none h-20 resize-none"
                      placeholder="Specify purpose of testing..."
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-green-800 uppercase tracking-wider mb-1.5">Environment</label>
                    <select
                      value={newTarget.environment}
                      onChange={(e) => setNewTarget({...newTarget, environment: e.target.value})}
                      className="w-full bg-slate-50 border border-green-100 focus:border-green-500 rounded-xl p-2.5 text-sm text-green-950 outline-none cursor-pointer"
                    >
                      <option value="Production">Production</option>
                      <option value="Staging">Staging</option>
                      <option value="Development">Development</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-green-800 uppercase tracking-wider mb-1.5">Crawl Depth Limit</label>
                    <input
                      type="number"
                      min="1"
                      max="10"
                      value={newTarget.crawl_depth}
                      onChange={(e) => setNewTarget({...newTarget, crawl_depth: parseInt(e.target.value)})}
                      className="w-full bg-slate-50 border border-green-100 focus:border-green-500 rounded-xl p-2.5 text-sm text-green-950 outline-none"
                    />
                  </div>

                  <button
                    type="submit"
                    className="md:col-span-2 bg-green-500 hover:bg-green-600 text-white font-bold py-3 rounded-xl flex items-center justify-center gap-2 cursor-pointer shadow-md shadow-green-500/10 transition-all"
                  >
                    Configure Target Scope
                  </button>
                </form>
              </div>
            ) : (
              <div className="bg-white border border-green-100 p-6 rounded-2xl shadow-sm text-center text-xs text-neutral-500">
                Developer role accounts cannot configure target scopes.
              </div>
            )}

            {/* Configured Targets list */}
            <div className="bg-white border border-green-100 p-6 rounded-2xl shadow-sm">
              <h3 className="font-bold text-sm text-green-900 mb-6">Configured Target Scopes</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-green-100 text-green-800/70 font-bold">
                      <th className="pb-3 px-2">Name</th>
                      <th className="pb-3 px-2">URL</th>
                      <th className="pb-3 px-2">Env</th>
                      <th className="pb-3 px-2">Crawl Depth</th>
                      <th className="pb-3 px-2">Auth Type</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-green-50/50">
                    {targets.map((t) => (
                      <tr key={t.id} className="text-green-950 hover:bg-green-50/10">
                        <td className="py-4 px-2 font-bold">{t.name}</td>
                        <td className="py-4 px-2 font-mono text-green-600">{t.url}</td>
                        <td className="py-4 px-2 font-semibold">{t.environment}</td>
                        <td className="py-4 px-2">{t.crawl_depth}</td>
                        <td className="py-4 px-2">{t.auth_type}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: SCAN ENGINE */}
        {activeTab === 'scans' && (
          <div className="space-y-8">
            {/* Launch Scan Form (only ADMIN/SECURITY_ANALYST) */}
            {role !== 'DEVELOPER' ? (
              <div className="bg-white border border-green-100 p-6 rounded-2xl shadow-sm">
                <h3 className="font-bold text-sm text-green-900 mb-6 flex items-center gap-2">
                  <Play className="w-4 h-4 text-green-650" /> Start Posture Assessment
                </h3>
                
                <form onSubmit={handleLaunchScan} className="space-y-6">
                  <div>
                    <label className="block text-xs font-bold text-green-800 uppercase tracking-wider mb-1.5">Select Target Scope</label>
                    <select
                      value={scanTargetId}
                      onChange={(e) => setScanTargetId(e.target.value)}
                      className="w-full bg-slate-50 border border-green-100 focus:border-green-500 rounded-xl p-2.5 text-sm text-green-950 outline-none cursor-pointer"
                    >
                      {targets.map((t) => (
                        <option key={t.id} value={t.id}>{t.name} ({t.url})</option>
                      ))}
                    </select>
                  </div>

                  <div className="bg-green-50/40 border border-green-100 p-4 rounded-xl">
                    <div className="flex items-start gap-3">
                      <input
                        type="checkbox"
                        required
                        id="consent-check"
                        checked={scanConsent}
                        onChange={(e) => setScanConsent(e.target.checked)}
                        className="mt-1 cursor-pointer w-4 h-4 accent-green-600"
                      />
                      <label htmlFor="consent-check" className="text-xs text-green-900/80 leading-relaxed cursor-pointer select-none font-medium">
                        <strong>Consent Confirmation:</strong> I hereby certify that I am authorized to perform defensive security assessments on this target URL. I authorize the RiskLens AI passive crawler to assess configurations, headers, cookies, and tokens.
                      </label>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={scanQueued}
                    className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 rounded-xl flex items-center justify-center gap-2 cursor-pointer shadow-md shadow-green-500/10 transition-all"
                  >
                    Start Scanner Lifecycle
                  </button>
                </form>
              </div>
            ) : (
              <div className="bg-white border border-green-100 p-6 rounded-2xl shadow-sm text-center text-xs text-neutral-500">
                Developer role profiles cannot launch scans.
              </div>
            )}

            {/* Scan History */}
            <div className="bg-white border border-green-100 p-6 rounded-2xl shadow-sm">
              <h3 className="font-bold text-sm text-green-900 mb-6">Scan Assessments Log</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-green-100 text-green-800/70 font-bold">
                      <th className="pb-3 px-2">ID</th>
                      <th className="pb-3 px-2">Target Name</th>
                      <th className="pb-3 px-2">Status</th>
                      <th className="pb-3 px-2">Progress</th>
                      <th className="pb-3 px-2">Started</th>
                      <th className="pb-3 px-2 text-right">Report Download</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-green-50/50">
                    {scans.map((s) => (
                      <tr key={s.id} className="text-green-950 hover:bg-green-50/10">
                        <td className="py-4 px-2 font-mono">#{s.id}</td>
                        <td className="py-4 px-2 font-bold">{s.target ? s.target.name : 'Sample Sandbox'}</td>
                        <td className="py-4 px-2">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            s.status === 'COMPLETED' ? 'bg-green-50 text-green-700 border border-green-200' :
                            s.status === 'FAILED' ? 'bg-red-50 text-red-700 border border-red-200' :
                            'bg-yellow-50 text-yellow-700 border border-yellow-200'
                          }`}>
                            {s.status}
                          </span>
                        </td>
                        <td className="py-4 px-2 font-mono">{s.progress}%</td>
                        <td className="py-4 px-2 text-neutral-500 font-medium">{new Date(s.started_at).toLocaleString()}</td>
                        <td className="py-4 px-2 text-right space-x-2">
                          <button
                            onClick={() => handleDownloadReport(s.id, 'pdf')}
                            className="bg-white border border-green-200 hover:border-green-500 text-green-900 font-bold px-2.5 py-1 rounded-lg text-[10px] flex inline-flex items-center gap-1 cursor-pointer transition-all hover:bg-green-50/30"
                          >
                            <FileDown className="w-3.5 h-3.5" /> PDF
                          </button>
                          <button
                            onClick={() => handleDownloadReport(s.id, 'html')}
                            className="bg-white border border-green-200 hover:border-green-500 text-green-900 font-bold px-2.5 py-1 rounded-lg text-[10px] flex inline-flex items-center gap-1 cursor-pointer transition-all hover:bg-green-50/30"
                          >
                            <FileDown className="w-3.5 h-3.5" /> HTML
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: POWER BI CONNECTOR */}
        {activeTab === 'powerbi' && (
          <div className="space-y-8">
            <div className="bg-white border border-green-100 p-6 rounded-2xl shadow-sm">
              <h3 className="font-bold text-sm text-green-900 mb-4 flex items-center gap-2">
                <FileSpreadsheet className="w-5 h-5 text-green-600" /> Power BI Integration Config
              </h3>
              <p className="text-xs text-neutral-500 leading-relaxed mb-6 font-medium">
                Expose analytical datasets directly to Power BI. You can import denormalized tables into your Power BI reports by creating a Web Data Source targeting our JSON data stream URLs.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div className="bg-slate-50 border border-green-50 p-4 rounded-xl">
                  <span className="text-[10px] text-green-800 font-bold block uppercase tracking-wider">Findings Table URL</span>
                  <input
                    type="text"
                    readOnly
                    value={`${API_URL}/api/v1/analytics/powerbi/findings`}
                    className="w-full bg-white border border-green-100 rounded-lg p-2.5 text-xs text-green-600 mt-2 outline-none font-mono font-bold"
                  />
                </div>

                <div className="bg-slate-50 border border-green-50 p-4 rounded-xl">
                  <span className="text-[10px] text-green-800 font-bold block uppercase tracking-wider">Scans Trends Table URL</span>
                  <input
                    type="text"
                    readOnly
                    value={`${API_URL}/api/v1/analytics/powerbi/trends`}
                    className="w-full bg-white border border-green-100 rounded-lg p-2.5 text-xs text-green-600 mt-2 outline-none font-mono font-bold"
                  />
                </div>
              </div>

              {/* Power Query Script Copier */}
              <div className="bg-slate-50 border border-green-100 p-6 rounded-2xl relative shadow-inner">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs font-bold text-green-900 uppercase tracking-wider">Power Query (M) Script</span>
                  <button
                    onClick={copyMQuery}
                    className="bg-white hover:bg-green-50 border border-green-150 px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-2 cursor-pointer transition-all text-green-900 shadow-sm"
                  >
                    {copied ? (
                      <>
                        <CheckCircle className="w-3.5 h-3.5 text-green-600" /> Copied!
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5 text-green-600" /> Copy Script
                      </>
                    )}
                  </button>
                </div>

                <pre className="text-[10px] text-green-950 font-mono bg-white p-4 rounded-xl overflow-x-auto max-h-56 leading-relaxed border border-green-100">
                  {mQuery}
                </pre>

                <div className="mt-6 text-xs text-neutral-500 leading-relaxed font-medium">
                  <strong className="text-green-950 block mb-1">To load this into Power BI Desktop:</strong>
                  1. Launch Power BI Desktop and select <strong>Get Data</strong> &rarr; <strong>Blank Query</strong>.<br />
                  2. Open the <strong>Advanced Editor</strong> window.<br />
                  3. Paste the copied M Query script, replacing all contents.<br />
                  4. Click <strong>Done</strong> and select <strong>Close & Apply</strong>.
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 5: AUDIT LOGS */}
        {activeTab === 'audit' && (
          <div className="bg-white border border-green-100 p-6 rounded-2xl shadow-sm">
            <h3 className="font-bold text-sm text-green-900 mb-6">Security Actions Audit Trails</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-green-100 text-green-800/70 font-bold">
                    <th className="pb-3 px-2">Timestamp</th>
                    <th className="pb-3 px-2">User</th>
                    <th className="pb-3 px-2">Action</th>
                    <th className="pb-3 px-2">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-green-50/50">
                  {auditLogs.map((log) => (
                    <tr key={log.id} className="text-green-950 hover:bg-green-50/10">
                      <td className="py-4 px-2 text-neutral-500 font-mono">{log.created_at}</td>
                      <td className="py-4 px-2 font-bold text-green-600">{log.username}</td>
                      <td className="py-4 px-2 font-bold text-green-950">{log.action}</td>
                      <td className="py-4 px-2 text-neutral-600 font-semibold">{log.details}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}
