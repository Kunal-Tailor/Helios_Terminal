import React from 'react';
import { Link, NavLink, useLocation } from 'react-router-dom';
import { Button } from './Button';
import { ArrowLeft, Terminal } from 'lucide-react';

export interface SiteHeaderProps {
  variant?: 'light' | 'dark-collapsed';
}

export const SiteHeader: React.FC<SiteHeaderProps> = ({ variant }) => {
  const location = useLocation();
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
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
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
        <div className="flex items-center gap-8">
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
              Enter Dashboard
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};