import React, { useState } from 'react';
import { Link, NavLink, useLocation } from 'react-router-dom';
import { Button } from './Button';
import { ArrowLeft, Menu, Terminal, X } from 'lucide-react';

export interface SiteHeaderProps {
  variant?: 'light' | 'dark-collapsed';
}

export const SiteHeader: React.FC<SiteHeaderProps> = ({ variant }) => {
  const location = useLocation();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const isDashboard = variant ? variant === 'dark-collapsed' : location.pathname.startsWith('/dashboard');

  if (isDashboard) {
    return (
      <header className="sticky top-0 z-50 w-full bg-[#0E1013] border-b border-[#23272F] text-[#E6EDF3] transition-colors duration-200">
        <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
          <Link to="/dashboard" className="flex items-center gap-2.5 group">
            <div className="w-7 h-7 rounded bg-[#1A1E24] border border-[#2D333B] flex items-center justify-center text-site-accent">
              <Terminal className="w-4 h-4" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="font-mono font-bold tracking-wider text-sm text-[#F0F6FC]">
                HELIOS_TERMINAL
              </span>
              <span className="text-[10px] font-mono uppercase tracking-widest text-[#7D8590] hidden sm:inline">
                [SOVEREIGN_CORE]
              </span>
            </div>
          </Link>

          <Link
            to="/"
            className="flex items-center gap-1.5 text-xs font-mono text-site-accent hover:text-[#56D4DD] transition-colors py-1 px-2 rounded hover:bg-[#161B22]"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Overview</span>
          </Link>
        </div>
      </header>
    );
  }

  const navLinks = [
    { name: 'Home', path: '/' },
    { name: 'Architecture', path: '/architecture' },
    { name: 'About', path: '/about' },
    { name: 'Team', path: '/team' },
  ];

  return (
    <header className="sticky top-0 z-50 w-full bg-site-bg/95 backdrop-blur-sm border-b border-site-border transition-colors duration-200">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
        {/* Logo and Wordmark */}
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-7 h-7 rounded-site bg-site-surface border border-site-border flex items-center justify-center text-site-accent group-hover:border-site-accent transition-colors">
            <span className="font-mono font-bold text-sm">H</span>
          </div>
          <span className="font-serif font-bold text-lg text-site-text-primary tracking-tight">
            Helios Terminal
          </span>
        </Link>

        {/* Navigation & Action */}
        <div className="flex items-center gap-4 sm:gap-8">
          <nav className="hidden md:flex items-center gap-6">
            {navLinks.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `text-sm font-sans transition-colors duration-150 ${
                    isActive
                      ? 'text-site-text-primary font-semibold'
                      : 'text-site-text-secondary hover:text-site-text-primary'
                  }`
                }
              >
                {item.name}
              </NavLink>
            ))}
          </nav>

          <div className="flex items-center gap-3">
            <Button to="/dashboard" variant="primary" size="sm">
              <span className="hidden sm:inline">Enter Dashboard</span>
              <span className="sm:hidden">Dashboard</span>
            </Button>
            <button
              type="button"
              className="inline-flex h-9 w-9 items-center justify-center text-site-text-primary md:hidden"
              aria-label={mobileNavOpen ? 'Close site navigation' : 'Open site navigation'}
              aria-expanded={mobileNavOpen}
              aria-controls="site-mobile-navigation"
              onClick={() => setMobileNavOpen((open) => !open)}
            >
              {mobileNavOpen ? <X className="h-5 w-5" aria-hidden="true" /> : <Menu className="h-5 w-5" aria-hidden="true" />}
            </button>
          </div>
        </div>
      </div>
      <nav
        id="site-mobile-navigation"
        className={`${mobileNavOpen ? 'grid' : 'hidden'} border-t border-site-border bg-site-bg px-4 py-3 md:hidden`}
        aria-label="Mobile site navigation"
      >
        {navLinks.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            onClick={() => setMobileNavOpen(false)}
            className={({ isActive }) => `px-2 py-2 text-sm ${isActive ? 'font-semibold text-site-text-primary' : 'text-site-text-secondary'}`}
          >
            {item.name}
          </NavLink>
        ))}
      </nav>
    </header>
  );
};
