import React from 'react';

export default function Logo({ className = "w-10 h-10", showText = true }) {
  return (
    <div className="flex items-center gap-3 select-none">
      <svg
        className={className}
        viewBox="0 0 200 200"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Outer Tech Shield */}
        <path
          d="M100 20C135 20 170 30 170 30V100C170 145 135 175 100 185C65 175 30 145 30 100V30C30 30 65 20 100 20Z"
          stroke="#22C55E"
          strokeWidth="8"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="#0A2F1D"
          fillOpacity="0.8"
        />

        {/* AI Network Grid Nodes */}
        <circle cx="100" cy="55" r="5" fill="#4ADE80" />
        <circle cx="70" cy="90" r="5" fill="#4ADE80" />
        <circle cx="130" cy="90" r="5" fill="#4ADE80" />
        <circle cx="100" cy="125" r="5" fill="#4ADE80" />

        {/* Node Interconnection Lines */}
        <line x1="100" y1="55" x2="70" y2="90" stroke="#22C55E" strokeWidth="2" strokeDasharray="3 3" />
        <line x1="100" y1="55" x2="130" y2="90" stroke="#22C55E" strokeWidth="2" strokeDasharray="3 3" />
        <line x1="70" y1="90" x2="100" y2="125" stroke="#22C55E" strokeWidth="2" strokeDasharray="3 3" />
        <line x1="130" y1="90" x2="100" y2="125" stroke="#22C55E" strokeWidth="2" strokeDasharray="3 3" />
        <line x1="100" y1="55" x2="100" y2="125" stroke="#22C55E" strokeWidth="1" />

        {/* Cybersecurity Lens Overlay */}
        <circle
          cx="100"
          cy="95"
          r="30"
          stroke="#4ADE80"
          strokeWidth="6"
          fill="none"
          strokeDasharray="90 10"
        />
        {/* Lens Handle */}
        <line
          x1="121"
          y1="116"
          x2="140"
          y2="135"
          stroke="#4ADE80"
          strokeWidth="6"
          strokeLinecap="round"
        />
      </svg>
      {showText && (
        <span className="font-extrabold text-2xl tracking-tight bg-gradient-to-r from-emerald-400 to-green-600 bg-clip-text text-transparent">
          RiskLens<span className="text-white">AI</span>
        </span>
      )}
    </div>
  );
}
