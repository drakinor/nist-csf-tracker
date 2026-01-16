import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Shield, ChevronRight, ChevronDown } from 'lucide-react';
import { controlApi, type Control } from '../services/api';

export default function Controls() {
  const [expandedFunctions, setExpandedFunctions] = useState<Set<string>>(new Set(['Govern', 'Identify', 'Protect', 'Detect', 'Respond', 'Recover']));

  const { data: controls, isLoading } = useQuery({
    queryKey: ['controls'],
    queryFn: () => controlApi.list({ limit: 200 }).then(res => res.data),
  });

  const functions = ['Govern', 'Identify', 'Protect', 'Detect', 'Respond', 'Recover'];

  // Group controls by function, then by category
  const groupedByFunction = controls?.reduce((acc, control) => {
    if (!acc[control.function]) {
      acc[control.function] = {};
    }
    if (!acc[control.function][control.category]) {
      acc[control.function][control.category] = [];
    }
    acc[control.function][control.category].push(control);
    return acc;
  }, {} as Record<string, Record<string, Control[]>>);

  const toggleFunction = (func: string) => {
    setExpandedFunctions((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(func)) {
        newSet.delete(func);
      } else {
        newSet.add(func);
      }
      return newSet;
    });
  };

  const getFunctionColor = (func: string) => {
    const colors: Record<string, string> = {
      'Govern': '#4F46E5',
      'Identify': '#0891B2',
      'Protect': '#059669',
      'Detect': '#DC2626',
      'Respond': '#EA580C',
      'Recover': '#7C3AED',
    };
    return colors[func] || '#6B7280';
  };

  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">NIST CSF Controls</h1>
        <p className="page-description">
          Browse and manage NIST Cybersecurity Framework 2.0 controls - {controls?.length || 0} total
        </p>
      </div>

      {/* Controls List by Function */}
      {isLoading ? (
        <div className="spinner" />
      ) : groupedByFunction ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {functions.map((func) => {
            const functionData = groupedByFunction[func];
            if (!functionData) return null;
            
            const isExpanded = expandedFunctions.has(func);
            const functionColor = getFunctionColor(func);
            const controlCount = Object.values(functionData).reduce((sum, controls) => sum + controls.length, 0);

            return (
              <div key={func} className="card">
                <button
                  onClick={() => toggleFunction(func)}
                  style={{
                    width: '100%',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '1rem',
                    background: 'transparent',
                    border: 'none',
                    cursor: 'pointer',
                    textAlign: 'left',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div
                      style={{
                        width: '4px',
                        height: '40px',
                        backgroundColor: functionColor,
                        borderRadius: '2px',
                      }}
                    />
                    <div>
                      <h2 style={{ margin: 0, fontSize: '1.5rem', color: functionColor }}>
                        {func}
                      </h2>
                      <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.875rem', color: '#666666' }}>
                        {controlCount} control{controlCount !== 1 ? 's' : ''} • {Object.keys(functionData).length} categor{Object.keys(functionData).length !== 1 ? 'ies' : 'y'}
                      </p>
                    </div>
                  </div>
                  <ChevronDown
                    size={24}
                    color="#666666"
                    style={{
                      transform: isExpanded ? 'rotate(0deg)' : 'rotate(-90deg)',
                      transition: 'transform 0.2s',
                    }}
                  />
                </button>

                {isExpanded && (
                  <div style={{ paddingTop: '1rem' }}>
                    {Object.entries(functionData).map(([category, categoryControls]) => (
                      <div key={category} style={{ marginBottom: '1.5rem' }}>
                        <h3 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '0.75rem', color: '#1a1a1a', paddingLeft: '1rem' }}>
                          {category}
                        </h3>
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
                                marginLeft: '1rem',
                                marginRight: '1rem',
                                background: '#f9fafb',
                                borderRadius: '6px',
                                textDecoration: 'none',
                                color: '#1a1a1a',
                                transition: 'all 0.2s',
                                borderLeft: `3px solid ${functionColor}`,
                              }}
                              onMouseEnter={(e) => {
                                e.currentTarget.style.background = '#f3f4f6';
                              }}
                              onMouseLeave={(e) => {
                                e.currentTarget.style.background = '#f9fafb';
                              }}
                            >
                              <div style={{ flex: 1 }}>
                                <div className="flex items-center gap-2 mb-1" style={{ color: '#1a1a1a' }}>
                                  <Shield size={16} color={functionColor} />
                                  <strong>{control.csf_id}</strong>
                                  <span style={{ color: '#666666' }}>•</span>
                                  <span>{control.name}</span>
                                </div>
                                <div className="text-sm" style={{ color: '#666666' }}>{control.text}</div>
                              </div>
                              <ChevronRight size={20} color="#999999" />
                            </Link>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
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
