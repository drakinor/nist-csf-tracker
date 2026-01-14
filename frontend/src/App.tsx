import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Moon, Sun } from 'lucide-react';
import { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './pages/Dashboard';
import Artifacts from './pages/Artifacts';
import Controls from './pages/Controls';
import ControlDetail from './pages/ControlDetail';
import ValidationQueue from './pages/ValidationQueue';
import GapAnalysis from './pages/GapAnalysis';

function App() {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : true;
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
  }, [darkMode]);

  return (
    <Router>
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <header style={{
          background: '#2c3e50',
          color: 'white',
          padding: '1rem 2rem',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', maxWidth: '1200px', margin: '0 auto' }}>
            <h1 style={{ margin: 0, fontSize: '1.5rem' }}>NIST CSF Tracker</h1>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <button
                onClick={() => setDarkMode(!darkMode)}
                style={{
                  background: 'rgba(255,255,255,0.1)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  cursor: 'pointer',
                  padding: '0.5rem',
                  display: 'flex',
                  alignItems: 'center',
                  color: 'white',
                  borderRadius: '4px'
                }}
                title={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                {darkMode ? <Sun size={20} /> : <Moon size={20} />}
              </button>
              <nav style={{ display: 'flex', gap: '2rem' }}>
                <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>Dashboard</Link>
                <Link to="/artifacts" style={{ color: 'white', textDecoration: 'none' }}>Artifacts</Link>
                <Link to="/controls" style={{ color: 'white', textDecoration: 'none' }}>Controls</Link>
                <Link to="/validation" style={{ color: 'white', textDecoration: 'none' }}>Validation Queue</Link>
                <Link to="/gaps" style={{ color: 'white', textDecoration: 'none' }}>Gap Analysis</Link>
              </nav>
            </div>
          </div>
        </header>

        <main style={{ flex: 1, padding: '2rem', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/artifacts" element={<Artifacts />} />
            <Route path="/controls" element={<Controls />} />
            <Route path="/controls/:id" element={<ControlDetail />} />
            <Route path="/validation" element={<ValidationQueue />} />
            <Route path="/gaps" element={<GapAnalysis />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;