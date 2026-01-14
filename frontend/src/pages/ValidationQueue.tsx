import { useQuery, useMutation, useQueryClient } from '@tantml:function_calls>tanstack/react-query';
import { CheckCircle, XCircle, AlertTriangle, Filter, ArrowUpDown, Trash2, CheckSquare, Square } from 'lucide-react';
import { Link } from 'react-router-dom';
import { evidenceApi, controlApi } from '../services/api';
import { useState, useMemo } from 'react';
import axios from 'axios';

export default function ValidationQueue() {
  const queryClient = useQueryClient();
  const [notes, setNotes] = useState<Record<number, string>>({});
  const [evidenceTypes, setEvidenceTypes] = useState<Record<number, string>>({});
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  
  // Filters and sorting
  const [statusFilter, setStatusFilter] = useState<string>('pending');
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [sortBy, setSortBy] = useState<string>('created_at');
  const [sortOrder, setSortOrder] = useState<string>('desc');
  const [showFilters, setShowFilters] = useState(false);

  const { data: allEvidence, isLoading } = useQuery({
    queryKey: ['evidence', statusFilter, typeFilter, sortBy, sortOrder],
    queryFn: () => evidenceApi.list({ 
      status: statusFilter || undefined, 
      evidence_type: typeFilter || undefined,
      sort_by: sortBy,
      sort_order: sortOrder
    }).then((res) => res.data),
  });

  const { data: controls } = useQuery({
    queryKey: ['controls'],
    queryFn: () => controlApi.list().then((res) => res.data),
  });

  const validateMutation = useMutation({
    mutationFn: ({ id, status, notes, evidenceType }: {
      id: number;
      status: string;
      notes?: string;
      evidenceType?: string;
    }) => evidenceApi.validate(id, { status, notes, evidence_type: evidenceType }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['evidence'] });
      queryClient.invalidateQueries({ queryKey: ['scores'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  const bulkValidateMutation = useMutation({
    mutationFn: ({ evidence_ids, status, notes, evidence_type }: {
      evidence_ids: number[];
      status: string;
      notes?: string;
      evidence_type?: string;
    }) => axios.post('http://localhost:8000/api/evidence/bulk-validate', {
      evidence_ids,
      status,
      notes,
      evidence_type
    }),
    onSuccess: () => {
      setSelectedIds(new Set());
      queryClient.invalidateQueries({ queryKey: ['evidence'] });
      queryClient.invalidateQueries({ queryKey: ['scores'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  const bulkDeleteMutation = useMutation({
    mutationFn: (evidence_ids: number[]) => 
      axios.post('http://localhost:8000/api/evidence/bulk-delete', evidence_ids),
    onSuccess: () => {
      setSelectedIds(new Set());
      queryClient.invalidateQueries({ queryKey: ['evidence'] });
      queryClient.invalidateQueries({ queryKey: ['scores'] });
    },
  });

  const getControlInfo = (controlId: number) => {
    return controls?.find((c) => c.id === controlId);
  };

  const toggleSelection = (id: number) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedIds(newSelected);
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === allEvidence?.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(allEvidence?.map(e => e.id) || []));
    }
  };

  const handleBulkAccept = () => {
    if (selectedIds.size === 0) return;
    bulkValidateMutation.mutate({
      evidence_ids: Array.from(selectedIds),
      status: 'accepted',
      evidence_type: 'operational'
    });
  };

  const handleBulkReject = () => {
    if (selectedIds.size === 0) return;
    bulkValidateMutation.mutate({
      evidence_ids: Array.from(selectedIds),
      status: 'rejected'
    });
  };

  const handleBulkDelete = () => {
    if (selectedIds.size === 0) return;
    if (confirm(`Delete ${selectedIds.size} evidence items?`)) {
      bulkDeleteMutation.mutate(Array.from(selectedIds));
    }
  };

  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">Validation Queue</h1>
        <p className="page-description">
          Review and validate evidence items with bulk operations
        </p>
      </div>

      {/* Filters and Bulk Actions */}
      <div className="card" style={{ marginBottom: '1rem' }}>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
          {/* Filter Toggle */}
          <button
            className="btn btn-secondary"
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter size={16} />
            Filters
          </button>

          {/* Bulk Actions */}
          {selectedIds.size > 0 && (
            <>
              <div style={{ 
                padding: '0.5rem 1rem', 
                background: 'var(--bg-secondary)', 
                borderRadius: '6px',
                fontWeight: '500'
              }}>
                {selectedIds.size} selected
              </div>
              <button
                className="btn btn-success"
                onClick={handleBulkAccept}
                disabled={bulkValidateMutation.isPending}
              >
                <CheckCircle size={16} />
                Accept All
              </button>
              <button
                className="btn btn-danger"
                onClick={handleBulkReject}
                disabled={bulkValidateMutation.isPending}
              >
                <XCircle size={16} />
                Reject All
              </button>
              <button
                className="btn btn-danger"
                onClick={handleBulkDelete}
                disabled={bulkDeleteMutation.isPending}
              >
                <Trash2 size={16} />
                Delete
              </button>
            </>
          )}
        </div>

        {/* Filter Controls */}
        {showFilters && (
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '1rem',
            marginTop: '1rem',
            paddingTop: '1rem',
            borderTop: '1px solid var(--border-color)'
          }}>
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
                <option value="pending">Pending</option>
                <option value="accepted">Accepted</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500' }}>
                Evidence Type
              </label>
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="form-control"
              >
                <option value="">All Types</option>
                <option value="policy">Policy</option>
                <option value="procedure">Procedure</option>
                <option value="technical">Technical</option>
                <option value="operational">Operational</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500' }}>
                Sort By
              </label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="form-control"
              >
                <option value="created_at">Created Date</option>
                <option value="validated_at">Validated Date</option>
                <option value="status">Status</option>
                <option value="confidence">Confidence</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500' }}>
                Order
              </label>
              <select
                value={sortOrder}
                onChange={(e) => setSortOrder(e.target.value)}
                className="form-control"
              >
                <option value="desc">Descending</option>
                <option value="asc">Ascending</option>
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Evidence List */}
      <div className="card">
        {isLoading ? (
          <div className="spinner" />
        ) : allEvidence && allEvidence.length > 0 ? (
          <>
            {/* Select All */}
            <div style={{ 
              padding: '1rem', 
              borderBottom: '1px solid var(--border-color)',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              cursor: 'pointer'
            }}
            onClick={toggleSelectAll}
            >
              {selectedIds.size === allEvidence.length ? (
                <CheckSquare size={20} />
              ) : (
                <Square size={20} />
              )}
              <span style={{ fontWeight: '500' }}>Select All ({allEvidence.length})</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', padding: '1rem' }}>
              {allEvidence.map((evidence) => {
                const control = getControlInfo(evidence.control_id);
                const isSelected = selectedIds.has(evidence.id);
                const statusColor = evidence.status === 'accepted' ? '#059669' : 
                                   evidence.status === 'rejected' ? '#dc2626' : '#f59e0b';
                
                return (
                  <div
                    key={evidence.id}
                    style={{
                      padding: '1.5rem',
                      background: isSelected ? 'var(--bg-secondary)' : 'transparent',
                      border: `2px solid ${isSelected ? '#2563eb' : 'var(--border-color)'}`,
                      borderRadius: '8px',
                      transition: 'all 0.2s'
                    }}
                  >
                    <div style={{ display: 'flex', gap: '1rem' }}>
                      {/* Checkbox */}
                      <div 
                        onClick={() => toggleSelection(evidence.id)}
                        style={{ cursor: 'pointer', paddingTop: '0.25rem' }}
                      >
                        {isSelected ? (
                          <CheckSquare size={20} color="#2563eb" />
                        ) : (
                          <Square size={20} />
                        )}
                      </div>

                      <div style={{ flex: 1 }}>
                        {/* Header: Control + Status */}
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.75rem' }}>
                          <div>
                            <Link
                              to={`/controls/${evidence.control_id}`}
                              style={{ textDecoration: 'none' }}
                            >
                              <strong style={{ color: '#2563eb' }}>
                                {control?.csf_id} - {control?.name}
                              </strong>
                            </Link>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                              {control?.function} / {control?.category}
                            </div>
                          </div>
                          <span style={{ 
                            padding: '0.25rem 0.75rem', 
                            background: statusColor, 
                            color: 'white',
                            borderRadius: '12px',
                            fontSize: '0.75rem',
                            fontWeight: '600',
                            textTransform: 'uppercase'
                          }}>
                            {evidence.status}
                          </span>
                        </div>

                        {/* Evidence Snippet */}
                        <div
                          style={{
                            background: 'var(--bg-primary)',
                            padding: '1rem',
                            borderRadius: '6px',
                            marginBottom: '1rem',
                            border: '1px solid var(--border-color)'
                          }}
                        >
                          <div style={{ fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                            {evidence.snippet_text}
                          </div>
                          {evidence.evidence_type && (
                            <span className={`badge badge-${evidence.evidence_type}`}>
                              {evidence.evidence_type}
                            </span>
                          )}
                        </div>

                        {/* Validation Form (only for pending) */}
                        {evidence.status === 'pending' && (
                          <>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '0.5rem', marginBottom: '1rem' }}>
                              <select
                                value={evidenceTypes[evidence.id] || 'operational'}
                                onChange={(e) =>
                                  setEvidenceTypes({ ...evidenceTypes, [evidence.id]: e.target.value })
                                }
                                className="form-control"
                              >
                                <option value="policy">Policy</option>
                                <option value="procedure">Procedure</option>
                                <option value="technical">Technical</option>
                                <option value="operational">Operational</option>
                              </select>

                              <input
                                type="text"
                                value={notes[evidence.id] || ''}
                                onChange={(e) => setNotes({ ...notes, [evidence.id]: e.target.value })}
                                placeholder="Add notes (optional)..."
                                className="form-control"
                              />
                            </div>

                            {/* Actions */}
                            <div className="flex gap-2">
                              <button
                                className="btn btn-success"
                                onClick={() =>
                                  validateMutation.mutate({
                                    id: evidence.id,
                                    status: 'accepted',
                                    notes: notes[evidence.id],
                                    evidenceType: evidenceTypes[evidence.id] || 'operational',
                                  })
                                }
                                disabled={validateMutation.isPending}
                              >
                                <CheckCircle size={16} />
                                Accept
                              </button>
                              <button
                                className="btn btn-danger"
                                onClick={() =>
                                  validateMutation.mutate({
                                    id: evidence.id,
                                    status: 'rejected',
                                    notes: notes[evidence.id],
                                  })
                                }
                                disabled={validateMutation.isPending}
                              >
                                <XCircle size={16} />
                                Reject
                              </button>
                            </div>
                          </>
                        )}

                        {/* Notes display for validated items */}
                        {evidence.status !== 'pending' && evidence.notes && (
                          <div style={{ 
                            fontSize: '0.875rem', 
                            color: 'var(--text-muted)',
                            marginTop: '0.5rem',
                            fontStyle: 'italic'
                          }}>
                            Notes: {evidence.notes}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </>
        ) : (
          <div className="empty-state">
            <AlertTriangle className="empty-state-icon" size={48} />
            <h3 className="empty-state-title">No evidence found</h3>
            <p className="empty-state-description">
              {statusFilter === 'pending' ? 
                'All evidence has been reviewed. Great work!' :
                'Try adjusting your filters to see more results.'
              }
            </p>
          </div>
        )}
      </div>
    </div>
  );
}