import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { CheckCircle, XCircle, Eye, AlertTriangle, Trash2, Sparkles } from 'lucide-react';
import { controlApi, evidenceApi, type Candidate } from '../services/api';

// Helper function to highlight matching keywords
function highlightMatches(text: string, control: any) {
  if (!text || !control) return text;
  
  // Build list of terms to highlight
  const terms: string[] = [];
  
  // Add control ID
  if (control.csf_id) {
    terms.push(control.csf_id);
  }
  
  // Add control name words
  if (control.name) {
    const words = control.name.split(/\s+/).filter((w: string) => w.length > 3);
    terms.push(...words);
  }
  
  // Add custom keywords
  if (control.keywords) {
    const keywords = control.keywords.split(',').map((k: string) => k.trim());
    terms.push(...keywords);
  }
  
  // Function-specific terms
  const functionTerms: Record<string, string[]> = {
    'Govern': ['governance', 'policy', 'oversight', 'cybersecurity', 'risk'],
    'Identify': ['asset', 'inventory', 'risk assessment', 'vulnerability'],
    'Protect': ['access control', 'authentication', 'encryption', 'security'],
    'Detect': ['monitoring', 'detection', 'alert', 'logging', 'SIEM'],
    'Respond': ['incident', 'response', 'mitigation', 'analysis'],
    'Recover': ['recovery', 'continuity', 'restoration', 'backup']
  };
  
  if (control.function && functionTerms[control.function]) {
    terms.push(...functionTerms[control.function]);
  }
  
  if (terms.length === 0) return text;
  
  // Create regex pattern (case insensitive, whole words)
  const pattern = terms
    .map(term => term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
    .join('|');
  const regex = new RegExp(`\\b(${pattern})\\b`, 'gi');
  
  // Split text and wrap matches
  const parts: (string | JSX.Element)[] = [];
  let lastIndex = 0;
  let match;
  let matchCount = 0;
  
  while ((match = regex.exec(text)) !== null && matchCount < 100) {
    // Add text before match
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index));
    }
    
    // Add highlighted match
    parts.push(
      <mark
        key={`match-${matchCount}`}
        style={{
          background: '#fef08a',
          padding: '0.1rem 0.2rem',
          borderRadius: '2px',
          fontWeight: 500
        }}
      >
        {match[0]}
      </mark>
    );
    
    lastIndex = regex.lastIndex;
    matchCount++;
  }
  
  // Add remaining text
  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }
  
  return <>{parts}</>;
}

// Helper function to format locator nicely
function formatLocator(locator: any) {
  if (!locator) return 'Unknown location';
  
  const parts: string[] = [];
  
  if (locator.type === 'pdf' && locator.page) {
    parts.push(`PDF Page ${locator.page}`);
    if (locator.total_pages) {
      parts.push(`of ${locator.total_pages}`);
    }
  } else if (locator.type === 'docx') {
    if (locator.heading_path && locator.heading_path.length > 0) {
      parts.push(`Section: ${locator.heading_path.join(' > ')}`);
    }
    if (locator.para_start !== undefined) {
      parts.push(`Paragraph ${locator.para_start}`);
    }
  } else if (locator.heading) {
    parts.push(`Section: ${locator.heading}`);
  }
  
  return parts.length > 0 ? parts.join(' • ') : JSON.stringify(locator);
}

