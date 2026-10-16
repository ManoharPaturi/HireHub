/*
 * Optional animated loading screen. The progress timer is visual and is not
 * connected to API/database readiness. The current App entry point does not
 * mount this component.
 */

import React, { useEffect, useState } from 'react';
import { Briefcase, Sparkles, Code2, Rocket } from 'lucide-react';

interface SplashScreenProps {
  onComplete: () => void;
}

export const SplashScreen: React.FC<SplashScreenProps> = ({ onComplete }) => {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(timer);
          setTimeout(onComplete, 400);
          return 100;
        }
        return prev + 5;
      });
    }, 35);
    return () => clearInterval(timer);
  }, [onComplete]);

  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center overflow-hidden select-none" style={{ background: 'var(--bg)' }}>
      <div className="absolute -top-40 -left-40 w-96 h-96 rounded-full blur-3xl animate-pulse-glow" style={{ background: 'var(--primary-soft)' }} />
      <div className="absolute -bottom-40 -right-40 w-96 h-96 rounded-full blur-3xl animate-pulse-glow" style={{ background: 'color-mix(in srgb, var(--accent) 12%, transparent)' }} />

      <div className="relative mb-8 flex items-center justify-center animate-float">
        <div className="w-24 h-24 rounded-3xl flex items-center justify-center text-white shadow-2xl" style={{ background: 'linear-gradient(135deg, var(--primary), var(--accent))', boxShadow: 'var(--shadow-glow)' }}>
          <Briefcase className="w-12 h-12" strokeWidth={2.2} />
        </div>
        <div className="absolute -top-2 -right-2 p-1.5 rounded-xl text-white font-bold shadow-lg flex items-center gap-1 text-xs" style={{ background: 'linear-gradient(135deg, #fbbf24, #f97316)' }}>
          <Sparkles className="w-3.5 h-3.5" /> PRO
        </div>
      </div>

      <h1 className="text-4xl font-extrabold tracking-tight mb-2" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
        Hire<span style={{ color: 'var(--primary)' }}>Hub</span>
      </h1>
      <p className="text-sm font-medium mb-10 flex items-center gap-2" style={{ color: 'var(--muted)' }}>
        <Code2 className="w-4 h-4" style={{ color: 'var(--primary)' }} /> Where careers begin
      </p>

      <div className="w-72 rounded-full overflow-hidden p-0.5 mb-3" style={{ background: 'var(--surface-3)' }}>
        <div className="h-2.5 rounded-full transition-all duration-200 ease-out" style={{ width: `${progress}%`, background: 'linear-gradient(90deg, var(--primary), var(--accent))' }} />
      </div>

      <div className="flex items-center gap-2 text-xs font-medium" style={{ color: 'var(--muted)' }}>
        <Rocket className="w-3.5 h-3.5 animate-bounce" style={{ color: 'var(--primary)' }} />
        Loading ({progress}%)
      </div>
    </div>
  );
};
