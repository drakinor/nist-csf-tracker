import { useQuery } from '@tanstack/react-query';
import { Activity, FileText, CheckCircle, AlertCircle, TrendingUp, BarChart3 } from 'lucide-react';
import { scoreApi, artifactApi, controlApi, evidenceApi } from '../services/api';

export default function Dashboard() {
  const { data: dashboardData } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => scoreApi.getDashboard().then(res => res.data),
  });

  const { data: artifacts } = useQuery({
    queryKey: ['artifacts'],
    queryFn: () => artifactApi.list().then(res => res.data),
  });

  const { data: controls } = useQuery({
    queryKey: ['controls'],
    queryFn: () => controlApi.list().then(res => res.data),
  });

  const { data: pendingEvidence } = useQuery({
    queryKey: ['evidence', 'pending'],
    queryFn: () => evidenceApi.list({ status: 'pending' }).then(res => res.data),
  });

  const overallScore = dashboardData?.overall?.percentage || 0;
  const functionSummaries = dashboardData?.by_function || [];
  const categorySummaries = dashboardData?.by_category || [];
  const scoreDistribution = dashboardData?.score_distribution || {};

  // Calculate score color
  const getScoreColor = (percentage: number) => {
    if (percentage >= 80) return '#059669'; // green
    if (percentage >= 60) return '#2563eb'; // blue
    if (percentage >= 40) return '#f59e0b'; // orange
    return '#ef4444'; // red
  };

  // Calculate badge class
  const getBadgeClass = (percentage: number) => {
    if (percentage >= 80) return 'badge-full';
    if (percentage >= 50) return 'badge-mostly';
    if (percentage > 0) return 'badge-partial';
    return 'badge-none';
  };

  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-description">
          Overview of your NIST CSF compliance posture
        </p>
      </div>

      {/* Overall Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Overall Compliance</span>
            <Activity className="stat-icon" size={24} />
          </div>
          <div className="stat-value">{overallScore}%</div>
          <div className="stat-change">
            {dashboardData?.overall?.scored_controls || 0} of {dashboardData?.overall?.total_controls || 0} controls scored
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Artifacts Ingested</span>
            <FileText className="stat-icon" size={24} />
          </div>
          <div className="stat-value">{artifacts?.length || 0}</div>
          <div className="stat-change">Documents, URLs, and files</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Total Controls</span>
            <CheckCircle className="stat-icon" size={24} />
          </div>
          <div className="stat-value">{controls?.length || 0}</div>
          <div className="stat-change">NIST CSF controls loaded</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Pending Validation</span>
            <AlertCircle className="stat-icon" size={24} />
          </div>
          <div className="stat-value">{pendingEvidence?.length || 0}</div>
          <div className="stat-change">Evidence items to review</div>
        </div>
      </div>

      {/* Score Distribution */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
          <BarChart3 size={24} />
          <h2 className="section-title" style={{ margin: 0 }}>Score Distribution</h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem' }}>
          <div style={{ textAlign: 'center', padding: '1rem', backgroundColor: 'var(--bg-secondary)', borderRadius: '8px' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#059669' }}>
              {scoreDistribution.full || 0}
            </div>
            <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              Full Implementation
            </div>
          </div>
          <div style={{ textAlign: 'center', padding: '1rem', backgroundColor: 'var(--bg-secondary)', borderRadius: '8px' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2563eb' }}>
              {scoreDistribution.mostly || 0}
            </div>
            <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              Mostly Implemented
            </div>
          </div>
          <div style={{ textAlign: 'center', padding: '1rem', backgroundColor: 'var(--bg-secondary)', borderRadius: '8px' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#f59e0b' }}>
              {scoreDistribution.partial || 0}
            </div>
            <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              Partial Implementation
            </div>
          </div>
          <div style={{ textAlign: 'center', padding: '1rem', backgroundColor: 'var(--bg-secondary)', borderRadius: '8px' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#ef4444' }}>
              {scoreDistribution.none || 0}
            </div>
            <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              Not Implemented
            </div>
          </div>
        </div>
      </div>

      {/* Function Summary with Enhanced Visuals */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
          <TrendingUp size={24} />
          <h2 className="section-title" style={{ margin: 0 }}>Compliance by Function</h2>
        </div>
        {functionSummaries.length > 0 ? (
          <div style={{ display: 'grid', gap: '1.5rem' }}>
            {functionSummaries.map((func: any) => (
              <div key={func.function} style={{ 
                padding: '1.5rem', 
                backgroundColor: 'var(--bg-secondary)', 
                borderRadius: '8px',
                border: '1px solid var(--border-color)'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '1.25rem', fontWeight: '600' }}>{func.function}</h3>
                    <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                      {func.scored_controls} of {func.total_controls} controls scored
                    </p>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: getScoreColor(func.percentage) }}>
                      {func.percentage}%
                    </div>
                    <span className={`badge ${getBadgeClass(func.percentage)}`} style={{ marginTop: '0.5rem' }}>
                      {func.percentage >= 80 ? 'Excellent' : func.percentage >= 50 ? 'Good' : func.percentage > 0 ? 'Needs Work' : 'Not Started'}
                    </span>
                  </div>
                </div>
                {/* Progress bar */}
                <div style={{ 
                  background: 'var(--bg-primary)', 
                  height: '12px', 
                  borderRadius: '6px',
                  overflow: 'hidden',
                  border: '1px solid var(--border-color)'
                }}>
                  <div style={{
                    background: `linear-gradient(90deg, ${getScoreColor(func.percentage)}, ${getScoreColor(func.percentage)}dd)`,
                    width: `${func.percentage}%`,
                    height: '100%',
                    transition: 'width 0.5s ease',
                    borderRadius: '6px'
                  }} />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <p>No scores calculated yet. Start by ingesting artifacts and validating evidence.</p>
          </div>
        )}
      </div>

      {/* Category Breakdown */}
      <div className="card">
        <h2 className="section-title">Compliance by Category</h2>
        {categorySummaries.length > 0 ? (
          <table>
            <thead>
              <tr>
                <th>Category</th>
                <th>Score</th>
                <th>Controls</th>
                <th style={{ width: '40%' }}>Progress</th>
              </tr>
            </thead>
            <tbody>
              {categorySummaries.map((cat: any) => (
                <tr key={cat.category}>
                  <td>
                    <strong>{cat.category}</strong>
                  </td>
                  <td>
                    <span className={`badge ${getBadgeClass(cat.percentage)}`}>
                      {cat.percentage}%
                    </span>
                  </td>
                  <td className="text-muted">
                    {cat.scored_controls} / {cat.total_controls}
                  </td>
                  <td>
                    <div style={{ 
                      background: 'var(--bg-secondary)', 
                      height: '10px', 
                      borderRadius: '5px',
                      overflow: 'hidden',
                      border: '1px solid var(--border-color)'
                    }}>
                      <div style={{
                        background: getScoreColor(cat.percentage),
                        width: `${cat.percentage}%`,
                        height: '100%',
                        transition: 'width 0.3s ease'
                      }} />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="empty-state">
            <p>No category data available yet.</p>
          </div>
        )}
      </div>
    </div>
  );
}