export default function ControlDetail() {
  const { id } = useParams<{ id: string }>();
  const controlId = parseInt(id || '0');
  const queryClient = useQueryClient();

  const [showCandidates, setShowCandidates] = useState(true);
  const [viewingCandidate, setViewingCandidate] = useState<Candidate | null>(null);
  const [aiAnalysis, setAiAnalysis] = useState<any>(null);
  const [analyzingCandidate, setAnalyzingCandidate] = useState<number | null>(null);

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
        locator_json: candidate.locator_json,
        evidence_type: evidenceType,
        notes,
      });

      // Immediately validate as accepted
      await evidenceApi.validate(evidenceRes.data.id, {
        status: 'accepted',
        evidence_type: evidenceType,
        notes,
        confidence: candidate.match_score / 100,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidates', controlId] });
      queryClient.invalidateQueries({ queryKey: ['evidence', controlId] });
      queryClient.invalidateQueries({ queryKey: ['score', controlId] });
      setViewingCandidate(null);
      setAiAnalysis(null);
    },
  });

  const rejectEvidenceMutation = useMutation({
    mutationFn: async ({ candidate, notes }: { candidate: Candidate; notes: string }) => {
      const evidenceRes = await evidenceApi.create({
        control_id: controlId,
        artifact_id: candidate.artifact_id,
        chunk_id: candidate.chunk_id,
        snippet_text: candidate.snippet_text,
        locator_json: candidate.locator_json,
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
      setAiAnalysis(null);
    },
  });

  const deleteEvidenceMutation = useMutation({
    mutationFn: (evidenceId: number) => evidenceApi.delete(evidenceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['evidence', controlId] });
      queryClient.invalidateQueries({ queryKey: ['score', controlId] });
    },
  });

  const analyzeWithAI = async (candidate: Candidate) => {
    setAnalyzingCandidate(candidate.chunk_id);
    setAiAnalysis(null);
    
    try {
      const response = await controlApi.aiAnalyzeCandidate(controlId, candidate.chunk_id);
      setAiAnalysis(response.data.analysis);
      setViewingCandidate(candidate);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'AI analysis failed. Make sure Ollama is running on localhost:11434');
    } finally {
      setAnalyzingCandidate(null);
    }
  };

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
                  <div className="text-sm mb-1" style={{ color: '#666666' }}>Current Score</div>
                  <span className={`badge badge-${score.score_label}`} style={{ fontSize: '1.25rem', padding: '0.5rem 1rem' }}>
                    {score.score_label.toUpperCase()}
                  </span>
                </div>
              )}
            </div>
            <p style={{ color: '#666666' }}>{control.text}</p>
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
                      color: '#1a1a1a',
                    }}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className={`badge badge-${ev.evidence_type || 'pending'}`}>
                          {ev.evidence_type || 'untyped'}
                        </span>
                        <span className="text-xs" style={{ color: '#666666' }}>
                          {JSON.stringify(ev.locator_json)}
                        </span>
                      </div>
                      <button
                        className="btn btn-danger"
                        style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                        onClick={() => {
                          if (window.confirm('Remove this evidence? This will recalculate the control score.')) {
                            deleteEvidenceMutation.mutate(ev.id);
                          }
                        }}
                        disabled={deleteEvidenceMutation.isPending}
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                    <div className="text-sm" style={{ color: '#1a1a1a' }}>{ev.snippet_text}</div>
                    {ev.notes && (
                      <div className="text-xs mt-2" style={{ color: '#666666' }}>Note: {ev.notes}</div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: '#666666' }}>No evidence validated yet. Review candidates below.</p>
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
                  candidates.map((candidate) => (
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
                            Score: {candidate.match_score.toFixed(1)}
                          </span>
                          {candidate.is_existing_evidence && (
                            <span className="badge" style={{ background: '#f3f4f6', color: '#6b7280' }}>
                              Already reviewed
                            </span>
                          )}
                        </div>
                        {!candidate.is_existing_evidence && (
                          <div className="flex gap-2">
                            <button
                              className="btn"
                              style={{ 
                                padding: '0.25rem 0.75rem', 
                                fontSize: '0.875rem',
                                background: '#8b5cf6',
                                color: 'white'
                              }}
                              onClick={() => analyzeWithAI(candidate)}
                              disabled={analyzingCandidate === candidate.chunk_id}
                            >
                              <Sparkles size={14} />
                              {analyzingCandidate === candidate.chunk_id ? 'Analyzing...' : 'AI Review'}
                            </button>
                            <button
                              className="btn btn-primary"
                              style={{ padding: '0.25rem 0.75rem', fontSize: '0.875rem' }}
                              onClick={() => setViewingCandidate(candidate)}
                            >
                              <Eye size={14} />
                              Review
                            </button>
                          </div>
                        )}
                      </div>
                      <div className="text-sm mb-2" style={{ color: '#1a1a1a' }}>{candidate.snippet_text}</div>
                      <div className="text-xs" style={{ color: '#666666' }}>
                        <strong>Match reasons:</strong> {candidate.match_reasons?.join(', ') || 'N/A'}
                      </div>
                      <div className="text-xs mt-1" style={{ color: '#666666' }}>
                        <strong>Location:</strong> {JSON.stringify(candidate.locator_json)}
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
            padding: '2rem',
          }}
          onClick={() => setViewingCandidate(null)}
        >
          <div
            className="card"
            style={{ 
              maxWidth: '900px', 
              width: '100%',
              maxHeight: '90vh',
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="mb-3">Review Evidence</h3>

            <div style={{ 
              flex: 1, 
              overflowY: 'auto', 
              marginBottom: '1rem',
              paddingRight: '0.5rem'
            }}>
              {/* AI Analysis Section */}
              {aiAnalysis && (
                <div style={{ 
                  background: aiAnalysis.is_relevant ? '#f0fdf4' : '#fef2f2', 
                  border: `2px solid ${aiAnalysis.is_relevant ? '#86efac' : '#fca5a5'}`,
                  padding: '1rem', 
                  borderRadius: '6px', 
                  marginBottom: '1rem' 
                }}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Sparkles size={18} style={{ color: '#8b5cf6' }} />
                      <strong>AI Analysis</strong>
                    </div>
                    <span 
                      className="badge" 
                      style={{ 
                        background: aiAnalysis.is_relevant ? '#dcfce7' : '#fee2e2',
                        color: aiAnalysis.is_relevant ? '#166534' : '#991b1b'
                      }}
                    >
                      {aiAnalysis.is_relevant ? '✓ Relevant' : '✗ Not Relevant'}
                    </span>
                  </div>
                  
                  <div className="text-sm mb-2">
                    <strong>Confidence:</strong>{' '}
                    <span style={{ 
                      color: aiAnalysis.confidence > 0.7 ? '#059669' : aiAnalysis.confidence > 0.4 ? '#d97706' : '#dc2626' 
                    }}>
                      {(aiAnalysis.confidence * 100).toFixed(0)}%
                    </span>
                    <div style={{ 
                      width: '100%', 
                      height: '4px', 
                      background: '#e5e7eb', 
                      borderRadius: '2px',
                      marginTop: '0.25rem',
                      overflow: 'hidden'
                    }}>
                      <div style={{ 
                        width: `${aiAnalysis.confidence * 100}%`, 
                        height: '100%', 
                        background: aiAnalysis.confidence > 0.7 ? '#10b981' : aiAnalysis.confidence > 0.4 ? '#f59e0b' : '#ef4444',
                        transition: 'width 0.3s'
                      }} />
                    </div>
                  </div>
                  
                  {aiAnalysis.evidence_type && (
                    <div className="text-sm mb-2">
                      <strong>Suggested Type:</strong>{' '}
                      <span className="badge" style={{ background: '#e0e7ff', color: '#3730a3' }}>
                        {aiAnalysis.evidence_type}
                      </span>
                    </div>
                  )}
                  
                  <div className="text-sm mb-2">
                    <strong>Reasoning:</strong>
                    <div style={{ marginTop: '0.25rem', color: '#4b5563' }}>
                      {aiAnalysis.reasoning}
                    </div>
                  </div>
                  
                  {aiAnalysis.key_phrases && aiAnalysis.key_phrases.length > 0 && (
                    <div className="text-sm">
                      <strong>Key Phrases:</strong>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {aiAnalysis.key_phrases.map((phrase: string, idx: number) => (
                          <span 
                            key={idx}
                            className="badge" 
                            style={{ background: '#fef3c7', color: '#92400e', fontSize: '0.75rem' }}
                          >
                            {phrase}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              <div style={{ background: '#f9fafb', padding: '1rem', borderRadius: '6px', marginBottom: '1rem' }}>
                <div className="text-sm mb-2">
                  <strong>Full Text:</strong>
                  {viewingCandidate.match_reasons && viewingCandidate.match_reasons.length > 0 && (
                    <div className="text-xs mt-1" style={{ color: '#10b981' }}>
                      ✓ {viewingCandidate.match_reasons.join(' • ')}
                    </div>
                  )}
                </div>
                <div style={{ 
                  background: 'white', 
                  padding: '1rem', 
                  borderRadius: '4px', 
                  marginBottom: '1rem', 
                  color: '#1a1a1a',
                  lineHeight: '1.6',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word'
                }}>
                  {highlightMatches(viewingCandidate.full_text || viewingCandidate.snippet_text, control)}
                </div>
                <div className="text-xs" style={{ color: '#666666' }}>
                  <strong>Location:</strong> {formatLocator(viewingCandidate.locator_json)}
                </div>
              </div>
            </div>

            <ValidationForm
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
              onCancel={() => {
                setViewingCandidate(null);
                setAiAnalysis(null);
              }}
              isLoading={acceptEvidenceMutation.isPending || rejectEvidenceMutation.isPending}
            />
          </div>
        </div>
      )}
    </div>
  );
}

function ValidationForm({
  onAccept,
  onReject,
  onCancel,
  isLoading,
}: {
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
        <label className="text-sm" style={{ display: 'block', marginBottom: '0.5rem', color: '#666666', fontWeight: 500 }}>Evidence Type</label>
        <select
          value={evidenceType}
          onChange={(e) => setEvidenceType(e.target.value)}
          style={{
            width: '100%',
            padding: '0.5rem',
            border: '1px solid #e5e7eb',
            borderRadius: '6px',
            marginTop: '0.5rem',
            backgroundColor: '#ffffff',
            color: '#1a1a1a'
          }}
        >
          <option value="policy">Policy</option>
          <option value="procedure">Procedure</option>
          <option value="technical">Technical Control</option>
          <option value="operational">Operational Evidence</option>
        </select>
      </div>

      <div className="mb-3">
        <label className="text-sm" style={{ display: 'block', marginBottom: '0.5rem', color: '#666666', fontWeight: 500 }}>Notes (optional)</label>
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
            backgroundColor: '#ffffff',
            color: '#1a1a1a'
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
