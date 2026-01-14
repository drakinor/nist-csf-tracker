import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { controlApi, evidenceLinkApi } from '../services/api';
import { X, Link as LinkIcon, AlertCircle, CheckCircle } from 'lucide-react';

interface LinkEvidenceModalProps {
  evidenceId: number;
  currentControlId: number;
  onClose: () => void;
}

export function LinkEvidenceModal({ evidenceId, currentControlId, onClose }: LinkEvidenceModalProps) {
  const [selectedControlId, setSelectedControlId] = useState<number | null>(null);
  const [relevanceNotes, setRelevanceNotes] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  const queryClient = useQueryClient();

  const { data: controls = [] } = useQuery({
    queryKey: ['controls'],
    queryFn: async () => {
      const response = await controlApi.list();
      return response.data;
    },
  });

  const { data: existingLinks = [] } = useQuery({
    queryKey: ['evidence-links', evidenceId],
    queryFn: async () => {
      const response = await evidenceLinkApi.getLinks(evidenceId);
      return response.data;
    },
  });

  const linkMutation = useMutation({
    mutationFn: async () => {
      if (!selectedControlId) throw new Error('No control selected');
      return evidenceLinkApi.linkToControl(evidenceId, {
        control_id: selectedControlId,
        relevance_notes: relevanceNotes || undefined,
        linked_by: 'user',
      });
    },
    onSuccess: () => {
      setSuccess('Evidence successfully linked to control');
      setSelectedControlId(null);
      setRelevanceNotes('');
      queryClient.invalidateQueries({ queryKey: ['evidence-links'] });
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to link evidence');
    },
  });

  const unlinkMutation = useMutation({
    mutationFn: (controlId: number) => evidenceLinkApi.unlinkFromControl(evidenceId, controlId),
    onSuccess: () => {
      setSuccess('Link removed successfully');
      queryClient.invalidateQueries({ queryKey: ['evidence-links'] });
    },
  });

  const linkedControlIds = new Set([currentControlId, ...existingLinks.map((link: any) => link.control_id)]);
  const availableControls = controls.filter((control: any) => !linkedControlIds.has(control.id));

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg w-full max-w-2xl">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <LinkIcon className="h-5 w-5 text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Link Evidence to Controls
            </h2>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="px-6 py-4 space-y-4">
          {error && (
            <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 rounded flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-red-600" />
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}
          
          {success && (
            <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 rounded flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <p className="text-sm text-green-600">{success}</p>
            </div>
          )}

          {existingLinks.length > 0 && (
            <div>
              <h3 className="text-sm font-medium mb-2">Linked Controls ({existingLinks.length})</h3>
              <div className="space-y-2">
                {existingLinks.map((link: any) => {
                  const control = controls.find((c: any) => c.id === link.control_id);
                  return (
                    <div key={link.id} className="p-3 bg-blue-50 dark:bg-blue-900/20 border rounded flex justify-between">
                      <div>
                        <span className="font-medium">{control?.csf_id}</span> - {control?.name}
                      </div>
                      <button onClick={() => unlinkMutation.mutate(link.control_id)} className="text-red-600">
                        <X className="h-5 w-5" />
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-2">Select Control</label>
            <select
              value={selectedControlId || ''}
              onChange={(e) => setSelectedControlId(Number(e.target.value))}
              className="w-full px-3 py-2 border rounded"
            >
              <option value="">Choose a control...</option>
              {availableControls.map((control: any) => (
                <option key={control.id} value={control.id}>
                  {control.csf_id} - {control.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Relevance Notes</label>
            <textarea
              value={relevanceNotes}
              onChange={(e) => setRelevanceNotes(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border rounded"
              placeholder="Explain why this evidence is relevant..."
            />
          </div>

          <button
            onClick={() => linkMutation.mutate()}
            disabled={!selectedControlId}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            Link to Control
          </button>
        </div>
      </div>
    </div>
  );
}
