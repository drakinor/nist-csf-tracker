import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Artifact {
  id: number;
  title: string;
  type: string;
  source_path?: string;
  source_url?: string;
  collected_at: string;
  hash?: string;
  tags?: string;
  file_size?: number;
  metadata_json?: any;
}

export interface Control {
  id: number;
  csf_id: string;
  function: string;
  category: string;
  subcategory: string;
  name: string;
  text: string;
  intent?: string;
  scoring_rules?: any;
  rubric_json?: any;
  keywords?: string;
}

export interface Evidence {
  id: number;
  control_id: number;
  artifact_id: number;
  chunk_id: number;
  snippet_text: string;
  locator_json: any;
  status: string;
  notes?: string;
  confidence?: string;
  evidence_type?: string;
  validated_by?: string;
  validated_at?: string;
  created_at: string;
}

export interface EvidenceControlLink {
  id: number;
  evidence_id: number;
  control_id: number;
  relevance_notes?: string;
  linked_at: string;
  linked_by?: string;
}

export interface LinkedEvidence {
  evidence: Evidence;
  link: EvidenceControlLink;
}

export interface Score {
  id: number;
  control_id: number;
  score_value: number;
  score_label: string;
  score_rationale?: string;
  calculated_at: string;
  method: string;
  notes?: string;
}

export interface Gap {
  id: number;
  control_id: number;
  gap_type: string;
  description: string;
  severity: string;
  status: string;
  created_at: string;
  resolved_at?: string;
}

export interface Action {
  id: number;
  gap_id?: number;
  control_id?: number;
  title: string;
  description?: string;
  owner?: string;
  due_date?: string;
  status: string;
  acceptance_criteria?: string;
  created_at: string;
  completed_at?: string;
}

export interface Risk {
  id: number;
  control_id: number;
  gap_id?: number;
  risk_title: string;
  risk_statement: string;
  likelihood: string;
  impact: string;
  inherent_risk_score: number;
  residual_risk_score?: number;
  treatment: string;
  treatment_rationale?: string;
  compensating_controls?: string;
  acceptance_approver?: string;
  acceptance_approved_at?: string;
  acceptance_expiry_date?: string;
  mitigation_plan?: string;
  mitigation_owner?: string;
  mitigation_target_date?: string;
  status: string;
  review_frequency: string;
  last_reviewed_at?: string;
  next_review_date?: string;
  risk_category?: string;
  created_at: string;
  created_by?: string;
  updated_at?: string;
}

export interface Candidate {
  chunk_id: number;
  artifact_id: number;
  artifact_title: string;
  match_score: number;
  snippet_text: string;
  full_text?: string;
  locator_json: any;
  match_reasons?: string[];
  is_existing_evidence?: boolean;
}

