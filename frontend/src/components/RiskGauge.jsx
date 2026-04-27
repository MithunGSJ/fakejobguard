// src/components/RiskGauge.jsx
import { useEffect, useState } from 'react';

export default function RiskGauge({ score, label, color }) {
  const [animatedScore, setAnimatedScore] = useState(0);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
    // Animate score counting up
    const duration = 1200;
    const steps = 60;
    const increment = score / steps;
    let current = 0;
    const timer = setInterval(() => {
      current += increment;
      if (current >= score) {
        setAnimatedScore(score);
        clearInterval(timer);
      } else {
        setAnimatedScore(Math.round(current));
      }
    }, duration / steps);
    return () => clearInterval(timer);
  }, [score]);

  const colorConfig = {
    green: {
      bg: 'from-emerald-500/10 to-green-500/10',
      border: 'border-emerald-500/30',
      text: 'text-emerald-400',
      bar: 'from-emerald-400 to-green-500',
      glow: 'shadow-emerald-500/20',
      icon: '✅',
      bgBar: 'bg-emerald-900/30',
    },
    orange: {
      bg: 'from-amber-500/10 to-orange-500/10',
      border: 'border-amber-500/30',
      text: 'text-amber-400',
      bar: 'from-amber-400 to-orange-500',
      glow: 'shadow-amber-500/20',
      icon: '⚠️',
      bgBar: 'bg-amber-900/30',
    },
    red: {
      bg: 'from-red-500/10 to-rose-500/10',
      border: 'border-red-500/30',
      text: 'text-red-400',
      bar: 'from-red-400 to-rose-600',
      glow: 'shadow-red-500/20',
      icon: '🚨',
      bgBar: 'bg-red-900/30',
    },
  };

  const c = colorConfig[color] || colorConfig.green;

  return (
    <div
      className={`relative rounded-2xl p-8 bg-gradient-to-br ${c.bg} border ${c.border} backdrop-blur-sm shadow-2xl ${c.glow} transform transition-all duration-700 ${
        isVisible ? 'translate-y-0 opacity-100' : 'translate-y-8 opacity-0'
      }`}
    >
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{c.icon}</span>
          <h2 className="text-xl font-bold text-white">Risk Assessment</h2>
        </div>
        <span className={`text-lg font-bold px-4 py-1.5 rounded-full ${c.text} bg-black/30 border ${c.border}`}>
          {label}
        </span>
      </div>

      {/* Score Display */}
      <div className="flex items-center gap-6">
        <div className="relative">
          <span className={`text-7xl font-black ${c.text} tabular-nums tracking-tight`}>
            {animatedScore}
          </span>
          <span className="text-2xl text-slate-500 font-light">/100</span>
        </div>
        <div className="flex-1">
          <div className={`w-full ${c.bgBar} rounded-full h-4 overflow-hidden`}>
            <div
              className={`h-4 rounded-full bg-gradient-to-r ${c.bar} transition-all duration-1000 ease-out shadow-lg`}
              style={{ width: `${animatedScore}%` }}
            />
          </div>
          <p className="text-xs text-slate-500 mt-2 tracking-wide">
            Risk Score — 0 = Safe, 100 = Definite Scam
          </p>
        </div>
      </div>
    </div>
  );
}
