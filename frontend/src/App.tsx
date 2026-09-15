import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ScrollToTop } from './shared/ScrollToTop';
import { Home } from './site/pages/Home';
import { Architecture } from './site/pages/Architecture';
import { About } from './site/pages/About';
import { Team } from './site/pages/Team';
import { DashboardPlaceholder } from './dashboard/pages/DashboardPlaceholder';

export default function App() {
  return (
    <BrowserRouter>
      <ScrollToTop />
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
