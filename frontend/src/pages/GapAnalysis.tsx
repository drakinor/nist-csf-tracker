import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { AlertTriangle, CheckCircle, XCircle, TrendingDown, Filter } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import axios from 'axios';

export default function GapAnalysis() {
  const queryClient = useQueryClient();
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('open');
  const [gapTypeFilter, setGapTypeFilter] = useState<string>('');

  const { data: gaps, isLoading } = useQuery({
    queryKey: ['gaps', severityFilter, statusFilter, gapTypeFilter],
    queryFn: () => axios.get('http://localhost:8000/api/gaps/', {
      params: {
        severity: severityFilter || undefined,
        status: statusFilter || undefined,
        gap_type: gapTypeFilter || undefined
      }
    }).then(res => res.data),
  });

  const { data: controls } = useQuery({
    queryKey: ['controls'],
    queryFn: () => axios.get('http://localhost:8000/api/controls/').then(res => res.data),
  });

  const resolveGapMutation = useMutation({
    mutationFn: (gapId: number) => 
      axios.patch(`http://localhost:8000/api/gaps/${gapId}/resolve`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['gaps'] });
    },
  });

  const getControlInfo = (controlId: number) => {
    return controls?.find((c: any) => c.id === controlId);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#dc2626';
      case 'high': return '#f59e0b';
      case 'medium': return '#3b82f6';
      case 'low': return '#10b981';
      default: return '#6b7280';
    }
  };

  const getGapTypeLabel = (gapType: string) => {
    const labels: Record<string, string> = {
      'missing_control': 'Missing Control',
      'missing_policy': 'Missing Policy',
      'missing_procedure': 'Missing Procedure',
      'missing_technical_enforcement': 'Missing Technical Enforcement',
      'missing_operational_evidence': 'Missing Operational Evidence',
      'incomplete_implementation': 'Incomplete Implementation'
    };
    return labels[gapType] || gapType;
  };

  const groupedGaps = gaps?.reduce((acc: any, gap: any) => {
    if (!acc[gap.severity]) {
      acc[gap.severity] = [];
    }
    acc[gap.severity].push(gap);
    return acc;
  }, {}) || {};

  const severityOrder = ['critical', 'high', 'medium', 'low'];

  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">Gap Analysis</h1>
        <p className="page-description">
          Identified gaps in control implementation based on evidence validation
        </p>
      </div>

      {/* Summary Stats */}
      <div className="stats-grid" style={{ marginBottom: '2rem' }}>
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Total Gaps</span>
            <AlertTriangle className="stat-icon" size={24} />
          </div>
          <div className="stat-value">{gaps?.length || 0}</div>
          <div className="stat-change">Across all controls</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Critical</span>
            <TrendingDown className="stat-icon" size={24} style={{ color: '#dc2626' }} />
          </div>
          <div className="stat-value" style={{ color: '#dc2626' }}>
            {gaps?.filter((g: any) => g.severity === 'critical').length || 0}
          </div>
          <div className="stat-change">Require immediate attention</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">High Priority</span>
            <AlertTriangle className="stat-icon" size={24} style={{ color: '#f59e0b' }} />
          </div>
          <div className="stat-value" style={{ color: '#f59e0b' }}>
            {gaps?.filter((g: any) => g.severity === 'high').length || 0}
          </div>
          <div className="stat-change">Important to address</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Open Gaps</span>
            <XCircle className="stat-icon" size={24} />
          </div>
          <div className="stat-value">
            {gaps?.filter((g: any) => g.status === 'open').length || 0}
          </div>
          <div className="stat-change">Not yet addressed</div>
        </div>
      </div>

      {/* Filters */}
      <div className="card" style={{ marginBottom: '1rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500' }}>
              Status
            </label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="form-control"
            >
              <option value="">All</option>
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="accepted">Accepted</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500' }}>
              Severity
            </label>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="form-control"
            >
              <option value="">All</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500' }}>
              Gap Type
            </label>
            <select
              value={gapTypeFilter}
              onChange={(e) => setGapTypeFilter(e.target.value)}
              className="form-control"
            >
              <option value="">All Types</option>
              <option value="missing_control">Missing Control</option>
              <option value="missing_policy">Missing Policy</option>
              <option value="missing_procedure">Missing Procedure</option>
              <option value="missing_technical_enforcement">Missing Technical</option>
              <option value="missing_operational_evidence">Missing Operational</option>
              <option value="incomplete_implementation">Incomplete</option>
            </select>
          </div>
        </div>
      </div>

      {/* Gap List by Severity */}
      {isLoading ? (
        <div className="card">
          <div className="spinner" />
        </div>
      ) : gaps && gaps.length > 0 ? (
        severityOrder.map((severity) => {
          const severityGaps = groupedGaps[severity] || [];
          if (severityGaps.length === 0) return null;

          return (
            <div key={severity} className="card" style={{ marginBottom: '1.5rem' }}>
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '0.75rem',
                marginBottom: '1.5rem',
                paddingBottom: '1rem',
                borderBottom: '2px solid var(--border-color)'
              }}>
                <div style={{
                  width: '8px',
                  height: '40px',
                  backgroundColor: getSeverityColor(severity),
                  borderRadius: '4px'
                }} />
                <div>
                  <h2 style={{ margin: 0, fontSize: '1.5rem', fontWeight: '600', textTransform: 'capitalize' }}>
                    {severity} Priority
                  </h2>
                  <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                    {severityGaps.length} {severityGaps.length === 1 ? 'gap' : 'gaps'}
                  </p>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {severityGaps.map((gap: any) => {
                  const control = getControlInfo(gap.control_id);
                  return (
                    <div
                      key={gap.id}
                      style={{
                        padding: '1.5rem',
                        backgroundColor: 'var(--bg-secondary)',
                        borderRadius: '8px',
                        border: '1px solid var(--border-color)',
                        borderLeftWidth: '4px',
                        borderLeftColor: getSeverityColor(gap.severity)
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                        <div style={{ flex: 1 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                            <span style={{
                              padding: '0.25rem 0.75rem',
                              backgroundColor: getSeverityColor(gap.severity),
                              color: 'white',
                              borderRadius: '12px',
                              fontSize: '0.75rem',
                              fontWeight: '600',
                              textTransform: 'uppercase'
                            }}>
                              {gap.severity}
                            </span>
                            <span className="badge badge-none">
                              {getGapTypeLabel(gap.gap_type)}
                            </span>
                          </div>
                          
                          <Link
                            to={`/controls/${gap.control_id}`}
                            style={{ textDecoration: 'none' }}
                          >
                            <h3 style={{ 
                              margin: '0.5rem 0', 
                              fontSize: '1.125rem', 
                              fontWeight: '600',
                              color: '#2563eb'
                            }}>
                              {control?.csf_id} - {control?.name}
                            </h3>
                          </Link>
                          
                          <p style={{ 
                            margin: '0.5rem 0 0 0', 
                            fontSize: '0.875rem', 
                            color: 'var(--text-primary)' 
                          }}>
                            {gap.description}
                          </p>
                        </div>

                        {gap.status === 'open' && (
                          <button
                            className="btn btn-success"
                            onClick={() => resolveGapMutation.mutate(gap.id)}
                            disabled={resolveGapMutation.isPending}
                            style={{ marginLeft: '1rem' }}
                          >
                            <CheckCircle size={16} />
                            Mark Resolved
                          </button>
                        )}
                      </div>

                      <div style={{ 
                        fontSize: '0.75rem', 
                        color: 'var(--text-muted)',
                        display: 'flex',
                        gap: '1rem'
                      }}>
                        <span>Function: {control?.function}</span>
                        <span>Category: {control?.category}</span>
                        <span>Status: {gap.status}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })
      ) : (
        <div className="card">
          <div className="empty-state">
            <CheckCircle className="empty-state-icon" size={48} style={{ color: '#10b981' }} />
            <h3 className="empty-state-title">No Gaps Found</h3>
            <p className="empty-state-description">
              {statusFilter === 'open' 
                ? 'All controls are fully implemented! Great work!'
                : 'Try adjusting your filters to see more results.'}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}