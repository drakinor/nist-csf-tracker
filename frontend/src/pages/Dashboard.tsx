import { useQuery } from '@tanstack/react-query';
import { Activity, FileText, CheckCircle, AlertCircle } from 'lucide-react';
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

      {/* Function Summary */}
      <div className="card">
        <h2 className="section-title">Compliance by Function</h2>
        {functionSummaries.length > 0 ? (
          <table>
            <thead>
              <tr>
                <th>Function</th>
                <th>Score</th>
                <th>Controls</th>
                <th>Progress</th>
              </tr>
            </thead>
            <tbody>
              {functionSummaries.map((func: any) => (
                <tr key={func.function}>
                  <td>
                    <strong>{func.function}</strong>
                  </td>
                  <td>
                    <span className={`badge badge-${func.percentage >= 80 ? 'full' : func.percentage >= 50 ? 'mostly' : func.percentage > 0 ? 'partial' : 'none'}`}>
                      {func.percentage}%
                    </span>
                  </td>
                  <td className="text-muted">
                    {func.scored_controls} / {func.total_controls}
                  </td>
                  <td>
                    <div style={{ 
                      background: '#e5e7eb', 
                      height: '8px', 
                      borderRadius: '4px',
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        background: func.percentage >= 80 ? '#059669' : func.percentage >= 50 ? '#2563eb' : '#f59e0b',
                        width: `${func.percentage}%`,
                        height: '100%',
                        transition: 'width 0.3s'
                      }} />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="empty-state">
            <p>No scores calculated yet. Start by ingesting artifacts and validating evidence.</p>
          </div>
        )}
      </div>
    </div>
  );
}
