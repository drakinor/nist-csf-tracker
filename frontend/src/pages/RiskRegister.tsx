import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { riskApi, controlApi, gapApi, Risk, Control, Gap } from '../services/api';
import { AlertTriangle, TrendingUp, CheckCircle2, XCircle, Clock, Plus, Eye, Filter } from 'lucide-react';

export default function RiskRegister() {
  const queryClient = useQueryClient();
  const [selectedRisk, setSelectedRisk] = useState<Risk | null>(null);
  const [showRiskModal, setShowRiskModal] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterTreatment, setFilterTreatment] = useState<string>('all');
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [minRiskScore, setMinRiskScore] = useState<number>(0);

  // Fetch risks with filters
  const { data: risks = [], isLoading } = useQuery({
    queryKey: ['risks', filterStatus, filterTreatment, filterCategory, minRiskScore],
    queryFn: async () => {
      const params: any = {};
      if (filterStatus !== 'all') params.status = filterStatus;
      if (filterTreatment !== 'all') params.treatment = filterTreatment;
      if (filterCategory !== 'all') params.risk_category = filterCategory;
      if (minRiskScore > 0) params.min_risk_score = minRiskScore;
      
      const response = await riskApi.list(params);
      return response.data;
    },
  });

  // Fetch summary stats
  const { data: summary } = useQuery({
    queryKey: ['risk-summary'],
    queryFn: async () => {
      const response = await riskApi.getSummary();
      return response.data;
    },
  });

  // Fetch heat map data
  const { data: heatmapData } = useQuery({
    queryKey: ['risk-heatmap'],
    queryFn: async () => {
      const response = await riskApi.getHeatmap();
      return response.data;
    },
  });

  // Fetch highest risks
  const { data: highestRisks = [] } = useQuery({
    queryKey: ['highest-risks'],
    queryFn: async () => {
      const response = await riskApi.getHighestRisks(5);
      return response.data;
    },
  });

  // Fetch due for review
  const { data: dueForReview = [] } = useQuery({
    queryKey: ['risks-due-review'],
    queryFn: async () => {
      const response = await riskApi.getDueForReview();
      return response.data;
    },
  });

  // Generate risks from gaps mutation
  const generateFromGapsMutation = useMutation({
    mutationFn: () => riskApi.generateFromGaps(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risks'] });
      queryClient.invalidateQueries({ queryKey: ['risk-summary'] });
      alert('Risks generated from gaps successfully!');
    },
  });

  // Helper functions
  const getRiskLevelColor = (score: number) => {
    if (score >= 20) return 'text-red-600 bg-red-50';
    if (score >= 10) return 'text-orange-600 bg-orange-50';
    if (score >= 5) return 'text-yellow-600 bg-yellow-50';
    return 'text-green-600 bg-green-50';
  };

  const getRiskLevelLabel = (score: number) => {
    if (score >= 20) return 'Critical';
    if (score >= 10) return 'High';
    if (score >= 5) return 'Medium';
    return 'Low';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'closed': return <CheckCircle2 className="w-4 h-4 text-green-600" />;
      case 'accepted': return <CheckCircle2 className="w-4 h-4 text-blue-600" />;
      case 'under_review': return <Clock className="w-4 h-4 text-yellow-600" />;
      default: return <AlertTriangle className="w-4 h-4 text-red-600" />;
    }
  };

  const getTreatmentBadge = (treatment: string) => {
    const styles: any = {
      accept: 'bg-blue-100 text-blue-800',
      mitigate: 'bg-green-100 text-green-800',
      transfer: 'bg-purple-100 text-purple-800',
      avoid: 'bg-red-100 text-red-800',
    };
    return <span className={`px-2 py-1 text-xs font-semibold rounded ${styles[treatment] || 'bg-gray-100 text-gray-800'}`}>
      {treatment.toUpperCase()}
    </span>;
  };

  if (isLoading) {
    return <div className="p-8 text-center">Loading risk register...</div>;
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <AlertTriangle className="w-8 h-8 text-red-600" />
          Risk Register
        </h1>
        <div className="flex gap-2">
          <button
            onClick={() => generateFromGapsMutation.mutate()}
            className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 flex items-center gap-2"
            disabled={generateFromGapsMutation.isPending}
          >
            <Plus className="w-4 h-4" />
            Generate from Gaps
          </button>
          <button
            onClick={() => setShowRiskModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            New Risk
          </button>
        </div>
      </div>

      {/* Summary Statistics */}
      {summary && (
        <div className="grid grid-cols-5 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm text-gray-600">Total Risks</div>
            <div className="text-3xl font-bold">{summary.total}</div>
          </div>
          <div className="bg-red-50 p-4 rounded-lg shadow">
            <div className="text-sm text-red-600">Critical</div>
            <div className="text-3xl font-bold text-red-600">{summary.by_risk_level?.critical || 0}</div>
          </div>
          <div className="bg-orange-50 p-4 rounded-lg shadow">
            <div className="text-sm text-orange-600">High</div>
            <div className="text-3xl font-bold text-orange-600">{summary.by_risk_level?.high || 0}</div>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg shadow">
            <div className="text-sm text-yellow-600">Medium</div>
            <div className="text-3xl font-bold text-yellow-600">{summary.by_risk_level?.medium || 0}</div>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg shadow">
            <div className="text-sm text-blue-600">Due for Review</div>
            <div className="text-3xl font-bold text-blue-600">{summary.due_for_review || 0}</div>
          </div>
        </div>
      )}

      {/* Risk Heat Map */}
      {heatmapData && (
        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <h2 className="text-xl font-bold mb-4">Risk Heat Map</h2>
          <RiskHeatMap heatmap={heatmapData.heatmap} />
        </div>
      )}

      {/* Highest Risks Widget */}
      {highestRisks.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-red-600" />
            Top 5 Highest Risks
          </h2>
          <div className="space-y-2">
            {highestRisks.map((risk: any) => (
              <div key={risk.risk_id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div className="flex-1">
                  <div className="font-semibold">{risk.risk_title}</div>
                  <div className="text-sm text-gray-600">{risk.control_csf_id}: {risk.control_name}</div>
                </div>
                <div className="flex items-center gap-4">
                  {getTreatmentBadge(risk.treatment)}
                  <div className={`px-3 py-1 rounded font-bold ${getRiskLevelColor(risk.risk_score)}`}>
                    {risk.risk_score}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow mb-4">
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4" />
            <span className="font-semibold">Filters:</span>
          </div>
          
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-3 py-1 border rounded"
          >
            <option value="all">All Status</option>
            <option value="open">Open</option>
            <option value="under_review">Under Review</option>
            <option value="accepted">Accepted</option>
            <option value="mitigated">Mitigated</option>
            <option value="closed">Closed</option>
          </select>

          <select
            value={filterTreatment}
            onChange={(e) => setFilterTreatment(e.target.value)}
            className="px-3 py-1 border rounded"
          >
            <option value="all">All Treatment</option>
            <option value="accept">Accept</option>
            <option value="mitigate">Mitigate</option>
            <option value="transfer">Transfer</option>
            <option value="avoid">Avoid</option>
          </select>

          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="px-3 py-1 border rounded"
          >
            <option value="all">All Categories</option>
            <option value="operational">Operational</option>
            <option value="technical">Technical</option>
            <option value="compliance">Compliance</option>
            <option value="strategic">Strategic</option>
          </select>

          <label className="flex items-center gap-2">
            Min Risk Score:
            <input
              type="number"
              min="0"
              max="25"
              value={minRiskScore}
              onChange={(e) => setMinRiskScore(Number(e.target.value))}
              className="w-20 px-2 py-1 border rounded"
            />
          </label>

          <button
            onClick={() => {
              setFilterStatus('all');
              setFilterTreatment('all');
              setFilterCategory('all');
              setMinRiskScore(0);
            }}
            className="px-3 py-1 text-sm text-gray-600 hover:text-gray-900"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Risk List */}
      <div className="bg-white rounded-lg shadow">
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-semibold">Risk Title</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">Category</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">Score</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">Likelihood</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">Impact</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">Treatment</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">Status</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {risks.map((risk) => (
                <tr key={risk.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div className="font-medium">{risk.risk_title}</div>
                    <div className="text-sm text-gray-600 truncate max-w-md">{risk.risk_statement}</div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-1 text-xs rounded bg-gray-100">
                      {risk.risk_category || 'N/A'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className={`px-3 py-1 rounded font-bold text-center ${getRiskLevelColor(risk.inherent_risk_score)}`}>
                      {risk.inherent_risk_score}
                      <div className="text-xs font-normal">{getRiskLevelLabel(risk.inherent_risk_score)}</div>
                    </div>
                  </td>
                  <td className="px-4 py-3 capitalize">{risk.likelihood}</td>
                  <td className="px-4 py-3 capitalize">{risk.impact}</td>
                  <td className="px-4 py-3">{getTreatmentBadge(risk.treatment)}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      {getStatusIcon(risk.status)}
                      <span className="capitalize text-sm">{risk.status.replace('_', ' ')}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => {
                        setSelectedRisk(risk);
                        setShowRiskModal(true);
                      }}
                      className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 flex items-center gap-1"
                    >
                      <Eye className="w-3 h-3" />
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {risks.length === 0 && (
            <div className="p-8 text-center text-gray-500">
              No risks found. Click "Generate from Gaps" to create risks automatically.
            </div>
          )}
        </div>
      </div>

      {/* Risk Detail/Edit Modal */}
      {showRiskModal && (
        <RiskModal
          risk={selectedRisk}
          onClose={() => {
            setShowRiskModal(false);
            setSelectedRisk(null);
          }}
          onSave={() => {
            queryClient.invalidateQueries({ queryKey: ['risks'] });
            queryClient.invalidateQueries({ queryKey: ['risk-summary'] });
            setShowRiskModal(false);
            setSelectedRisk(null);
          }}
        />
      )}
    </div>
  );
}

// Risk Heat Map Component
function RiskHeatMap({ heatmap }: { heatmap: any }) {
  const likelihoods = ['low', 'medium', 'high', 'very_high'];
  const impacts = ['low', 'medium', 'high', 'critical'];
  
  const getCellColor = (count: number) => {
    if (count === 0) return 'bg-gray-100';
    if (count <= 2) return 'bg-yellow-100';
    if (count <= 5) return 'bg-orange-200';
    return 'bg-red-300';
  };

  return (
    <div className="overflow-x-auto">
      <table className="border-collapse">
        <thead>
          <tr>
            <th className="p-2 border"></th>
            {impacts.map((impact) => (
              <th key={impact} className="p-2 border text-sm font-semibold capitalize">
                {impact}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {likelihoods.slice().reverse().map((likelihood) => (
            <tr key={likelihood}>
              <th className="p-2 border text-sm font-semibold capitalize text-right">
                {likelihood.replace('_', ' ')}
              </th>
              {impacts.map((impact) => {
                const key = `${likelihood}_${impact}`;
                const count = heatmap[key] || 0;
                return (
                  <td
                    key={key}
                    className={`p-4 border text-center font-bold text-lg ${getCellColor(count)}`}
                  >
                    {count}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="mt-4 text-sm text-gray-600">
        <strong>Likelihood</strong> (vertical) × <strong>Impact</strong> (horizontal) = Risk Score
      </div>
    </div>
  );
}

// Risk Modal Component (simplified - would be expanded for full CRUD)
function RiskModal({ risk, onClose, onSave }: { risk: Risk | null; onClose: () => void; onSave: () => void }) {
  // This is a simplified modal - in production, would include full edit/create forms
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Risk Details</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700 text-2xl">×</button>
        </div>

        {risk ? (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold mb-1">Risk Title</label>
              <div className="p-2 bg-gray-50 rounded">{risk.risk_title}</div>
            </div>

            <div>
              <label className="block text-sm font-semibold mb-1">Risk Statement</label>
              <div className="p-2 bg-gray-50 rounded whitespace-pre-wrap">{risk.risk_statement}</div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold mb-1">Likelihood</label>
                <div className="p-2 bg-gray-50 rounded capitalize">{risk.likelihood}</div>
              </div>
              <div>
                <label className="block text-sm font-semibold mb-1">Impact</label>
                <div className="p-2 bg-gray-50 rounded capitalize">{risk.impact}</div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold mb-1">Risk Score</label>
                <div className="p-2 bg-gray-50 rounded font-bold">{risk.inherent_risk_score}</div>
              </div>
              <div>
                <label className="block text-sm font-semibold mb-1">Treatment</label>
                <div className="p-2 bg-gray-50 rounded capitalize">{risk.treatment}</div>
              </div>
            </div>

            {risk.treatment === 'accept' && risk.compensating_controls && (
              <div>
                <label className="block text-sm font-semibold mb-1">Compensating Controls</label>
                <div className="p-2 bg-gray-50 rounded">{risk.compensating_controls}</div>
              </div>
            )}

            {risk.treatment === 'mitigate' && risk.mitigation_plan && (
              <div>
                <label className="block text-sm font-semibold mb-1">Mitigation Plan</label>
                <div className="p-2 bg-gray-50 rounded whitespace-pre-wrap">{risk.mitigation_plan}</div>
              </div>
            )}

            <div>
              <label className="block text-sm font-semibold mb-1">Status</label>
              <div className="p-2 bg-gray-50 rounded capitalize">{risk.status.replace('_', ' ')}</div>
            </div>

            <div className="flex justify-end gap-2 mt-6">
              <button onClick={onClose} className="px-4 py-2 border rounded hover:bg-gray-50">
                Close
              </button>
            </div>
          </div>
        ) : (
          <div>
            <p>Create new risk form would go here...</p>
            <div className="flex justify-end gap-2 mt-6">
              <button onClick={onClose} className="px-4 py-2 border rounded hover:bg-gray-50">
                Cancel
              </button>
              <button onClick={onSave} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                Create Risk
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
