import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { Link } from 'react-router-dom';
import { evidenceApi, controlApi } from '../services/api';
import { useState } from 'react';

export default function ValidationQueue() {
  const queryClient = useQueryClient();
  const [notes, setNotes] = useState<Record<number, string>>({});
  const [evidenceTypes, setEvidenceTypes] = useState<Record<number, string>>({});

  const { data: pendingEvidence, isLoading } = useQuery({
    queryKey: ['evidence', 'pending'],
    queryFn: () => evidenceApi.list({ status: 'pending' }).then((res) => res.data),
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
    },
  });

  const getControlInfo = (controlId: number) => {
    return controls?.find((c) => c.id === controlId);
  };

  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">Validation Queue</h1>
        <p className="page-description">
          Review and validate pending evidence items
        </p>
      </div>

      <div className="card">
        {isLoading ? (
          <div className="spinner" />
        ) : pendingEvidence && pendingEvidence.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {pendingEvidence.map((evidence) => {
              const control = getControlInfo(evidence.control_id);
              return (
                <div
                  key={evidence.id}
                  style={{
                    padding: '1.5rem',
                    background: '#fffbeb',
                    border: '1px solid #fcd34d',
                    borderRadius: '8px',
                  }}
                >
                  {/* Control Info */}
                  <div className="mb-2">
                    <Link
                      to={`/controls/${evidence.control_id}`}
                      style={{ textDecoration: 'none' }}
                    >
                      <strong style={{ color: '#2563eb' }}>
                        {control?.csf_id} - {control?.name}
                      </strong>
                    </Link>
                    <div className="text-xs text-muted mt-1">
                      {control?.function} / {control?.category}
                    </div>
                  </div>

                  {/* Evidence Snippet */}
                  <div
                    style={{
                      background: 'white',
                      padding: '1rem',
                      borderRadius: '6px',
                      marginBottom: '1rem',
                    }}
                  >
                    <div className="text-sm mb-2">{evidence.snippet_text}</div>
                    <div className="text-xs text-muted">
                      <strong>Location:</strong> {JSON.stringify(evidence.locator_json)}
                    </div>
                  </div>

                  {/* Validation Form */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '0.5rem', marginBottom: '1rem' }}>
                    <select
                      value={evidenceTypes[evidence.id] || 'policy'}
                      onChange={(e) =>
                        setEvidenceTypes({ ...evidenceTypes, [evidence.id]: e.target.value })
                      }
                      style={{
                        padding: '0.5rem',
                        border: '1px solid #e5e7eb',
                        borderRadius: '6px',
                      }}
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
                      style={{
                        padding: '0.5rem',
                        border: '1px solid #e5e7eb',
                        borderRadius: '6px',
                      }}
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
                          evidenceType: evidenceTypes[evidence.id] || 'policy',
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
                </div>
              );
            })}
          </div>
        ) : (
          <div className="empty-state">
            <AlertTriangle className="empty-state-icon" size={48} />
            <h3 className="empty-state-title">No pending validations</h3>
            <p className="empty-state-description">
              All evidence has been reviewed. Great work!
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
