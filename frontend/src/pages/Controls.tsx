import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Shield, ChevronRight } from 'lucide-react';
import { controlApi, type Control } from '../services/api';

export default function Controls() {
  const [selectedFunction, setSelectedFunction] = useState<string>('');

  const { data: controls, isLoading } = useQuery({
    queryKey: ['controls', selectedFunction],
    queryFn: () =>
      controlApi.list(selectedFunction ? { function: selectedFunction } : undefined)
        .then(res => res.data),
  });

  const functions = ['Identify', 'Protect', 'Detect', 'Respond', 'Recover'];

  // Group controls by category
  const groupedControls = controls?.reduce((acc, control) => {
    if (!acc[control.category]) {
      acc[control.category] = [];
    }
    acc[control.category].push(control);
    return acc;
  }, {} as Record<string, Control[]>);

  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">NIST CSF Controls</h1>
        <p className="page-description">
          Browse and manage NIST Cybersecurity Framework controls
        </p>
      </div>

      {/* Function Filter */}
      <div className="card mb-3">
        <div className="flex gap-2">
          <button
            className={`btn ${selectedFunction === '' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setSelectedFunction('')}
          >
            All
          </button>
          {functions.map((func) => (
            <button
              key={func}
              className={`btn ${selectedFunction === func ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setSelectedFunction(func)}
            >
              {func}
            </button>
          ))}
        </div>
      </div>

      {/* Controls List */}
      {isLoading ? (
        <div className="spinner" />
      ) : groupedControls ? (
        Object.entries(groupedControls).map(([category, categoryControls]) => (
          <div key={category} className="card mb-3">
            <h3 className="mb-2">{category}</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {categoryControls.map((control) => (
                <Link
                  key={control.id}
                  to={`/controls/${control.id}`}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '1rem',
                    background: '#f9fafb',
                    borderRadius: '6px',
                    textDecoration: 'none',
                    color: 'inherit',
                    transition: 'all 0.2s',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = '#f3f4f6';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = '#f9fafb';
                  }}
                >
                  <div style={{ flex: 1 }}>
                    <div className="flex items-center gap-2 mb-1">
                      <Shield size={16} />
                      <strong>{control.csf_id}</strong>
                      <span className="text-muted">•</span>
                      <span>{control.name}</span>
                    </div>
                    <div className="text-sm text-muted">{control.text}</div>
                  </div>
                  <ChevronRight size={20} className="text-muted" />
                </Link>
              ))}
            </div>
          </div>
        ))
      ) : (
        <div className="card">
          <div className="empty-state">
            <Shield className="empty-state-icon" size={48} />
            <h3 className="empty-state-title">No controls found</h3>
          </div>
        </div>
      )}
    </div>
  );
}
