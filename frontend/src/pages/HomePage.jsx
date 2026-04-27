// src/pages/HomePage.jsx
import { Link } from 'react-router-dom';

export default function HomePage() {
  const features = [
    {
      icon: '📝',
      title: 'Text Analysis',
      desc: 'Paste any job posting. Our BERT-powered NLP engine analyzes language patterns, suspicious phrasing, and scam indicators.',
      color: 'from-cyan-500 to-blue-600',
    },
    {
      icon: '🖼️',
      title: 'Image Detection',
      desc: 'Upload a job ad screenshot. Our CLIP vision model detects fake logos, stock photos, and suspicious visual patterns.',
      color: 'from-purple-500 to-pink-600',
    },
    {
      icon: '🔗',
      title: 'URL Verification',
      desc: 'Enter a job URL. We check domain age, SSL certificates, redirect chains, and Google Safe Browsing database.',
      color: 'from-amber-500 to-orange-600',
    },
  ];

  const stats = [
    { value: '99%+', label: 'Detection Accuracy' },
    { value: '17.8K', label: 'Training Samples' },
    { value: '3', label: 'AI Models Combined' },
    { value: '<5s', label: 'Analysis Time' },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900"></div>
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-cyan-500/5 rounded-full blur-3xl"></div>

        <div className="relative max-w-7xl mx-auto px-6 py-24 lg:py-36">
          <div className="text-center max-w-4xl mx-auto">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-sm font-medium mb-8 backdrop-blur-sm">
              <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
              AI-Powered Job Fraud Detection
            </div>

            {/* Heading */}
            <h1 className="text-5xl lg:text-7xl font-black text-white mb-6 leading-tight">
              Don't Fall For{' '}
              <span className="bg-gradient-to-r from-cyan-300 via-blue-400 to-purple-400 bg-clip-text text-transparent">
                Fake Jobs
              </span>
            </h1>

            <p className="text-xl text-slate-400 mb-10 leading-relaxed max-w-2xl mx-auto">
              Millions of fake job postings go live every month. Our AI scans text, images, and URLs
              to give you a <span className="text-white font-semibold">Risk Score in seconds</span> — protecting
              your data, your money, and your time.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to="/analyze"
                className="group inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold rounded-2xl shadow-2xl shadow-blue-500/25 hover:shadow-blue-500/40 transition-all duration-300 hover:scale-105 text-lg"
              >
                Start Analyzing
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </Link>
              <a
                href="#features"
                className="inline-flex items-center gap-2 px-8 py-4 text-slate-400 hover:text-white font-semibold rounded-2xl border border-slate-700 hover:border-slate-500 transition-all duration-300 text-lg"
              >
                Learn More
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Bar */}
      <section className="relative bg-slate-800/50 border-y border-slate-700/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {stats.map((stat, i) => (
              <div key={i} className="text-center">
                <p className="text-3xl font-black bg-gradient-to-r from-cyan-300 to-blue-400 bg-clip-text text-transparent">
                  {stat.value}
                </p>
                <p className="text-sm text-slate-500 mt-1 font-medium">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="relative bg-slate-900 py-24">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-white mb-4">
              Three Layers of AI Protection
            </h2>
            <p className="text-slate-400 text-lg max-w-2xl mx-auto">
              Our system combines NLP, computer vision, and URL analysis to provide comprehensive fraud detection.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, i) => (
              <div
                key={i}
                className="group relative rounded-2xl bg-slate-800/50 border border-slate-700/50 p-8 hover:border-slate-600/50 transition-all duration-500 hover:-translate-y-2 hover:shadow-2xl"
              >
                {/* Gradient top border effect */}
                <div className={`absolute inset-x-0 top-0 h-1 bg-gradient-to-r ${feature.color} rounded-t-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500`}></div>
                
                <span className="text-4xl mb-4 block">{feature.icon}</span>
                <h3 className="text-xl font-bold text-white mb-3">{feature.title}</h3>
                <p className="text-slate-400 leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="relative bg-slate-950 py-24">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-white mb-4">
              How It Works
            </h2>
            <p className="text-slate-400 text-lg">Simple 3-step process to verify any job posting</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {[
              { step: '01', title: 'Input', desc: 'Paste job text, upload an ad screenshot, or enter a URL — or all three at once.' },
              { step: '02', title: 'AI Analysis', desc: 'BERT analyzes text, CLIP scans images, and our URL checker verifies links.' },
              { step: '03', title: 'Risk Score', desc: 'Get a 0–100 risk score with detailed SHAP explanations of why it was flagged.' },
            ].map((item, i) => (
              <div key={i} className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/20 mb-6">
                  <span className="text-xl font-black bg-gradient-to-r from-cyan-300 to-blue-400 bg-clip-text text-transparent">
                    {item.step}
                  </span>
                </div>
                <h3 className="text-lg font-bold text-white mb-2">{item.title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>

          <div className="text-center mt-16">
            <Link
              to="/analyze"
              className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold rounded-2xl shadow-2xl shadow-blue-500/25 hover:shadow-blue-500/40 transition-all duration-300 hover:scale-105"
            >
              Try It Now — Free
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 border-t border-slate-800 py-8">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <p className="text-slate-500 text-sm">
            Built with BERT • CLIP • FastAPI • React — Fake Job Posting Detection System
          </p>
        </div>
      </footer>
    </div>
  );
}
