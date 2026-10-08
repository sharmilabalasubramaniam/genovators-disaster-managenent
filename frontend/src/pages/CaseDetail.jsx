import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import { ArrowLeft, User, MapPin, Clock, FileText, CheckCircle, Activity, ShieldCheck } from 'lucide-react';

export default function CaseDetail() { 
  const { id } = useParams();
  const navigate = useNavigate();
  const [caseData, setCaseData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!id || id === 'undefined' || id === 'null') {
      setError("Case ID is missing or invalid");
      setLoading(false);
      return;
    }
    api.get(`/cases/${id}`)
      .then(res => {
        setCaseData(res.data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.response?.data?.detail || err.message || "Failed to load case");
        setLoading(false);
      });
  }, [id]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;
  if (!caseData) return <ErrorState message="Case not found" />;

  const person = caseData.person;
  const familyReport = caseData.family_reports?.[0];
  const lastKnownLoc = caseData.location_records?.find(l => l.location_type === 'Last Known') || caseData.location_records?.[0];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button onClick={() => navigate(-1)} className="p-2 hover:bg-gray-100 rounded-full transition-colors">
          <ArrowLeft className="h-5 w-5 text-gray-600" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
            {caseData.vrn_id}
            <span className="text-sm px-3 py-1 bg-blue-50 text-blue-700 rounded-full font-semibold border border-blue-100 uppercase">
              {caseData.status}
            </span>
          </h1>
          <p className="text-sm text-gray-500 mt-1">Reported on {new Date(caseData.created_at).toLocaleString()}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Column: Details */}
        <div className="md:col-span-2 space-y-6">
          
          {/* Person Info */}
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <h2 className="text-lg font-bold border-b pb-3 mb-4 flex items-center gap-2">
              <User className="h-5 w-5 text-primary" /> Person Information
            </h2>
            <div className="grid grid-cols-2 gap-y-4 gap-x-8">
              <div>
                <p className="text-sm text-gray-500 font-medium">Full Name</p>
                <p className="text-base font-semibold text-gray-900">{person.first_name} {person.last_name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500 font-medium">Age & Gender</p>
                <p className="text-base text-gray-900">{person.age || 'Unknown'} yrs, {person.gender || 'Unknown'}</p>
              </div>
              <div className="col-span-2">
                <p className="text-sm text-gray-500 font-medium">Distinguishing Features</p>
                <p className="text-base text-gray-900 bg-gray-50 p-3 rounded-lg mt-1 text-sm border border-gray-100">
                  {person.distinguishing_features || 'None reported'}
                </p>
              </div>
            </div>
          </div>

          {/* Report Source & Location */}
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <h2 className="text-lg font-bold border-b pb-3 mb-4 flex items-center gap-2">
              <FileText className="h-5 w-5 text-primary" /> Report Details
            </h2>
            
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-500 font-medium flex items-center gap-2">
                   Report Source
                </p>
                {familyReport ? (
                  <div className="mt-1">
                    <p className="text-gray-900 font-medium">Family Member: {familyReport.reporter_name}</p>
                    <p className="text-sm text-gray-600">Relationship: {familyReport.relationship_to_person}</p>
                    <p className="text-sm text-gray-600">Contact: {familyReport.reporter_contact}</p>
                  </div>
                ) : caseData.hospital_records?.length > 0 ? (
                  <div className="mt-1">
                    <p className="text-gray-900 font-medium">Hospital: {caseData.hospital_records[0].hospital_name}</p>
                    <p className="text-sm text-gray-600">Condition: {caseData.hospital_records[0].condition_summary || 'N/A'}</p>
                    <p className="text-sm text-gray-600">Admitted: {caseData.hospital_records[0].admission_date ? new Date(caseData.hospital_records[0].admission_date).toLocaleString() : 'Unknown'}</p>
                  </div>
                ) : caseData.shelter_records?.length > 0 ? (
                  <div className="mt-1">
                    <p className="text-gray-900 font-medium">Shelter: {caseData.shelter_records[0].shelter_name}</p>
                    <p className="text-sm text-gray-600">Checked In: {caseData.shelter_records[0].check_in_date ? new Date(caseData.shelter_records[0].check_in_date).toLocaleString() : 'Unknown'}</p>
                  </div>
                ) : caseData.rescue_records?.length > 0 ? (
                  <div className="mt-1">
                    <p className="text-gray-900 font-medium">Rescue Team: {caseData.rescue_records[0].rescue_team}</p>
                    <p className="text-sm text-gray-600">Rescue Date: {caseData.rescue_records[0].rescue_date ? new Date(caseData.rescue_records[0].rescue_date).toLocaleString() : 'Unknown'}</p>
                  </div>
                ) : (
                  <p className="mt-1 text-gray-600">System generated or other source</p>
                )}
              </div>
              
              <div className="pt-2">
                <p className="text-sm text-gray-500 font-medium flex items-center gap-2 mb-1">
                  <MapPin className="h-4 w-4" /> Location
                </p>
                <p className="text-gray-900 mb-2">{lastKnownLoc ? lastKnownLoc.address : 'Location unknown'}</p>
                {caseData.location_records?.length > 0 && (
                  <button onClick={() => navigate(`/map/${caseData.vrn_id}`)} className="text-sm font-semibold text-primary hover:underline flex items-center gap-1">
                    <MapPin className="h-4 w-4" /> View Map Tracking
                  </button>
                )}
              </div>
            </div>
          </div>

        </div>

        {/* Right Column: Statuses */}
        <div className="space-y-6">
          <div className="bg-gray-50 rounded-2xl p-6 border border-gray-200">
            <h2 className="text-lg font-bold mb-4 text-gray-900">Workflow Status</h2>
            
            <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent">
              
              <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                <div className="flex items-center justify-center w-10 h-10 rounded-full border border-white bg-blue-100 text-blue-600 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
                  <Activity className="h-5 w-5" />
                </div>
                <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded border border-blue-200 bg-blue-50 shadow-sm">
                  <div className="flex items-center justify-between space-x-2 mb-2">
                    <div className="font-bold text-slate-900">AI Matching</div>
                  </div>
                  <div className="text-sm text-slate-500 font-medium mb-3">
                    Status: {caseData.match_results && caseData.match_results.length > 0 ? 'MATCHING COMPLETE' : 'NOT STARTED'}
                  </div>
                  {caseData.match_results && caseData.match_results.length > 0 ? (
                    <button onClick={() => navigate(`/matches/${caseData.vrn_id}`)} className="w-full rounded bg-white border border-gray-300 py-1.5 text-xs font-bold text-gray-700 hover:bg-gray-50">
                      VIEW {caseData.match_results.length} MATCHES
                    </button>
                  ) : (
                    <button onClick={() => navigate(`/matches/${caseData.vrn_id}`)} className="w-full rounded bg-primary py-1.5 text-xs font-bold text-white hover:bg-primary/90 shadow-sm">
                      RUN AI MATCHING
                    </button>
                  )}
                </div>
              </div>
              
              <div className={`relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group ${caseData.status === 'In Verification' || caseData.status === 'Verified' ? 'is-active' : ''}`}>
                <div className={`flex items-center justify-center w-10 h-10 rounded-full border border-white shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10 ${caseData.status === 'In Verification' ? 'bg-amber-100 text-amber-600' : caseData.status === 'Verified' ? 'bg-green-100 text-green-600' : 'bg-slate-200 text-slate-500'}`}>
                  <ShieldCheck className="h-5 w-5" />
                </div>
                <div className={`w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded border shadow-sm ${caseData.status === 'In Verification' ? 'border-amber-200 bg-amber-50' : caseData.status === 'Verified' ? 'border-green-200 bg-green-50' : 'border-slate-200 bg-white'}`}>
                  <div className="flex items-center justify-between space-x-2 mb-1">
                    <div className="font-bold text-slate-900">Verification</div>
                  </div>
                  <div className="text-sm text-slate-500 font-medium">
                    {caseData.status === 'Verified' || caseData.status === 'Reunification Ready' || caseData.status === 'Reunification In Progress' || caseData.status === 'Reunified' ? 'VERIFIED' : caseData.status === 'In Verification' ? 'IN REVIEW' : 'Not started'}
                  </div>
                  {(caseData.status === 'In Verification' || caseData.status === 'Verified' || caseData.status === 'Reunification Ready' || caseData.status === 'Reunification In Progress' || caseData.status === 'Reunified') && (
                    <button onClick={() => navigate(`/verification/${caseData.vrn_id}`)} className="w-full mt-2 rounded bg-white border border-gray-300 py-1.5 text-xs font-bold text-gray-700 hover:bg-gray-50">
                      {caseData.status === 'In Verification' ? 'REVIEW EVIDENCE' : 'VIEW VERIFICATION'}
                    </button>
                  )}
                </div>
              </div>
              
              <div className={`relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group ${caseData.status === 'Reunified' ? 'is-active' : ''}`}>
                <div className={`flex items-center justify-center w-10 h-10 rounded-full border border-white shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10 ${caseData.status === 'Reunified' ? 'bg-green-100 text-green-600' : 'bg-slate-200 text-slate-500'}`}>
                  <CheckCircle className="h-5 w-5" />
                </div>
                <div className={`w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded border shadow-sm ${caseData.status === 'Reunified' ? 'border-green-200 bg-green-50' : 'border-slate-200 bg-white'}`}>
                  <div className="flex items-center justify-between space-x-2 mb-1">
                    <div className="font-bold text-slate-900">Reunification</div>
                  </div>
                  <div className="text-sm text-slate-500 font-medium">
                    {caseData.status === 'Verified' || caseData.status === 'Reunification Ready' ? 'AUTHORIZATION REQUIRED' : caseData.status === 'Reunified' ? 'REUNITED' : caseData.status === 'Reunification In Progress' ? 'IN PROGRESS' : 'Pending'}
                  </div>
                  {(caseData.status === 'Verified' || caseData.status === 'Reunification Ready' || caseData.status === 'Reunification In Progress' || caseData.status === 'Reunified') && (
                    <button onClick={() => navigate(`/reunification/${caseData.vrn_id}`)} className={`w-full mt-2 rounded py-1.5 text-xs font-bold shadow-sm ${caseData.status === 'Reunified' ? 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50' : 'bg-primary text-white hover:bg-primary/90'}`}>
                      {(caseData.status === 'Verified' || caseData.status === 'Reunification Ready') ? 'PREPARE REUNIFICATION' : caseData.status === 'Reunification In Progress' ? 'CONTINUE REUNIFICATION' : 'VIEW REUNIFICATION'}
                    </button>
                  )}
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  ); 
}