export const artifactApi = {
  list: () => api.get<Artifact[]>('/artifacts/'),
  get: (id: number) => api.get<Artifact>(`/artifacts/${id}`),
  upload: (file: File, tags: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('tags', tags);
    return api.post('/artifacts/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  ingestUrl: (url: string, tags: string) => {
    const formData = new FormData();
    formData.append('url', url);
    formData.append('tags', tags);
    return api.post('/artifacts/ingest-url', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getChunks: (id: number) => api.get(`/artifacts/${id}/chunks`),
  delete: (id: number) => api.delete(`/artifacts/${id}`),
};

export const controlApi = {
  list: (params?: { function?: string; category?: string }) =>
    api.get<Control[]>('/controls/', { params }),
  get: (id: number) => api.get<Control>(`/controls/${id}`),
  getEvidence: (id: number) => api.get<Evidence[]>(`/controls/${id}/evidence`),
  getCandidates: (id: number, limit?: number) =>
    api.get<{ control_id: number; csf_id: string; candidates: Candidate[] }>(
      `/controls/${id}/candidates`,
      { params: { limit } }
    ),
  getScore: (id: number) => api.get<Score>(`/controls/${id}/score`),
  getFunctionsSummary: () => api.get('/controls/functions/summary'),
  getCategoriesSummary: () => api.get('/controls/categories/summary'),
  getLinkedEvidence: (id: number) => api.get<{ primary: Evidence[]; linked: LinkedEvidence[] }>(`/controls/${id}/linked-evidence`),
  aiAnalyzeCandidate: (controlId: number, candidateId: number) => 
    api.post(`/controls/${controlId}/ai-analyze-candidate?candidate_id=${candidateId}`),
};

export const evidenceApi = {
  list: (params?: { control_id?: number; status?: string }) =>
    api.get<Evidence[]>('/evidence/', { params }),
  get: (id: number) => api.get<Evidence>(`/evidence/${id}`),
  create: (data: {
    control_id: number;
    artifact_id: number;
    chunk_id: number;
    snippet_text: string;
    locator_json: any;
    evidence_type?: string;
    notes?: string;
  }) => api.post<Evidence>('/evidence/', data),
  validate: (id: number, data: {
    status: string;
    notes?: string;
    evidence_type?: string;
    confidence?: number;
  }) => api.patch<Evidence>(`/evidence/${id}/validate`, data),
  delete: (id: number) => api.delete(`/evidence/${id}`),
};

export const evidenceLinkApi = {
  linkToControl: (evidenceId: number, data: {
    control_id: number;
    relevance_notes?: string;
    linked_by?: string;
  }) => api.post<EvidenceControlLink>(`/evidence/${evidenceId}/link`, data),
  unlinkFromControl: (evidenceId: number, controlId: number) =>
    api.delete(`/evidence/${evidenceId}/link/${controlId}`),
  getLinks: (evidenceId: number) => api.get<EvidenceControlLink[]>(`/evidence/${evidenceId}/links`),
};

export const scoreApi = {
  list: () => api.get<Score[]>('/scores/'),
  recalculateAll: () => api.post('/scores/recalculate-all'),
  recalculateWeighted: () => api.post('/scores/recalculate-weighted'),
  getDashboard: () => api.get('/scores/dashboard'),
  getHistory: (controlId: number) => api.get(`/scores/history/${controlId}`),
  getLowestScoring: (limit: number = 10) => api.get(`/scores/lowest?limit=${limit}`),
  getTrends: (days: number = 30) => api.get(`/scores/trends?days=${days}`),
  createSnapshot: () => api.post('/scores/snapshot'),
  overrideScore: (controlId: number, data: {
    score_value: number;
    score_label: string;
    notes: string;
    user?: string;
  }) => api.post(`/scores/${controlId}/override`, data),
};

export const gapApi = {
  list: (params?: { status?: string; severity?: string; gap_type?: string; control_id?: number }) =>
    api.get<Gap[]>('/gaps/', { params }),
  get: (id: number) => api.get<Gap>(`/gaps/${id}`),
  getSummary: () => api.get('/gaps/summary'),
  create: (data: { control_id: number; gap_type: string; description: string; severity?: string }) =>
    api.post<Gap>('/gaps/', data),
  update: (id: number, data: { status?: string; severity?: string; description?: string }) =>
    api.patch<Gap>(`/gaps/${id}`, data),
  regenerate: () => api.post('/gaps/regenerate'),
};

export const actionApi = {
  list: (params?: { status?: string }) =>
    api.get<Action[]>('/actions/', { params }),
  get: (id: number) => api.get<Action>(`/actions/${id}`),
  getSummary: () => api.get('/actions/summary/stats'),
  getKanban: () => api.get('/actions/kanban/board'),
  create: (data: {
    gap_id?: number;
    control_id?: number;
    title: string;
    description?: string;
    owner?: string;
    due_date?: string;
    acceptance_criteria?: string;
  }) => api.post<Action>('/actions/', data),
  update: (id: number, data: {
    title?: string;
    description?: string;
    owner?: string;
    due_date?: string;
    status?: string;
    acceptance_criteria?: string;
  }) => api.patch<Action>(`/actions/${id}`, data),
  delete: (id: number) => api.delete(`/actions/${id}`),
};

export const riskApi = {
  list: (params?: { 
    status?: string; 
    treatment?: string; 
    risk_category?: string;
    control_id?: number;
    min_risk_score?: number;
  }) => api.get<Risk[]>('/risks/', { params }),
  get: (id: number) => api.get<Risk>(`/risks/${id}`),
  getSummary: () => api.get('/risks/summary/stats'),
  getHeatmap: () => api.get('/risks/heatmap/data'),
  getHighestRisks: (limit?: number) => api.get('/risks/top/highest', { params: { limit } }),
  getDueForReview: () => api.get<Risk[]>('/risks/due/reviews'),
  create: (data: {
    control_id: number;
    gap_id?: number;
    risk_title: string;
    risk_statement: string;
    likelihood: string;
    impact: string;
    treatment?: string;
    risk_category?: string;
  }) => api.post<Risk>('/risks/', data),
  update: (id: number, data: Partial<Risk>) =>
    api.patch<Risk>(`/risks/${id}`, data),
  delete: (id: number) => api.delete(`/risks/${id}`),
  accept: (id: number, data: {
    acceptance_approver: string;
    compensating_controls?: string;
    acceptance_expiry_date?: string;
    treatment_rationale?: string;
  }) => api.post<Risk>(`/risks/${id}/accept`, data),
  mitigate: (id: number, data: {
    mitigation_plan: string;
    mitigation_owner: string;
    mitigation_target_date?: string;
    residual_risk_score?: number;
    treatment_rationale?: string;
  }) => api.post<Risk>(`/risks/${id}/mitigate`, data),
  close: (id: number, closure_notes?: string) =>
    api.post<Risk>(`/risks/${id}/close`, null, { params: { closure_notes } }),
  markReviewed: (id: number, review_notes?: string) =>
    api.post<Risk>(`/risks/${id}/review`, null, { params: { review_notes } }),
  generateFromGaps: () => api.post('/risks/generate/from-gaps'),
};

export default api;
