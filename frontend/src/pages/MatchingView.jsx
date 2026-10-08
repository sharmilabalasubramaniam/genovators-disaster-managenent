import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { CheckCircle, AlertTriangle, User, MapPin, Clock, Search } from 'lucide-react';
import api from '../services/api';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';

export default function MatchingView() {
  const { id } = useParams(); // family case vrn_id
  const navigate = useNavigate();
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    if (!id || id === 'undefined' || id === 'null') {
      setError("Case ID is missing or invalid");
      setLoading(false);
      return;
    }
    api.post(`/matching/cases/${id}`)
      .then(res => {
        setCandidates(res.data.candidates);
        setLoading(false);
      })
      .catch(err => {
        setError(err.response?.data?.detail || err.message);
        setLoading(false);
      });
  }, [id]);

  if (loading) return (
    <div className="flex flex-col items-center justify-center py-20">
      <Search className="h-12 w-12 text-primary animate-pulse mb-4" />
      <h2 className="text-xl font-bold">Comparing 15 hospital, shelter and rescue records...</h2>
    </div>
  );
  if (error) return <ErrorState message={error} />;

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="bg-gray-900 rounded-2xl p-6 text-white text-center shadow-lg">
        <h1 className="text-2xl font-bold mb-2">AI CANDIDATE MATCHING</h1>
        <p className="text-gray-300">Case: <span className="font-mono text-white">{id}</span></p>
        <div className="mt-4 flex justify-center gap-6 text-sm">
          <span className="flex items-center gap-1"><CheckCircle className="h-4 w-4 text-green-400" /> Hospital Records</span>
          <span className="flex items-center gap-1"><CheckCircle className="h-4 w-4 text-green-400" /> Shelter Records</span>
          <span className="flex items-center gap-1"><CheckCircle className="h-4 w-4 text-green-400" /> Rescue Records</span>
        </div>
        <div className="mt-6 border-t border-gray-700 pt-4">
          <p className="text-xl font-bold text-primary-light">Potential Matches Found: {candidates.length}</p>
        </div>
      </div>

      {candidates.length === 0 ? (
        <div className="bg-white rounded-2xl p-8 text-center shadow-sm border border-gray-100">
          <AlertTriangle className="h-12 w-12 text-amber-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-900">No matches found</h2>
          <p className="text-gray-500 mt-2">No sufficiently similar candidate was found in the database.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {candidates.map((cand, idx) => (
            <div key={cand.record_id} className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <div className="flex justify-between items-start mb-4 border-b pb-4">
                <div>
                  <h2 className="text-lg font-bold text-gray-900">Candidate {idx + 1}</h2>
                  <p className="text-gray-500 text-sm">{cand.organization} • <span className="font-mono">{cand.record_id}</span></p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold text-gray-500">Evidence Strength</p>
                  <p className="text-3xl font-black text-primary">{Math.round(cand.score * 100)}%</p>
                </div>
              </div>
              
              <div className="mb-4">
                <span className={`inline-flex items-center rounded-md px-2.5 py-0.5 text-sm font-medium ${
                  cand.confidence === 'HIGH' ? 'bg-green-100 text-green-800' :
                  cand.confidence === 'STRONG' ? 'bg-blue-100 text-blue-800' :
                  cand.confidence === 'POSSIBLE' ? 'bg-amber-100 text-amber-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {cand.confidence} CANDIDATE MATCH
                </span>
              </div>

              <div className="bg-gray-50 rounded-lg p-4 mb-4">
                <h3 className="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wider">AI Match Analysis</h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-y-3 gap-x-4">
                  {cand.signals && typeof cand.signals === 'object' ? (
                    <>
                      <div className="flex justify-between items-center text-sm border-b pb-1"><span className="text-gray-600">Name Similarity</span><span className="font-semibold text-gray-900">{cand.signals.name !== undefined && cand.signals.name !== null ? Math.round(cand.signals.name * 100) + '%' : 'Not available'}</span></div>
                      <div className="flex justify-between items-center text-sm border-b pb-1"><span className="text-gray-600">Age Compatibility</span><span className="font-semibold text-gray-900">{cand.signals.age !== undefined && cand.signals.age !== null ? Math.round(cand.signals.age * 100) + '%' : 'Not available'}</span></div>
                      <div className="flex justify-between items-center text-sm border-b pb-1"><span className="text-gray-600">Gender Match</span><span className="font-semibold text-gray-900">{cand.signals.gender !== undefined && cand.signals.gender !== null ? Math.round(cand.signals.gender * 100) + '%' : 'Not available'}</span></div>
                      <div className="flex justify-between items-center text-sm border-b pb-1"><span className="text-gray-600">Location Proximity</span><span className="font-semibold text-gray-900">{cand.signals.location !== undefined && cand.signals.location !== null ? Math.round(cand.signals.location * 100) + '%' : 'Not available'}</span></div>
                      <div className="flex justify-between items-center text-sm border-b pb-1"><span className="text-gray-600">Time Compatibility</span><span className="font-semibold text-gray-900">{cand.signals.time !== undefined && cand.signals.time !== null ? Math.round(cand.signals.time * 100) + '%' : 'Not available'}</span></div>
                      <div className="flex justify-between items-center text-sm border-b pb-1"><span className="text-gray-600">Physical Description</span><span className="font-semibold text-gray-900">{cand.signals.physical !== undefined && cand.signals.physical !== null ? Math.round(cand.signals.physical * 100) + '%' : 'Not available'}</span></div>
                      <div className="flex justify-between items-center text-sm border-b pb-1"><span className="text-gray-600">Face Similarity</span><span className="font-semibold text-gray-900">{cand.signals.face !== undefined && cand.signals.face !== null ? Math.round(cand.signals.face * 100) + '%' : 'Not available'}</span></div>
                    </>
                  ) : (
                    <div className="col-span-3 text-sm text-gray-500 italic">Signal details unavailable</div>
                  )}
                </div>
              </div>

              <div className="bg-amber-50 border-l-4 border-amber-400 p-3 mb-4 rounded-r-md">
                <p className="text-amber-800 font-bold text-sm">Potential Match — Requires Human Verification</p>
                <p className="text-amber-700 text-xs mt-1">AI MATCH ≠ IDENTITY CONFIRMED. An authorized human must review the evidence.</p>
              </div>

              <div className="flex justify-end">
                <button onClick={() => navigate(`/verification/${id}?candidate=${cand.record_id}`)} className="px-4 py-2 border border-gray-300 rounded-md text-sm font-semibold text-gray-700 hover:bg-gray-50">
                  VIEW EVIDENCE
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="text-center py-6">
        <p className="text-sm text-gray-500 italic">"AI generates candidate matches. Authorized verification is required before reunification."</p>
      </div>
    </div>
  );
}
