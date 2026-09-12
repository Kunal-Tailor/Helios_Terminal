import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Home } from './site/pages/Home';
import { Architecture } from './site/pages/Architecture';
import { About } from './site/pages/About';
import { Team } from './site/pages/Team';
import { DashboardPlaceholder } from './dashboard/pages/DashboardPlaceholder';

function SiteMotion() {
  const { pathname } = useLocation();

  useEffect(() => {
    const sections = Array.from(document.querySelectorAll<HTMLElement>('.theme-site main > section'));
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    sections.forEach((section) => section.classList.add('site-reveal'));
    if (reduceMotion || !('IntersectionObserver' in window)) {
      sections.forEach((section) => section.classList.add('is-revealed'));
      return undefined;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-revealed');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.08 },
    );

    sections.forEach((section) => observer.observe(section));
    return () => observer.disconnect();
  }, [pathname]);

  return null;
}

export default function App() {
  return (
    <BrowserRouter>
      <SiteMotion />
      <Routes>
        {/* Marketing Site Family (Light Theme) */}
        <Route path="/" element={<Home />} />
        <Route path="/architecture" element={<Architecture />} />
        <Route path="/about" element={<About />} />
        <Route path="/team" element={<Team />} />

        {/* Dashboard Family (Dark Theme) */}
        <Route path="/dashboard" element={<DashboardPlaceholder />} />

        {/* Catch-all route returns to Home */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
