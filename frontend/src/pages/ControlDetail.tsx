import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { CheckCircle, XCircle, Eye, AlertTriangle } from 'lucide-react';
import { controlApi, evidenceApi, type Candidate } from '../services/api';

export default function ControlDetail() {
  const { id } = useParams<{ id: string }>();
  const controlId = parseInt(id || '0');
  const queryClient = useQueryClient();

  const [showCandidates, setShowCandidates] = useState(true);
  const [viewingCandidate, setViewingCandidate] = useState<Candidate | null>(null);

  const { data: control } = useQuery({
    queryKey: ['control', controlId],
    queryFn: () => controlApi.get(controlId).then((res) => res.data),
  });

  const { data: candidatesData } = useQuery({
    queryKey: ['candidates', controlId],
    queryFn: () => controlApi.getCandidates(controlId, 20).then((res) => res.data),
  });

  const { data: evidence } = useQuery({
    queryKey: ['evidence', controlId],
    queryFn: () => controlApi.getEvidence(controlId).then((res) => res.data),
  });

  const { data: score } = useQuery({
    queryKey: ['score', controlId],
    queryFn: () => controlApi.getScore(controlId).then((res) => res.data),
  });

  const acceptEvidenceMutation = useMutation({
    mutationFn: async ({
      candidate,
      evidenceType,
      notes,
    }: {
      candidate: Candidate;
      evidenceType: string;
      notes: string;
    }) => {
      // Create evidence
      const evidenceRes = await evidenceApi.create({
        control_id: controlId,
        artifact_id: candidate.artifact_id,
        chunk_id: candidate.chunk_id,
        snippet_text: candidate.snippet_text,
        locator_json: candidate.locator,
        evidence_type: evidenceType,
        notes,
      });

      // Immediately validate as accepted
      await evidenceApi.validate(evidenceRes.data.id, {
        status: 'accepted',
        evidence_type: evidenceType,
        notes,
        confidence: candidate.score / 100,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidates', controlId] });
      queryClient.invalidateQueries({ queryKey: ['evidence', controlId] });
      queryClient.invalidateQueries({ queryKey: ['score', controlId] });
      setViewingCandidate(null);
    },
  });

  const rejectEvidenceMutation = useMutation({
    mutationFn: async ({ candidate, notes }: { candidate: Candidate; notes: string }) => {
      const evidenceRes = await evidenceApi.create({
        control_id: controlId,
        artifact_id: candidate.artifact_id,
        chunk_id: candidate.chunk_id,
        snippet_text: candidate.snippet_text,
        locator_json: candidate.locator,
        notes,
      });

      await evidenceApi.validate(evidenceRes.data.id, {
        status: 'rejected',
        notes,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidates', controlId] });
      setViewingCandidate(null);
    },
  });

  const candidates = candidatesData?.candidates || [];
  const acceptedEvidence = evidence?.filter((e) => e.status === 'accepted') || [];

  return (
    <div className="container">
      {control && (
        <>
          {/* Control Header */}
          <div className="card mb-3">
            <div className="flex items-center justify-between mb-2">
              <div>
                <h1 className="page-title" style={{ marginBottom: '0.25rem' }}>
                  {control.csf_id} - {control.name}
                </h1>
                <div className="flex items-center gap-2">
                  <span className="badge" style={{ background: '#e0e7ff', color: '#3730a3' }}>
                    {control.function}
                  </span>
                  <span className="badge" style={{ background: '#f3f4f6', color: '#374151' }}>
                    {control.category}
                  </span>
                </div>
              </div>
              {score && (
                <div style={{ textAlign: 'right' }}>
                  <div className="text-muted text-sm mb-1">Current Score</div>
                  <span className={`badge badge-${score.score_label}`} style={{ fontSize: '1.25rem', padding: '0.5rem 1rem' }}>
                    {score.score_label.toUpperCase()}
                  </span>
                </div>
              )}
            </div>
            <p className="text-muted">{control.text}</p>
          </div>

          {/* Accepted Evidence */}
          <div className="card mb-3">
            <h2 className="section-title">Validated Evidence ({acceptedEvidence.length})</h2>
            {acceptedEvidence.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {acceptedEvidence.map((ev) => (
                  <div
                    key={ev.id}
                    style={{
                      padding: '1rem',
                      background: '#f0fdf4',
                      border: '1px solid #86efac',
                      borderRadius: '6px',
                    }}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className={`badge badge-${ev.evidence_type || 'pending'}`}>
                        {ev.evidence_type || 'untyped'}
                      </span>
                      <span className="text-xs text-muted">
                        {JSON.stringify(ev.locator_json)}
                      </span>
                    </div>
                    <div className="text-sm">{ev.snippet_text}</div>
                    {ev.notes && (
                      <div className="text-xs text-muted mt-2">Note: {ev.notes}</div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted">No evidence validated yet. Review candidates below.</p>
            )}
          </div>

          {/* Evidence Candidates */}
          <div className="card">
            <div className="flex items-center justify-between mb-2">
              <h2 className="section-title" style={{ marginBottom: 0 }}>
                Evidence Candidates ({candidates.length})
              </h2>
              <button
                className="btn btn-secondary"
                onClick={() => setShowCandidates(!showCandidates)}
              >
                {showCandidates ? 'Hide' : 'Show'}
              </button>
            </div>

            {showCandidates && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {candidates.length > 0 ? (
                  candidates.map((candidate, idx) => (
                    <div
                      key={candidate.chunk_id}
                      style={{
                        padding: '1rem',
                        background: candidate.is_existing_evidence ? '#f3f4f6' : '#fff',
                        border: '1px solid #e5e7eb',
                        borderRadius: '6px',
                        opacity: candidate.is_existing_evidence ? 0.6 : 1,
                      }}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="badge" style={{ background: '#dbeafe', color: '#1e40af' }}>
                            Score: {candidate.score.toFixed(1)}
                          </span>
                          {candidate.is_existing_evidence && (
                            <span className="badge" style={{ background: '#f3f4f6', color: '#6b7280' }}>
                              Already reviewed
                            </span>
                          )}
                        </div>
                        {!candidate.is_existing_evidence && (
                          <button
                            className="btn btn-primary"
                            style={{ padding: '0.25rem 0.75rem', fontSize: '0.875rem' }}
                            onClick={() => setViewingCandidate(candidate)}
                          >
                            <Eye size={14} />
                            Review
                          </button>
                        )}
                      </div>
                      <div className="text-sm mb-2">{candidate.snippet_text}</div>
                      <div className="text-xs text-muted">
                        <strong>Match reasons:</strong> {candidate.match_reasons.join(', ')}
                      </div>
                      <div className="text-xs text-muted mt-1">
                        <strong>Location:</strong> {JSON.stringify(candidate.locator)}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="empty-state">
                    <AlertTriangle className="empty-state-icon" size={48} />
                    <h3 className="empty-state-title">No candidates found</h3>
                    <p className="empty-state-description">
                      Ingest more artifacts to find evidence for this control.
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </>
      )}

      {/* Review Modal */}
      {viewingCandidate && (
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
          }}
          onClick={() => setViewingCandidate(null)}
        >
          <div
            className="card"
            style={{ maxWidth: '800px', margin: '2rem' }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="mb-3">Review Evidence</h3>

            <div style={{ background: '#f9fafb', padding: '1rem', borderRadius: '6px', marginBottom: '1rem' }}>
              <div className="text-sm mb-2">
                <strong>Snippet:</strong>
              </div>
              <div style={{ background: 'white', padding: '1rem', borderRadius: '4px', marginBottom: '1rem' }}>
                {viewingCandidate.full_text}
              </div>
              <div className="text-xs text-muted">
                <strong>Location:</strong> {JSON.stringify(viewingCandidate.locator)}
              </div>
            </div>

            <ValidationForm
              candidate={viewingCandidate}
              onAccept={(evidenceType, notes) => {
                acceptEvidenceMutation.mutate({
                  candidate: viewingCandidate,
                  evidenceType,
                  notes,
                });
              }}
              onReject={(notes) => {
                rejectEvidenceMutation.mutate({
                  candidate: viewingCandidate,
                  notes,
                });
              }}
              onCancel={() => setViewingCandidate(null)}
              isLoading={acceptEvidenceMutation.isPending || rejectEvidenceMutation.isPending}
            />
          </div>
        </div>
      )}
    </div>
  );
}

function ValidationForm({
  candidate,
  onAccept,
  onReject,
  onCancel,
  isLoading,
}: {
  candidate: Candidate;
  onAccept: (evidenceType: string, notes: string) => void;
  onReject: (notes: string) => void;
  onCancel: () => void;
  isLoading: boolean;
}) {
  const [evidenceType, setEvidenceType] = useState('policy');
  const [notes, setNotes] = useState('');

  return (
    <>
      <div className="mb-2">
        <label className="text-sm text-muted">Evidence Type</label>
        <select
          value={evidenceType}
          onChange={(e) => setEvidenceType(e.target.value)}
          style={{
            width: '100%',
            padding: '0.5rem',
            border: '1px solid #e5e7eb',
            borderRadius: '6px',
            marginTop: '0.5rem',
          }}
        >
          <option value="policy">Policy</option>
          <option value="procedure">Procedure</option>
          <option value="technical">Technical Control</option>
          <option value="operational">Operational Evidence</option>
        </select>
      </div>

      <div className="mb-3">
        <label className="text-sm text-muted">Notes (optional)</label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Add any notes about this evidence..."
          rows={3}
          style={{
            width: '100%',
            padding: '0.5rem',
            border: '1px solid #e5e7eb',
            borderRadius: '6px',
            marginTop: '0.5rem',
            fontFamily: 'inherit',
          }}
        />
      </div>

      <div className="flex gap-2">
        <button
          className="btn btn-success"
          onClick={() => onAccept(evidenceType, notes)}
          disabled={isLoading}
        >
          <CheckCircle size={18} />
          {isLoading ? 'Processing...' : 'Accept Evidence'}
        </button>
        <button
          className="btn btn-danger"
          onClick={() => onReject(notes)}
          disabled={isLoading}
        >
          <XCircle size={18} />
          Reject
        </button>
        <button className="btn btn-secondary" onClick={onCancel} disabled={isLoading}>
          Cancel
        </button>
      </div>
    </>
  );
}
