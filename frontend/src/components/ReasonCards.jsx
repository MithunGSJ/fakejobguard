// src/components/ReasonCards.jsx
import { useState } from 'react';

export default function ReasonCards({ flags, textReasons }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="rounded-2xl bg-slate-800/50 border border-slate-700/50 backdrop-blur-sm p-8 shadow-xl">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-8 h-8 rounded-lg bg-amber-500/20 flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 className="text-lg font-bold text-white">Why This Was Flagged</h3>
      </div>

      {/* SHAP Word Reasons */}
      {textReasons && textReasons.length > 0 && (
        <div className="mb-6">
          <p className="text-sm font-semibold text-slate-400 mb-3 uppercase tracking-wider">
            Suspicious Words Detected
          </p>
          <div className="flex flex-wrap gap-2">
            {textReasons.map((r, i) => (
              <span
                key={i}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 hover:scale-105 cursor-default ${
                  r.impact > 0
                    ? 'bg-red-500/15 text-red-300 border border-red-500/20'
                    : 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/20'
                }`}
              >
                <span className={`w-1.5 h-1.5 rounded-full ${r.impact > 0 ? 'bg-red-400' : 'bg-emerald-400'}`}></span>
                {r.word}
                <span className="text-xs opacity-60">
                  ({r.impact > 0 ? '+' : ''}{r.impact})
                </span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* All Flags */}
      {flags && flags.length > 0 && (
        <div className="space-y-3">
          <p className="text-sm font-semibold text-slate-400 uppercase tracking-wider">
            Analysis Flags
          </p>
          {(expanded ? flags : flags.slice(0, 5)).map((flag, i) => (
            <div
              key={i}
              className="flex items-start gap-3 bg-slate-700/30 border border-slate-600/30 rounded-xl p-4 transition-all duration-200 hover:bg-slate-700/50"
            >
              <span className="mt-0.5">
                {flag.startsWith('[TEXT]') ? '📝' :
                 flag.startsWith('[IMAGE]') ? '🖼️' :
                 flag.startsWith('[URL]') ? '🔗' : '⚡'}
              </span>
              <p className="text-sm text-slate-300 leading-relaxed">{flag}</p>
            </div>
          ))}
          {flags.length > 5 && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="text-sm text-cyan-400 hover:text-cyan-300 font-medium transition-colors"
            >
              {expanded ? '← Show less' : `Show ${flags.length - 5} more flags →`}
            </button>
          )}
        </div>
      )}

      {/* No flags */}
      {(!flags || flags.length === 0) && (!textReasons || textReasons.length === 0) && (
        <div className="flex items-center gap-3 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
          <span className="text-2xl">✅</span>
          <p className="text-emerald-300 font-medium">No suspicious signals detected. This posting appears safe.</p>
        </div>
      )}
    </div>
  );
}
