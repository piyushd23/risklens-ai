import React from 'react';
import { Link } from 'react-router-dom';
import Logo from '../components/Logo';
import { Shield, Search, Cpu, BarChart3, Download, Layers, ArrowRight } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-50 text-green-950 selection:bg-green-100 selection:text-green-900 overflow-x-hidden">
      
      {/* NAVBAR */}
      <nav className="fixed top-0 left-0 w-full z-50 bg-white/80 backdrop-blur-md border-b border-green-100 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          {/* We'll pass a custom text-color override for Logo in light mode */}
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

          <div className="flex items-center gap-6">
            <Link to="/login" className="text-sm font-semibold text-green-900 hover:text-green-600 transition-colors">
              Sign In
            </Link>
            <Link
              to="/register"
              className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-bold shadow-md shadow-green-500/10 transition-all hover:scale-[1.02]"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* HERO SECTION */}
      <section className="relative pt-36 pb-20 px-6 max-w-7xl mx-auto flex flex-col lg:flex-row items-center gap-16">
        <div className="absolute inset-0 -z-10 flex items-center justify-center">
          <div className="w-[400px] h-[400px] bg-green-200/40 blur-[120px] rounded-full animate-pulse-soft"></div>
        </div>
        
        <div className="flex-1 text-center lg:text-left">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-green-50 border border-green-200/50 text-green-800 text-xs font-semibold mb-6">
            <Shield className="w-3.5 h-3.5 text-green-600" /> AI-Driven Defensive DAST Platform
          </div>
          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-none mb-6 text-green-950">
            Intelligent Security <br />
            <span className="bg-gradient-to-r from-green-600 to-emerald-700 bg-clip-text text-transparent">
              Assessment.
            </span>
          </h1>
          <p className="text-base text-neutral-600 max-w-xl mb-8 leading-relaxed">
            Assess web application security posture, map findings to OWASP standards, calculate CVSS vectors, and prioritize remediations using machine learning.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4">
            <Link
              to="/register"
              className="w-full sm:w-auto bg-green-500 hover:bg-green-650 text-white px-8 py-4 rounded-xl font-bold shadow-lg shadow-green-500/20 flex items-center justify-center gap-2 transition-all hover:scale-[1.02]"
            >
              Start Free Scan <ArrowRight className="w-4 h-4" />
            </Link>
            <a
              href="#features"
              className="w-full sm:w-auto bg-white border border-green-200 hover:bg-green-50/50 text-green-900 px-8 py-4 rounded-xl font-semibold flex items-center justify-center transition-all"
            >
              Learn More
            </a>
          </div>
        </div>

        {/* HERO INTERACTIVE WIDGET PREVIEW */}
        <div className="flex-1 w-full max-w-xl">
          <div className="glass-panel rounded-3xl p-6 border border-green-200 shadow-xl relative overflow-hidden bg-white/95">
            {/* Top Bar */}
            <div className="flex items-center justify-between pb-4 border-b border-green-100 mb-6">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-red-400"></span>
                <span className="w-3 h-3 rounded-full bg-yellow-400"></span>
                <span className="w-3 h-3 rounded-full bg-green-400"></span>
              </div>
              <span className="text-xs text-neutral-400 font-mono">sec-core-dashboard-preview.json</span>
            </div>

            {/* Score Ring Section */}
            <div className="flex flex-col sm:flex-row items-center gap-8 mb-6">
              <div className="relative w-36 h-36 flex items-center justify-center bg-green-50/30 rounded-full border border-green-200/50">
                <div className="absolute inset-2 rounded-full border-4 border-dashed border-green-500/20 animate-spin" style={{ animationDuration: '30s' }}></div>
                <div className="text-center z-10">
                  <span className="text-4xl font-extrabold text-green-800">92.4</span>
                  <span className="block text-[10px] uppercase tracking-wider text-green-700 mt-1 font-bold">Posture Score</span>
                </div>
              </div>
              
              <div className="flex-1 space-y-3 w-full">
                <div className="bg-green-50/20 p-3 rounded-lg border border-green-100/50">
                  <div className="flex justify-between text-xs mb-1 font-semibold">
                    <span className="text-green-900">OWASP A05 Compliance</span>
                    <span className="text-green-600">100%</span>
                  </div>
                  <div className="w-full bg-neutral-200 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-green-500 h-full w-full"></div>
                  </div>
                </div>

                <div className="bg-green-50/20 p-3 rounded-lg border border-green-100/50">
                  <div className="flex justify-between text-xs mb-1 font-semibold">
                    <span className="text-green-900">SSL/TLS Configuration</span>
                    <span className="text-green-600">80%</span>
                  </div>
                  <div className="w-full bg-neutral-200 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-green-500 h-full w-[80%]"></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Vulnerabilities Mock Table */}
            <div className="space-y-2">
              <div className="text-[10px] font-bold text-green-800 uppercase tracking-widest mb-2">Live AI Prioritised Threats</div>
              
              <div className="bg-red-50 border border-red-200 px-4 py-2.5 rounded-lg flex items-center justify-between">
                <div>
                  <span className="text-xs font-bold block text-red-950">Exposed Private SSL Keys</span>
                  <span className="text-[10px] text-red-750">OWASP A02 &bull; CVSS 7.5</span>
                </div>
                <span className="bg-red-100 text-red-800 border border-red-200 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider">AI Priority: 84.5</span>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 px-4 py-2.5 rounded-lg flex items-center justify-between">
                <div>
                  <span className="text-xs font-bold block text-yellow-950">Missing Clickjacking Protections</span>
                  <span className="text-[10px] text-yellow-750">OWASP A05 &bull; CVSS 4.7</span>
                </div>
                <span className="bg-yellow-100 text-yellow-800 border border-yellow-200 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider">AI Priority: 58.2</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES SECTION */}
      <section id="features" className="py-20 bg-white px-6 border-y border-green-100">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-xl mx-auto mb-16">
            <h2 className="text-3xl font-extrabold mb-4 text-green-950">Complete Defensive DAST Pipeline</h2>
            <p className="text-neutral-500 text-sm">
              Discover, assess, and audit security layers using deep contextual analyses, machine learning, and automated threat score calculations.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-slate-50 border border-green-50 hover:border-green-300 p-6 rounded-2xl transition-all hover:scale-[1.01] shadow-sm">
              <Search className="w-10 h-10 text-green-600 mb-4" />
              <h3 className="font-bold text-lg mb-2 text-green-950">Intelligent Discovery</h3>
              <p className="text-neutral-600 text-sm leading-relaxed">
                Asynchronous crawling engine scans pages, maps links, discovers forms, and audits input arguments to catalog sitemap structure.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-slate-50 border border-green-50 hover:border-green-300 p-6 rounded-2xl transition-all hover:scale-[1.01] shadow-sm">
              <Shield className="w-10 h-10 text-green-600 mb-4" />
              <h3 className="font-bold text-lg mb-2 text-green-950">Security Posture Audits</h3>
              <p className="text-neutral-600 text-sm leading-relaxed">
                Evaluates response headers (CSP, HSTS, X-Frame), secure session cookie properties (HttpOnly, Secure, SameSite), and CSRF tokens.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-slate-50 border border-green-50 hover:border-green-300 p-6 rounded-2xl transition-all hover:scale-[1.01] shadow-sm">
              <Layers className="w-10 h-10 text-green-600 mb-4" />
              <h3 className="font-bold text-lg mb-2 text-green-950">OWASP & CVSS Alignment</h3>
              <p className="text-neutral-600 text-sm leading-relaxed">
                Automatically maps findings directly to OWASP Top 10 vulnerabilities and calculates exact CVSS 3.1 severity scores.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="bg-slate-50 border border-green-50 hover:border-green-300 p-6 rounded-2xl transition-all hover:scale-[1.01] shadow-sm">
              <Cpu className="w-10 h-10 text-green-600 mb-4" />
              <h3 className="font-bold text-lg mb-2 text-green-950">AI Risk Prioritization</h3>
              <p className="text-neutral-600 text-sm leading-relaxed">
                Uses machine learning to rank remediation queues by combining asset criticality, CVSS scores, threat frequency, and logs.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="bg-slate-50 border border-green-50 hover:border-green-300 p-6 rounded-2xl transition-all hover:scale-[1.01] shadow-sm">
              <BarChart3 className="w-10 h-10 text-green-600 mb-4" />
              <h3 className="font-bold text-lg mb-2 text-green-950">Ensemble Anomalies</h3>
              <p className="text-neutral-600 text-sm leading-relaxed">
                Utilizes Isolation Forest, One-Class SVM, and LOF classifiers to flag deviant vulnerability frequencies and outliers.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="bg-slate-50 border border-green-50 hover:border-green-300 p-6 rounded-2xl transition-all hover:scale-[1.01] shadow-sm">
              <Download className="w-10 h-10 text-green-600 mb-4" />
              <h3 className="font-bold text-lg mb-2 text-green-950">Streaming Report Engine</h3>
              <p className="text-neutral-600 text-sm leading-relaxed">
                Generates high-fidelity PDF, HTML, and JSON reports with automated download file streaming and client progress trackers.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="py-20 max-w-7xl mx-auto px-6">
        <div className="text-center max-w-xl mx-auto mb-16">
          <h2 className="text-3xl font-extrabold mb-4 text-green-950">How RiskLens AI Works</h2>
          <p className="text-neutral-500 text-sm">
            Five streamlined steps to evaluate vulnerability posture and protect web assets.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-8">
          {[
            { step: "01", title: "Add Target", desc: "Configure application URL, crawler scope boundaries, and access methods." },
            { step: "02", title: "Discover Assets", desc: "Map directories, forms, files, and dynamic inputs automatically." },
            { step: "03", title: "Assess Posture", desc: "Evaluate response configuration vectors and cookies." },
            { step: "04", title: "Analyze Risks", desc: "Use AI classifiers to determine remediation priorities and action items." },
            { step: "05", title: "Generate Reports", desc: "Download PDF, JSON summaries, or query BI connector streams." },
          ].map((obj, i) => (
            <div key={i} className="bg-white border border-green-100 p-6 rounded-2xl relative shadow-sm">
              <span className="text-4xl font-extrabold text-green-500/10 absolute top-4 right-4">{obj.step}</span>
              <h4 className="font-bold text-base mb-2 mt-4 text-green-950">{obj.title}</h4>
              <p className="text-neutral-500 text-xs leading-relaxed">{obj.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t border-green-100 bg-white py-12 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
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

          <div className="flex flex-wrap justify-center gap-6 text-sm text-green-900/60 font-semibold">
            <span className="hover:text-green-600 transition-colors cursor-pointer">About</span>
            <span className="hover:text-green-600 transition-colors cursor-pointer">Features</span>
            <span className="hover:text-green-600 transition-colors cursor-pointer">Documentation</span>
            <span className="hover:text-green-600 transition-colors cursor-pointer">Privacy Policy</span>
          </div>
          <div className="text-xs text-neutral-450 text-center md:text-right font-medium">
            &copy; {new Date().getFullYear()} RiskLens AI. Defensive cybersecurity platform.
          </div>
        </div>
      </footer>
    </div>
  );
}
