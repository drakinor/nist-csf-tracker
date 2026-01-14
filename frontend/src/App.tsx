import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { FileText, Shield, CheckCircle, AlertTriangle, Home } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Artifacts from './pages/Artifacts';
import Controls from './pages/Controls';
import ControlDetail from './pages/ControlDetail';
import ValidationQueue from './pages/ValidationQueue';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="container">
            <div className="nav-brand">
              <Shield size={28} />
              <span>NIST CSF Tracker</span>
            </div>
            <div className="nav-links">
              <Link to="/" className="nav-link">
                <Home size={18} />
                Dashboard
              </Link>
              <Link to="/artifacts" className="nav-link">
                <FileText size={18} />
                Artifacts
              </Link>
              <Link to="/controls" className="nav-link">
                <CheckCircle size={18} />
                Controls
              </Link>
              <Link to="/validation" className="nav-link">
                <AlertTriangle size={18} />
                Validation Queue
              </Link>
            </div>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/artifacts" element={<Artifacts />} />
            <Route path="/controls" element={<Controls />} />
            <Route path="/controls/:id" element={<ControlDetail />} />
            <Route path="/validation" element={<ValidationQueue />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
