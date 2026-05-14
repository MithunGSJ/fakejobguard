// src/pages/AnalyzePage.jsx
import { useState, useRef } from 'react';
import { analyzeAll } from '../api/analyzeApi';
import RiskGauge from '../components/RiskGauge';
import ReasonCards from '../components/ReasonCards';

export default function AnalyzePage() {
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('text');
  const resultRef = useRef(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => setImagePreview(reader.result);
      reader.readAsDataURL(file);
    }
  };

  const clearImage = () => {
    setImageFile(null);
    setImagePreview(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text && !url && !imageFile) {
      setError('Please provide at least one input: text, URL, or image');
      return;
    }
    // Warn if text is the only input and it's too short
    const wordCount = text.trim().split(/\s+/).filter(Boolean).length;
    if (text && !url && !imageFile && wordCount < 10) {
      setError(`Text too short (${wordCount} word${wordCount === 1 ? '' : 's'}). Please paste the full job posting — minimum 10 words for accurate analysis.`);
      return;
    }
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const data = await analyzeAll({ text, url, imageFile });
      setResult(data);
      // Scroll to results
      setTimeout(() => {
        resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 200);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Analysis failed. Make sure the backend is running at http://localhost:8000'
      );
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'text', label: '📝 Text', icon: '📝' },
    { id: 'url', label: '🔗 URL', icon: '🔗' },
    { id: 'image', label: '🖼️ Image', icon: '🖼️' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950">
      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-4xl font-black text-white mb-3">
            Analyze a Job Posting
          </h1>
          <p className="text-slate-400 text-lg max-w-xl mx-auto">
            Paste the job text, enter a URL, or upload an image — or all three for maximum accuracy.
          </p>
        </div>

        {/* Analysis Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Tab Switcher */}
          <div className="flex gap-2 bg-slate-800/50 p-1.5 rounded-xl border border-slate-700/50">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 py-3 px-4 rounded-lg text-sm font-semibold transition-all duration-300 ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-cyan-500/20 to-blue-600/20 text-cyan-300 border border-cyan-500/20 shadow-lg'
                    : 'text-slate-500 hover:text-slate-300 hover:bg-slate-700/30'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Text Input */}
          <div className={`transition-all duration-300 ${activeTab === 'text' ? 'block' : 'hidden'}`}>
            <div className="rounded-2xl bg-slate-800/50 border border-slate-700/50 p-6 backdrop-blur-sm">
              <label className="block text-sm font-bold text-slate-300 mb-3">
                Job Post Text
              </label>
              <textarea
                id="text-input"
                className="w-full bg-slate-900/70 border border-slate-600/50 rounded-xl p-4 h-48 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500/50 resize-none transition-all"
                placeholder="Paste the full job posting text here...&#10;&#10;Example: 'Work from home earn Rs.50000/month no experience needed apply now WhatsApp 9876543210'"
                value={text}
                onChange={(e) => setText(e.target.value)}
              />
              <p className={`text-xs mt-2 transition-colors ${
                text.length === 0 ? 'text-slate-600' :
                text.trim().split(/\s+/).filter(Boolean).length < 10 ? 'text-amber-500' : 'text-emerald-500'
              }`}>
                {text.trim().split(/\s+/).filter(Boolean).length > 0
                  ? `${text.trim().split(/\s+/).filter(Boolean).length} words${text.trim().split(/\s+/).filter(Boolean).length < 10 ? ' — need at least 10 for accurate results' : ' ✓ ready to analyze'}`
                  : 'Paste the complete job description for best results'
                }
              </p>
            </div>
          </div>

          {/* URL Input */}
          <div className={`transition-all duration-300 ${activeTab === 'url' ? 'block' : 'hidden'}`}>
            <div className="rounded-2xl bg-slate-800/50 border border-slate-700/50 p-6 backdrop-blur-sm">
              <label className="block text-sm font-bold text-slate-300 mb-3">
                Job / Ad URL
              </label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">🔗</span>
                <input
                  id="url-input"
                  type="text"
                  className="w-full bg-slate-900/70 border border-slate-600/50 rounded-xl pl-10 pr-4 py-4 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500/50 transition-all"
                  placeholder="https://www.example.com/jobs/12345"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                />
              </div>
              <p className="text-xs text-slate-600 mt-2">
                We check domain age, SSL, Safe Browsing database, and redirect patterns
              </p>
            </div>
          </div>

          {/* Image Upload */}
          <div className={`transition-all duration-300 ${activeTab === 'image' ? 'block' : 'hidden'}`}>
            <div className="rounded-2xl bg-slate-800/50 border border-slate-700/50 p-6 backdrop-blur-sm">
              <label className="block text-sm font-bold text-slate-300 mb-3">
                Ad Screenshot
              </label>
              {!imagePreview ? (
                <label
                  htmlFor="image-input"
                  className="flex flex-col items-center justify-center w-full h-48 bg-slate-900/70 border-2 border-dashed border-slate-600/50 rounded-xl cursor-pointer hover:border-cyan-500/50 hover:bg-slate-900 transition-all duration-300"
                >
                  <span className="text-4xl mb-3">📸</span>
                  <span className="text-sm text-slate-400 font-medium">Click to upload or drag an image</span>
                  <span className="text-xs text-slate-600 mt-1">PNG, JPG, WEBP up to 10MB</span>
                  <input
                    id="image-input"
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={handleImageChange}
                  />
                </label>
              ) : (
                <div className="relative rounded-xl overflow-hidden bg-slate-900/70">
                  <img src={imagePreview} alt="Preview" className="w-full h-48 object-contain" />
                  <button
                    type="button"
                    onClick={clearImage}
                    className="absolute top-3 right-3 w-8 h-8 bg-red-500/80 hover:bg-red-500 text-white rounded-lg flex items-center justify-center transition-colors text-sm font-bold"
                  >
                    ✕
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Active Inputs Indicator */}
          <div className="flex items-center gap-3 flex-wrap">
            <span className="text-xs text-slate-600 font-medium">Active inputs:</span>
            {text && (
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-cyan-500/10 text-cyan-400 text-xs border border-cyan-500/20">
                📝 Text ({text.length} chars)
              </span>
            )}
            {url && (
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-purple-500/10 text-purple-400 text-xs border border-purple-500/20">
                🔗 URL
              </span>
            )}
            {imageFile && (
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-amber-500/10 text-amber-400 text-xs border border-amber-500/20">
                🖼️ {imageFile.name}
              </span>
            )}
            {!text && !url && !imageFile && (
              <span className="text-xs text-slate-600 italic">None — provide at least one input</span>
            )}
          </div>

          {/* Error */}
          {error && (
            <div className="flex items-start gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/20">
              <span className="text-xl">❌</span>
              <p className="text-sm text-red-300">{error}</p>
            </div>
          )}

          {/* Submit Button */}
          <button
            id="analyze-button"
            type="submit"
            disabled={loading}
            className="w-full relative overflow-hidden bg-gradient-to-r from-cyan-500 to-blue-600 text-white py-4 rounded-2xl font-bold text-lg shadow-2xl shadow-blue-500/25 hover:shadow-blue-500/40 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]"
          >
            {loading ? (
              <span className="inline-flex items-center gap-3">
                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
                Analyzing with AI...
              </span>
            ) : (
              'Analyze Job Posting'
            )}
          </button>
        </form>

        {/* Results Section */}
        {result && (
          <div ref={resultRef} className="mt-12 space-y-6 animate-fadeIn">
            <div className="flex items-center gap-3 mb-2">
              <div className="h-px flex-1 bg-gradient-to-r from-transparent via-slate-700 to-transparent"></div>
              <span className="text-sm font-bold text-slate-500 uppercase tracking-widest">Results</span>
              <div className="h-px flex-1 bg-gradient-to-r from-transparent via-slate-700 to-transparent"></div>
            </div>

            {/* Warning banner — shown when backend detects non-job text */}
            {result.text_analysis?.warning && (
              <div className="flex items-start gap-3 p-4 rounded-xl bg-amber-500/10 border border-amber-500/30">
                <span className="text-2xl">⚠️</span>
                <div>
                  <p className="text-sm font-bold text-amber-400 mb-1">Input Notice</p>
                  <p className="text-sm text-amber-300/80">{result.text_analysis.warning}</p>
                </div>
              </div>
            )}

            <RiskGauge
              score={result.final_result.final_score}
              label={result.final_result.label}
              color={result.final_result.color}
            />
            <ReasonCards
              flags={result.final_result.flags}
              textReasons={result.text_analysis?.top_reasons}
            />

            {/* Component Breakdown */}
            {result.final_result.components && Object.keys(result.final_result.components).length > 0 && (
              <div className="rounded-2xl bg-slate-800/50 border border-slate-700/50 p-8 backdrop-blur-sm">
                <h3 className="text-lg font-bold text-white mb-4">Score Breakdown</h3>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {Object.entries(result.final_result.components).map(([key, value]) => (
                    <div key={key} className="rounded-xl bg-slate-900/50 border border-slate-700/30 p-4 text-center">
                      <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">
                        {key === 'text' ? '📝 Text' : key === 'image' ? '🖼️ Image' : '🔗 URL'}
                      </p>
                      <p className={`text-3xl font-black ${
                        value >= 70 ? 'text-red-400' :
                        value >= 40 ? 'text-amber-400' : 'text-emerald-400'
                      }`}>
                        {value}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
