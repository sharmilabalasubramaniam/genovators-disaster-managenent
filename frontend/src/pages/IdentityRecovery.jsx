import React, { useState, useEffect } from 'react';
import { Network, Search, AlertCircle, CheckCircle, List, User } from 'lucide-react';
import axios from 'axios';

const IdentityRecovery = () => {
  const [records, setRecords] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [cluster, setCluster] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [graph, setGraph] = useState(null);

  const API_BASE = 'http://localhost:8000/api/identity_recovery';

  useEffect(() => {
    fetchRecords();
  }, []);

  const fetchRecords = async () => {
    try {
      const res = await axios.get(`${API_BASE}/records`);
      setRecords(res.data);
    } catch (err) {
      setError('Failed to fetch records from Identity Recovery Agent.');
    }
  };

  const toggleSelect = (id) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter(x => x !== id));
    } else {
      setSelectedIds([...selectedIds, id]);
    }
  };

  const recoverIdentity = async () => {
    if (selectedIds.length < 2) {
      setError('Select at least two records to correlate.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post(`${API_BASE}/identity/recover`, { record_ids: selectedIds });
      setCluster(res.data);
      const graphRes = await axios.get(`${API_BASE}/clusters/${res.data.cluster_id}/graph`);
      setGraph(graphRes.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error recovering identity.');
    }
    setLoading(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Identity Recovery Agent</h2>
      </div>
      
      {error && (
        <div className="rounded-xl bg-red-50 p-4 text-sm text-red-600 flex items-center gap-2">
          <AlertCircle className="h-5 w-5" />
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Records Selection Panel */}
        <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="font-bold flex items-center gap-2"><List className="h-5 w-5 text-blue-500" /> Select Records to Correlate</h3>
            <button
              onClick={recoverIdentity}
              disabled={selectedIds.length < 2 || loading}
              className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Analyzing...' : 'Run Correlation Engine'}
            </button>
          </div>
          <div className="space-y-3 h-[500px] overflow-y-auto pr-2">
            {records.map(record => (
              <div
                key={record.record_id}
                onClick={() => toggleSelect(record.record_id)}
                className={`cursor-pointer rounded-xl border p-4 transition-all ${selectedIds.includes(record.record_id) ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-blue-300'}`}
              >
                <div className="flex justify-between">
                  <span className="font-semibold">{record.record_id} ({record.source_type})</span>
                  {selectedIds.includes(record.record_id) && <CheckCircle className="h-5 w-5 text-blue-600" />}
                </div>
                <div className="mt-2 text-sm text-gray-600 grid grid-cols-2 gap-1">
                  <span>Name: {record.name || 'Unknown'}</span>
                  <span>Age: {record.age || 'Unknown'}</span>
                  <span>Location: {record.location || 'Unknown'}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Results Panel */}
        <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
          <h3 className="mb-4 font-bold flex items-center gap-2"><Network className="h-5 w-5 text-pink-500" /> Cluster Analysis Results</h3>
          {cluster ? (
            <div className="space-y-4">
              <div className="rounded-xl bg-gray-50 p-4 border border-gray-100">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500 block mb-1">Cluster ID</span>
                    <span className="font-bold">{cluster.cluster_id}</span>
                  </div>
                  <div>
                    <span className="text-gray-500 block mb-1">Identity Stage</span>
                    <span className="inline-flex items-center rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-semibold text-blue-800">
                      {cluster.identity_stage}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500 block mb-1">Confidence</span>
                    <span className="font-bold">{cluster.confidence}%</span>
                  </div>
                  <div>
                    <span className="text-gray-500 block mb-1">Status</span>
                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${cluster.status === 'REVIEW_REQUIRED' ? 'bg-orange-100 text-orange-800' : 'bg-green-100 text-green-800'}`}>
                      {cluster.status}
                    </span>
                  </div>
                </div>
              </div>

              {cluster.conflicts && cluster.conflicts.length > 0 && (
                <div className="rounded-xl bg-orange-50 p-4 border border-orange-100">
                  <h4 className="font-semibold text-orange-800 mb-2">Detected Conflicts</h4>
                  <ul className="list-disc pl-5 text-sm text-orange-700">
                    {cluster.conflicts.map((c, i) => (
                      <li key={i}>{c}</li>
                    ))}
                  </ul>
                </div>
              )}

              {cluster.evidence && cluster.evidence.length > 0 && (
                <div className="rounded-xl border border-gray-100 p-4">
                  <h4 className="font-semibold mb-2">Supporting Evidence</h4>
                  <ul className="list-disc pl-5 text-sm text-gray-600">
                    {cluster.evidence.map((e, i) => (
                      <li key={i}>{e}</li>
                    ))}
                  </ul>
                </div>
              )}

              {graph && (
                <div className="rounded-xl border border-gray-100 p-4">
                  <h4 className="font-semibold mb-2 flex items-center gap-2"><User className="h-4 w-4" /> Probable Identity</h4>
                  <div className="text-sm bg-gray-50 p-3 rounded-lg">
                    {cluster.possible_identity || 'Not enough data to form a definitive identity.'}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex h-64 flex-col items-center justify-center text-gray-400">
              <Network className="mb-2 h-8 w-8 opacity-20" />
              <p>Select records and run correlation to view results.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default IdentityRecovery;
