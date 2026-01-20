import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Calendar, User, CheckCircle, Clock, Ban, Target, Trash2, Edit } from 'lucide-react';
import { actionApi, gapApi, type Action } from '../services/api';

export default function Actions() {
  const queryClient = useQueryClient();
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingAction, setEditingAction] = useState<Action | null>(null);
  const [viewMode, setViewMode] = useState<'kanban' | 'list'>('kanban');

  const { data: kanbanData } = useQuery({
    queryKey: ['actions', 'kanban'],
    queryFn: () => actionApi.getKanban().then(res => res.data),
  });

  const { data: summary } = useQuery({
    queryKey: ['actions', 'summary'],
    queryFn: () => actionApi.getSummary().then(res => res.data),
  });

  const { data: gaps } = useQuery({
    queryKey: ['gaps'],
    queryFn: () => gapApi.list({ status: 'open' }).then(res => res.data),
  });

  const updateActionMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => 
      actionApi.update(id, data).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['actions'] });
    },
  });

  const deleteActionMutation = useMutation({
    mutationFn: (id: number) => actionApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['actions'] });
    },
  });

  const moveAction = (action: Action, newStatus: string) => {
    updateActionMutation.mutate({
      id: action.id!,
      data: { status: newStatus },
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'open': return <Target size={16} />;
      case 'in_progress': return <Clock size={16} />;
      case 'blocked': return <Ban size={16} />;
      case 'complete': return <CheckCircle size={16} />;
      default: return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return '#3b82f6';
      case 'in_progress': return '#f59e0b';
      case 'blocked': return '#ef4444';
      case 'complete': return '#10b981';
      default: return '#6b7280';
    }
  };

  const isOverdue = (action: Action) => {
    if (!action.due_date || action.status === 'complete') return false;
    return new Date(action.due_date) < new Date();
  };

  return (
    <div className="container">
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <div>
            <h1 className="page-title">Action Items</h1>
            <p className="page-description">Track remediation tasks and improvement initiatives</p>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              className={`btn ${viewMode === 'kanban' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setViewMode('kanban')}
            >
              Kanban
            </button>
            <button
              className={`btn ${viewMode === 'list' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setViewMode('list')}
            >
              List
            </button>
            <button
              className="btn btn-success"
              onClick={() => setShowCreateForm(true)}
            >
              <Plus size={18} />
              New Action
            </button>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="stats-grid" style={{ marginBottom: '2rem' }}>
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Total Actions</span>
            <Target className="stat-icon" size={24} />
          </div>
          <div className="stat-value">{summary?.total_actions || 0}</div>
          <div className="stat-change">Across all controls</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">In Progress</span>
            <Clock className="stat-icon" size={24} style={{ color: '#f59e0b' }} />
          </div>
          <div className="stat-value" style={{ color: '#f59e0b' }}>
            {summary?.by_status?.in_progress || 0}
          </div>
          <div className="stat-change">Currently being worked</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Overdue</span>
            <Calendar className="stat-icon" size={24} style={{ color: '#ef4444' }} />
          </div>
          <div className="stat-value" style={{ color: '#ef4444' }}>
            {summary?.overdue_count || 0}
          </div>
          <div className="stat-change">Past due date</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Completion Rate</span>
            <CheckCircle className="stat-icon" size={24} style={{ color: '#10b981' }} />
          </div>
          <div className="stat-value" style={{ color: '#10b981' }}>
            {summary?.completion_rate || 0}%
          </div>
          <div className="stat-change">Actions completed</div>
        </div>
      </div>

      {/* Kanban Board View */}
      {viewMode === 'kanban' && kanbanData && (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(4, 1fr)', 
          gap: '1rem',
          marginBottom: '2rem'
        }}>
          {Object.entries(kanbanData).map(([status, actions]: [string, any]) => (
            <div key={status} className="card" style={{ 
              background: 'var(--bg-secondary)',
              minHeight: '400px'
            }}>
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '0.5rem',
                marginBottom: '1rem',
                paddingBottom: '0.75rem',
                borderBottom: '2px solid var(--border-color)'
              }}>
                {getStatusIcon(status)}
                <h3 style={{ 
                  margin: 0, 
                  fontSize: '1rem',
                  fontWeight: '600',
                  textTransform: 'capitalize',
                  color: getStatusColor(status)
                }}>
                  {status.replace('_', ' ')}
                </h3>
                <span className="badge" style={{ 
                  background: getStatusColor(status),
                  color: 'white',
                  marginLeft: 'auto'
                }}>
                  {actions.length}
                </span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {actions.map((action: Action) => (
                  <div
                    key={action.id}
                    className="card"
                    style={{
                      padding: '0.75rem',
                      cursor: 'pointer',
                      borderLeft: `4px solid ${getStatusColor(status)}`,
                      background: 'var(--bg-primary)',
                      transition: 'all 0.2s',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-2px)';
                      e.currentTarget.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                  >
                    <div style={{ marginBottom: '0.5rem' }}>
                      <strong style={{ fontSize: '0.875rem' }}>{action.title}</strong>
                      {isOverdue(action) && (
                        <span 
                          className="badge" 
                          style={{ 
                            background: '#fee2e2',
                            color: '#991b1b',
                            fontSize: '0.75rem',
                            marginLeft: '0.5rem'
                          }}
                        >
                          OVERDUE
                        </span>
                      )}
                    </div>

                    {action.description && (
                      <p style={{ 
                        fontSize: '0.75rem',
                        color: 'var(--text-muted)',
                        marginBottom: '0.5rem',
                        lineHeight: '1.4'
                      }}>
                        {action.description.substring(0, 80)}
                        {action.description.length > 80 && '...'}
                      </p>
                    )}

                    <div style={{ 
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '0.25rem',
                      fontSize: '0.75rem',
                      color: 'var(--text-muted)',
                      marginBottom: '0.5rem'
                    }}>
                      {action.owner && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                          <User size={12} />
                          <span>{action.owner}</span>
                        </div>
                      )}
                      {action.due_date && (
                        <div style={{ 
                          display: 'flex', 
                          alignItems: 'center', 
                          gap: '0.25rem',
                          color: isOverdue(action) ? '#ef4444' : 'var(--text-muted)'
                        }}>
                          <Calendar size={12} />
                          <span>{new Date(action.due_date).toLocaleDateString()}</span>
                        </div>
                      )}
                    </div>

                    {/* Quick Actions */}
                    <div style={{ 
                      display: 'flex', 
                      gap: '0.25rem',
                      paddingTop: '0.5rem',
                      borderTop: '1px solid var(--border-color)'
                    }}>
                      {status !== 'open' && (
                        <button
                          className="btn btn-secondary"
                          style={{ 
                            fontSize: '0.75rem', 
                            padding: '0.25rem 0.5rem',
                            flex: 1
                          }}
                          onClick={(e) => {
                            e.stopPropagation();
                            moveAction(action, 'open');
                          }}
                        >
                          ← Open
                        </button>
                      )}
                      {status === 'open' && (
                        <button
                          className="btn btn-primary"
                          style={{ 
                            fontSize: '0.75rem', 
                            padding: '0.25rem 0.5rem',
                            flex: 1
                          }}
                          onClick={(e) => {
                            e.stopPropagation();
                            moveAction(action, 'in_progress');
                          }}
                        >
                          Start →
                        </button>
                      )}
                      {status === 'in_progress' && (
                        <>
                          <button
                            className="btn btn-success"
                            style={{ 
                              fontSize: '0.75rem', 
                              padding: '0.25rem 0.5rem',
                              flex: 1
                            }}
                            onClick={(e) => {
                              e.stopPropagation();
                              moveAction(action, 'complete');
                            }}
                          >
                            ✓ Done
                          </button>
                          <button
                            className="btn btn-danger"
                            style={{ 
                              fontSize: '0.75rem', 
                              padding: '0.25rem 0.5rem',
                              flex: 1
                            }}
                            onClick={(e) => {
                              e.stopPropagation();
                              moveAction(action, 'blocked');
                            }}
                          >
                            ✕ Block
                          </button>
                        </>
                      )}
                      {status === 'blocked' && (
                        <button
                          className="btn btn-primary"
                          style={{ 
                            fontSize: '0.75rem', 
                            padding: '0.25rem 0.5rem',
                            flex: 1
                          }}
                          onClick={(e) => {
                            e.stopPropagation();
                            moveAction(action, 'in_progress');
                          }}
                        >
                          Resume
                        </button>
                      )}
                      {status === 'complete' && (
                        <span style={{ 
                          fontSize: '0.75rem',
                          color: '#10b981',
                          fontWeight: '500',
                          flex: 1,
                          textAlign: 'center'
                        }}>
                          ✓ Completed
                        </span>
                      )}
                    </div>
                  </div>
                ))}

                {actions.length === 0 && (
                  <div style={{ 
                    textAlign: 'center', 
                    padding: '2rem 1rem',
                    color: 'var(--text-muted)',
                    fontSize: '0.875rem'
                  }}>
                    No actions in this status
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Action Form Modal */}
      {showCreateForm && (
        <ActionFormModal
          onClose={() => setShowCreateForm(false)}
          gaps={gaps || []}
        />
      )}
    </div>
  );
}

function ActionFormModal({ onClose, gaps }: { onClose: () => void; gaps: any[] }) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    gap_id: '',
    owner: '',
    due_date: '',
    acceptance_criteria: '',
  });

  const createActionMutation = useMutation({
    mutationFn: (data: any) => actionApi.create(data).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['actions'] });
      onClose();
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const submitData: any = {
      title: formData.title,
      description: formData.description || undefined,
      owner: formData.owner || undefined,
      due_date: formData.due_date || undefined,
      acceptance_criteria: formData.acceptance_criteria || undefined,
    };

    if (formData.gap_id) {
      submitData.gap_id = parseInt(formData.gap_id);
    }

    createActionMutation.mutate(submitData);
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: '2rem',
      }}
      onClick={onClose}
    >
      <div
        className="card"
        style={{ maxWidth: '600px', width: '100%', maxHeight: '90vh', overflow: 'auto' }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 style={{ marginBottom: '1.5rem' }}>Create Action Item</h2>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1rem' }}>
            <label className="form-label">Title *</label>
            <input
              type="text"
              className="form-control"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              required
              placeholder="e.g., Implement MFA for all users"
            />
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label className="form-label">Description</label>
            <textarea
              className="form-control"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={3}
              placeholder="Detailed description of the action..."
            />
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label className="form-label">Linked Gap (optional)</label>
            <select
              className="form-control"
              value={formData.gap_id}
              onChange={(e) => setFormData({ ...formData, gap_id: e.target.value })}
            >
              <option value="">No linked gap</option>
              {gaps.map((gap) => (
                <option key={gap.id} value={gap.id}>
                  {gap.description.substring(0, 80)}
                </option>
              ))}
            </select>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
            <div>
              <label className="form-label">Owner</label>
              <input
                type="text"
                className="form-control"
                value={formData.owner}
                onChange={(e) => setFormData({ ...formData, owner: e.target.value })}
                placeholder="e.g., John Doe"
              />
            </div>

            <div>
              <label className="form-label">Due Date</label>
              <input
                type="date"
                className="form-control"
                value={formData.due_date}
                onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
              />
            </div>
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label className="form-label">Acceptance Criteria</label>
            <textarea
              className="form-control"
              value={formData.acceptance_criteria}
              onChange={(e) => setFormData({ ...formData, acceptance_criteria: e.target.value })}
              rows={2}
              placeholder="What evidence will show this action is complete?"
            />
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
              disabled={createActionMutation.isPending}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-success"
              disabled={createActionMutation.isPending || !formData.title}
            >
              {createActionMutation.isPending ? 'Creating...' : 'Create Action'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
