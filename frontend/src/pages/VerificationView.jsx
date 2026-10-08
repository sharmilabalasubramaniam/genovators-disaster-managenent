import React, { useEffect, useState } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { CheckCircle, AlertTriangle, ShieldCheck, Clock, FileText } from 'lucide-react';
import api from '../services/api';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';

export default function VerificationView() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  let candidateId = searchParams.get('candidate');
  if (candidateId === 'undefined' || candidateId === 'null') candidateId = null;
  let caseId = id || searchParams.get('caseId');
  if (caseId === 'undefined' || caseId === 'null') caseId = null;
  const navigate = useNavigate();
  
  const [verificationData, setVerificationData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Guard against missing case id
  useEffect(() => {
    if (!caseId) {
      setError('Case ID is missing in URL');
      setLoading(false);
    }
  }, [caseId]);
  const [rejectReason, setRejectReason] = useState('');
  const [moreEvidenceNotes, setMoreEvidenceNotes] = useState('');

  const loadData = () => {
    setLoading(true);
    api.get(`/verification/${caseId}/candidate/${candidateId}`)
      .then(res => {
        if (res.data.status === "NOT_STARTED") {
          // Auto start if not started
          return api.post(`/verification/${caseId}/start`, { candidate_vrn_id: candidateId })
            .then(() => api.get(`/verification/${caseId}/candidate/${candidateId}`));
        }
        return res;
      })
      .then(res => {
        setVerificationData(res.data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.response?.data?.detail || err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    if (!candidateId) {
      setError("Candidate ID is missing");
      setLoading(false);
      return;
    }
    loadData();
  }, [caseId, candidateId]);

  const handleApprove = () => {
    if (window.confirm("Are you sure you want to mark this candidate as VERIFIED?")) {
      api.post(`/verification/${caseId}/approve`)
        .then(() => {
          alert("Case VERIFIED");
          navigate(`/cases/${caseId}`);
        })
        .catch(err => alert("Error approving: " + err.message));
    }
  };

  const handleReject = () => {
    if (!rejectReason) {
      alert("Please provide a reason for rejection");
      return;
    }
    api.post(`/verification/${caseId}/reject`, { reason: rejectReason })
      .then(() => {
        alert("Candidate REJECTED");
        navigate(`/cases/${caseId}`);
      })
      .catch(err => alert("Error rejecting: " + err.message));
  };

  const handleRequestEvidence = () => {
    if (!moreEvidenceNotes) {
      alert("Please provide notes on what evidence is required");
      return;
    }
    api.post(`/verification/${caseId}/request-evidence`, { notes: moreEvidenceNotes })
      .then(() => loadData())
      .catch(err => alert("Error requesting evidence: " + err.message));
  };

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;
  if (!verificationData) return <ErrorState message="Not found" />;

  const strength = verificationData.strength;
  const isHighStrength = strength.strength_score >= 0.75;
  
  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <ShieldCheck className="h-6 w-6 text-primary" /> MULTI-FACTOR VERIFICATION
        </h1>
        <p className="text-gray-500 mt-1">Case: <span className="font-mono text-gray-900">{caseId}</span></p>
        <p className="text-gray-500">Candidate: <span className="font-mono text-gray-900">{candidateId}</span></p>
        <p className="text-gray-500 mt-2 text-sm font-semibold">
          Current Status: <span className="uppercase text-blue-600 bg-blue-50 px-2 py-1 rounded">{verificationData.status}</span>
        </p>
      </div>

      {(verificationData.case_photo_url || verificationData.candidate_photo_url) && (
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
          <h2 className="text-lg font-bold mb-4 flex items-center gap-2">Photo Verification</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Missing Person (Reported)</h3>
              {verificationData.case_photo_url ? (
                <img src={verificationData.case_photo_url} alt="Missing" className="mx-auto rounded-lg shadow-sm border border-gray-200 max-h-64 object-cover" />
              ) : (
                <div className="h-48 bg-gray-100 rounded-lg flex items-center justify-center text-gray-400">No Photo</div>
              )}
            </div>
            <div className="text-center">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Found Candidate</h3>
              {verificationData.candidate_photo_url ? (
                <img src={verificationData.candidate_photo_url} alt="Found" className="mx-auto rounded-lg shadow-sm border border-gray-200 max-h-64 object-cover" />
              ) : (
                <div className="h-48 bg-gray-100 rounded-lg flex items-center justify-center text-gray-400">No Photo</div>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="bg-gray-900 rounded-2xl p-8 text-white shadow-lg text-center">
        <h2 className="text-gray-400 text-sm font-bold uppercase tracking-wider mb-2">EVIDENCE STRENGTH</h2>
        <div className="text-5xl font-black text-white mb-2">{Math.round(strength.strength_score * 100)}%</div>
        <div className="text-xl font-bold text-primary-light mb-4">
          {isHighStrength ? 'HIGH' : 'MEDIUM'} EVIDENCE STRENGTH
        </div>
        <p className="text-gray-300 mb-6">
          {isHighStrength ? 'Multiple supporting signals detected. Authorized verification is required.' : 'Insufficient signals. Proceed with caution.'}
        </p>
        
        <div className="bg-gray-800 rounded-lg p-4 text-left max-w-md mx-auto">
          {strength.evidence_list.map((ev, i) => (
            <div key={i} className="flex justify-between items-center py-2 border-b border-gray-700 last:border-0 text-sm">
              <span className="text-gray-300 font-medium">{ev.type}</span>
              <span className={`font-semibold flex items-center gap-1 ${
                ev.status === 'SUPPORTED' ? 'text-green-400' :
                ev.status === 'PARTIAL' ? 'text-amber-400' :
                'text-red-400'
              }`}>
                {ev.status === 'SUPPORTED' ? '✓' : ev.status === 'PARTIAL' ? '⚠' : '✕'} {ev.status}
              </span>
            </div>
          ))}
        </div>
      </div>

      {strength.conflicts > 0 && (
        <div className="bg-red-50 rounded-2xl p-6 border border-red-200">
          <h2 className="text-red-800 font-bold flex items-center gap-2 mb-2">
            <AlertTriangle className="h-5 w-5" /> REVIEW REQUIRED
          </h2>
          <p className="text-red-700 text-sm">{strength.conflicts} conflict(s) detected in the evidence records.</p>
        </div>
      )}

      {/* Timeline Section */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
        <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
          <Clock className="h-5 w-5 text-gray-400" /> Evidence Timeline
        </h2>
        <div className="space-y-4">
           {strength.evidence_list.map((ev, i) => (
             <div key={i} className="flex gap-4 items-start">
                <div className="text-xs text-gray-500 w-16 pt-1 flex-shrink-0">
                  {new Date(ev.uploaded_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                </div>
                <div className="flex-grow border-l-2 border-gray-200 pl-4 pb-4">
                  <p className="text-sm font-semibold text-gray-900">{ev.source}</p>
                  <p className="text-sm text-gray-600">{ev.description}</p>
                </div>
             </div>
           ))}
        </div>
      </div>

      {/* Officer Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-200 space-y-3">
          <h3 className="font-bold text-gray-900">Request Evidence</h3>
          <input 
            type="text" 
            placeholder="What is needed?" 
            className="w-full border p-2 rounded text-sm"
            value={moreEvidenceNotes}
            onChange={e => setMoreEvidenceNotes(e.target.value)}
          />
          <button onClick={handleRequestEvidence} className="w-full bg-amber-100 text-amber-800 font-bold py-2 rounded text-sm hover:bg-amber-200">
            REQUEST MORE EVIDENCE
          </button>
        </div>
        
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-200 space-y-3">
          <h3 className="font-bold text-gray-900">Reject Candidate</h3>
          <input 
            type="text" 
            placeholder="Reason for rejection" 
            className="w-full border p-2 rounded text-sm"
            value={rejectReason}
            onChange={e => setRejectReason(e.target.value)}
          />
          <button onClick={handleReject} className="w-full bg-red-100 text-red-800 font-bold py-2 rounded text-sm hover:bg-red-200">
            REJECT CANDIDATE
          </button>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-200 space-y-3">
          <h3 className="font-bold text-gray-900">Approve Verification</h3>
          <p className="text-xs text-gray-500">Only approve if evidence is sufficient.</p>
          <button onClick={handleApprove} className="w-full bg-green-600 text-white font-bold py-2 rounded text-sm hover:bg-green-700">
            APPROVE VERIFICATION
          </button>
        </div>
      </div>
      
    </div>
  );
}
