import { useState } from 'react';
import { Link, NavLink, useLocation } from 'react-router-dom';
import { Button } from './Button';
import { ArrowLeft, Menu, Terminal, X } from 'lucide-react';

export interface SiteHeaderProps {
  variant?: 'light' | 'dark-collapsed';
}

export const SiteHeader: React.FC<SiteHeaderProps> = ({ variant }) => {
  const location = useLocation();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const isDashboard = variant
    ? variant === 'dark-collapsed'
    : location.pathname.startsWith('/dashboard');

  /* ── Dark-collapsed header for Dashboard ── */
  if (isDashboard) {
    return (
      <header className="sticky top-0 z-50 w-full border-b border-[#23272F] bg-[#0E1013] text-[#E6EDF3] transition-colors duration-200">
        <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-6">
          <Link to="/dashboard" className="group flex items-center gap-2.5">
            <div className="flex h-7 w-7 items-center justify-center rounded bg-[#1A1E24] border border-[#2D333B] text-site-accent">
              <Terminal className="h-4 w-4" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="font-mono text-sm font-bold tracking-wider text-[#F0F6FC]">
                HELIOS_TERMINAL
              </span>
              <span className="hidden text-[10px] font-mono uppercase tracking-widest text-[#7D8590] sm:inline">
                [SOVEREIGN_CORE]
              </span>
            </div>
          </Link>

          <Link
            to="/"
            className="flex items-center gap-1.5 rounded px-2 py-1 font-mono text-xs text-site-accent transition-colors hover:bg-[#161B22] hover:text-[#56D4DD]"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            <span>Overview</span>
          </Link>
        </div>
      </header>
    );
  }

  /* ── Light header for marketing site ── */
  const navLinks = [
    { name: 'Home', path: '/' },
    { name: 'Architecture', path: '/architecture' },
    { name: 'About', path: '/about' },
    { name: 'Team', path: '/team' },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-site-border bg-site-bg/95 backdrop-blur-sm transition-colors duration-200">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
        {/* Logo and Wordmark */}
        <Link to="/" className="group flex items-center gap-2.5">
          <div className="flex h-7 w-7 items-center justify-center rounded-site border border-site-border bg-site-surface text-site-accent transition-colors group-hover:border-site-accent">
            <span className="font-mono text-sm font-bold">H</span>
          </div>
          <span className="font-serif text-lg font-bold tracking-tight text-site-text-primary">
            Helios Terminal
          </span>
        </Link>

        {/* Navigation & Action */}
        <div className="flex items-center gap-4 sm:gap-8">
          <nav className="hidden items-center gap-6 md:flex">
            {navLinks.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
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
              aria-label={mobileNavOpen ? 'Close navigation' : 'Open navigation'}
              aria-expanded={mobileNavOpen}
              aria-controls="site-mobile-nav"
              onClick={() => setMobileNavOpen((o) => !o)}
            >
              {mobileNavOpen ? (
                <X className="h-5 w-5" aria-hidden="true" />
              ) : (
                <Menu className="h-5 w-5" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile nav drawer */}
      <nav
        id="site-mobile-nav"
        className={`${
          mobileNavOpen ? 'grid' : 'hidden'
        } border-t border-site-border bg-site-bg px-4 py-3 md:hidden`}
        aria-label="Mobile site navigation"
      >
        {navLinks.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            onClick={() => setMobileNavOpen(false)}
            className={({ isActive }) =>
              `px-2 py-2 text-sm ${
                isActive
                  ? 'font-semibold text-site-text-primary'
                  : 'text-site-text-secondary'
              }`
            }
          >
            {item.name}
          </NavLink>
        ))}
      </nav>
    </header>
  );
};
