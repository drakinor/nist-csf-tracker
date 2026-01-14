import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Artifact {
  id: number;
  title: string;
  type: string;
  source_path?: string;
  source_url?: string;
  collected_at: string;
  hash: string;
  tags?: string;
  file_size?: number;
}

export interface ArtifactChunk {
  id: number;
  artifact_id: number;
  chunk_text: string;
  locator_json: any;
  chunk_index: number;
}

export interface Control {
  id: number;
  csf_id: string;
  function: string;
  category: string;
  subcategory: string;
  name: string;
  text: string;
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
  confidence?: number;
  evidence_type?: string;
  validated_at?: string;
  created_at: string;
}

export interface Score {
  id: number;
  control_id: number;
  score_value: number;
  score_label: string;
  calculated_at: string;
  method: string;
  notes?: string;
}

export interface Candidate {
  chunk_id: number;
  artifact_id: number;
  snippet_text: string;
  full_text: string;
  locator: any;
  score: number;
  match_reasons: string[];
  is_existing_evidence: boolean;
}

// API functions
export const artifactApi = {
  list: () => api.get<Artifact[]>('/artifacts/'),
  get: (id: number) => api.get<Artifact>(`/artifacts/${id}`),
  getChunks: (id: number) => api.get<ArtifactChunk[]>(`/artifacts/${id}/chunks`),
  upload: (file: File, tags?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (tags) formData.append('tags', tags);
    return api.post('/artifacts/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  ingestUrl: (url: string, tags?: string) => {
    const formData = new FormData();
    formData.append('url', url);
    if (tags) formData.append('tags', tags);
    return api.post('/artifacts/ingest-url', formData);
  },
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

export const scoreApi = {
  list: () => api.get<Score[]>('/scores/'),
  recalculateAll: () => api.post('/scores/recalculate-all'),
  getDashboard: () => api.get('/scores/dashboard'),
  getHistory: (controlId: number) => api.get(`/scores/history/${controlId}`),
};

export default api;
