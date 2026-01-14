import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Upload, Link as LinkIcon, FileText, Trash2, Eye } from 'lucide-react';
import { artifactApi, type Artifact } from '../services/api';

export default function Artifacts() {
  const [showUpload, setShowUpload] = useState(false);
  const [showUrlIngest, setShowUrlIngest] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [url, setUrl] = useState('');
  const [tags, setTags] = useState('');
  const [viewingChunks, setViewingChunks] = useState<number | null>(null);

  const queryClient = useQueryClient();

  const { data: artifacts, isLoading } = useQuery({
    queryKey: ['artifacts'],
    queryFn: () => artifactApi.list().then(res => res.data),
  });

  const uploadMutation = useMutation({
    mutationFn: ({ file, tags }: { file: File; tags: string }) =>
      artifactApi.upload(file, tags),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['artifacts'] });
      setShowUpload(false);
      setSelectedFile(null);
      setTags('');
    },
  });

  const urlMutation = useMutation({
    mutationFn: ({ url, tags }: { url: string; tags: string }) =>
      artifactApi.ingestUrl(url, tags),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['artifacts'] });
      setShowUrlIngest(false);
      setUrl('');
      setTags('');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => artifactApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['artifacts'] });
    },
  });

  const { data: chunks } = useQuery({
    queryKey: ['artifact-chunks', viewingChunks],
    queryFn: () => artifactApi.getChunks(viewingChunks!).then(res => res.data),
    enabled: viewingChunks !== null,
  });

  const handleUpload = () => {
    if (selectedFile) {
      uploadMutation.mutate({ file: selectedFile, tags });
    }
  };

  const handleUrlIngest = () => {
    if (url) {
      urlMutation.mutate({ url, tags });
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'N/A';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="container">
      <div className="page-header">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="page-title">Artifacts</h1>
            <p className="page-description">
              Manage ingested documents, URLs, and evidence sources
            </p>
          </div>
          <div className="flex gap-2">
            <button
              className="btn btn-secondary"
              onClick={() => setShowUrlIngest(!showUrlIngest)}
            >
              <LinkIcon size={18} />
              Ingest URL
            </button>
            <button
              className="btn btn-primary"
              onClick={() => setShowUpload(!showUpload)}
            >
              <Upload size={18} />
              Upload File
            </button>
          </div>
        </div>
      </div>

      {/* Upload Form */}
      {showUpload && (
        <div className="card mb-3">
          <h3 className="mb-2">Upload Artifact</h3>
          <div className="mb-2">
            <label className="text-sm text-muted">File</label>
            <input
              type="file"
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              accept=".docx,.pdf,.txt,.md,.xlsx"
              style={{ display: 'block', marginTop: '0.5rem' }}
            />
          </div>
          <div className="mb-2">
            <label className="text-sm text-muted">Tags (comma-separated)</label>
            <input
              type="text"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="e.g., policy, access control, 2024"
              style={{
                width: '100%',
                padding: '0.5rem',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                marginTop: '0.5rem',
              }}
            />
          </div>
          <div className="flex gap-2">
            <button
              className="btn btn-primary"
              onClick={handleUpload}
              disabled={!selectedFile || uploadMutation.isPending}
            >
              {uploadMutation.isPending ? 'Uploading...' : 'Upload'}
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => setShowUpload(false)}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* URL Ingest Form */}
      {showUrlIngest && (
        <div className="card mb-3">
          <h3 className="mb-2">Ingest URL</h3>
          <div className="mb-2">
            <label className="text-sm text-muted">URL</label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/policy"
              style={{
                width: '100%',
                padding: '0.5rem',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                marginTop: '0.5rem',
              }}
            />
          </div>
          <div className="mb-2">
            <label className="text-sm text-muted">Tags (comma-separated)</label>
            <input
              type="text"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="e.g., policy, external, vendor"
              style={{
                width: '100%',
                padding: '0.5rem',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                marginTop: '0.5rem',
              }}
            />
          </div>
          <div className="flex gap-2">
            <button
              className="btn btn-primary"
              onClick={handleUrlIngest}
              disabled={!url || urlMutation.isPending}
            >
              {urlMutation.isPending ? 'Ingesting...' : 'Ingest'}
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => setShowUrlIngest(false)}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Artifacts List */}
      <div className="card">
        {isLoading ? (
          <div className="spinner" />
        ) : artifacts && artifacts.length > 0 ? (
          <table>
            <thead>
              <tr>
                <th>Title</th>
                <th>Type</th>
                <th>Size</th>
                <th>Collected</th>
                <th>Tags</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {artifacts.map((artifact: Artifact) => (
                <tr key={artifact.id}>
                  <td>
                    <div className="flex items-center gap-2">
                      <FileText size={16} />
                      <strong>{artifact.title}</strong>
                    </div>
                    {artifact.source_url && (
                      <div className="text-xs text-muted mt-1">
                        {artifact.source_url}
                      </div>
                    )}
                  </td>
                  <td>
                    <span className="badge" style={{ background: '#f3f4f6', color: '#374151' }}>
                      {artifact.type.toUpperCase()}
                    </span>
                  </td>
                  <td className="text-sm text-muted">
                    {formatFileSize(artifact.file_size)}
                  </td>
                  <td className="text-sm text-muted">
                    {formatDate(artifact.collected_at)}
                  </td>
                  <td className="text-sm text-muted">
                    {artifact.tags || '-'}
                  </td>
                  <td>
                    <div className="flex gap-2">
                      <button
                        className="btn btn-secondary"
                        style={{ padding: '0.25rem 0.5rem', fontSize: '0.875rem' }}
                        onClick={() => setViewingChunks(artifact.id)}
                      >
                        <Eye size={14} />
                      </button>
                      <button
                        className="btn btn-danger"
                        style={{ padding: '0.25rem 0.5rem', fontSize: '0.875rem' }}
                        onClick={() => {
                          if (confirm('Delete this artifact?')) {
                            deleteMutation.mutate(artifact.id);
                          }
                        }}
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="empty-state">
            <FileText className="empty-state-icon" size={48} />
            <h3 className="empty-state-title">No artifacts yet</h3>
            <p className="empty-state-description">
              Upload documents or ingest URLs to start building your evidence base.
            </p>
          </div>
        )}
      </div>

      {/* Chunks Viewer */}
      {viewingChunks && chunks && (
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
          onClick={() => setViewingChunks(null)}
        >
          <div
            className="card"
            style={{ maxWidth: '800px', maxHeight: '80vh', overflow: 'auto', margin: '2rem' }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-3">
              <h3>Artifact Chunks ({chunks.length})</h3>
              <button className="btn btn-secondary" onClick={() => setViewingChunks(null)}>
                Close
              </button>
            </div>
            {chunks.map((chunk, idx) => (
              <div
                key={chunk.id}
                style={{
                  background: '#f9fafb',
                  padding: '1rem',
                  borderRadius: '6px',
                  marginBottom: '1rem',
                }}
              >
                <div className="text-xs text-muted mb-1">
                  Chunk #{idx + 1} | {JSON.stringify(chunk.locator_json)}
                </div>
                <div className="text-sm">{chunk.chunk_text.substring(0, 500)}...</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
