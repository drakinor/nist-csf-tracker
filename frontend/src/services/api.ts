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
  getDashboard: () => api.get('/scores/dashboard'),
  getHistory: (controlId: number) => api.get(`/scores/history/${controlId}`),
};

export const gapApi = {
  list: (params?: { status?: string; severity?: string; gap_type?: string; control_id?: number }) =>
    api.get<Gap[]>('/gaps/', { params }),
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
};

export default api;