import React from 'react';
import { SiteHeader } from '../../shared/SiteHeader';
import { SiteFooter } from '../../shared/SiteFooter';
import { Button } from '../../shared/Button';

export const Architecture: React.FC = () => {
  return (
    <div className="theme-site min-h-screen flex flex-col justify-between bg-site-bg text-site-text-primary">
      <SiteHeader />
      <main className="max-w-4xl mx-auto px-6 py-20 flex-1 flex flex-col justify-center">
        <div className="inline-block px-2.5 py-1 mb-6 text-xs font-mono uppercase tracking-wider bg-site-surface border border-site-border rounded-site text-site-text-secondary w-max">
          [PAGE SKELETON // ARCHITECTURE]
        </div>
        <h1 className="text-4xl sm:text-5xl font-serif font-bold text-site-text-primary mb-4 leading-tight">
          System Architecture & Graph Engine
        </h1>
        <p className="text-lg text-site-text-secondary font-sans max-w-2xl mb-8 leading-relaxed">
          Architecture page skeleton ready for Task 8.5 implementation. Will feature the six-stage multi-agent pipeline diagram and bounded recalibration loops.
        </p>
        <div className="flex items-center gap-4">
          <Button to="/dashboard" variant="primary">
            Enter Dashboard
          </Button>
          <Button to="/" variant="secondary">
            Back to Home
          </Button>
        </div>
      </main>
      <SiteFooter />
    </div>
  );
};