import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import { ArrowLeft, CheckCircle, Clock, MapPin, Phone, User, Check, ShieldCheck, XCircle } from 'lucide-react';
import ReunificationGoogleMap from '../components/GoogleMap';

export default function ReunificationView() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [caseData, setCaseData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [meetingLocation, setMeetingLocation] = useState('');
  const [familyContact, setFamilyContact] = useState('');
  const [officerName, setOfficerName] = useState('');
  const [notes, setNotes] = useState('');
  const [scheduledTime, setScheduledTime] = useState('');

  const fetchCaseAndReunification = () => {
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
  };

  useEffect(() => {
    fetchCaseAndReunification();
  }, [id]);

  const handleStart = async (e) => {
    e.preventDefault();
    if (!meetingLocation || !familyContact || !officerName) {
      alert("Please fill in required fields: Location, Contact, Officer");
      return;
    }
    
    try {
      await api.post(`/reunification/${id}/start`, {
        meeting_location: meetingLocation,
        family_contact: familyContact,
        officer_in_charge: officerName,
        notes: notes,
        scheduled_time: scheduledTime || null
      });
      fetchCaseAndReunification();
    } catch (err) {
      alert("Failed to start reunification: " + (err.response?.data?.detail || err.message));
    }
  };

  const handleComplete = async () => {
    if (!window.confirm("Are you sure you want to mark this case as REUNITED?")) return;
    try {
      await api.post(`/reunification/${id}/complete`, {
        notes: notes || "Reunification completed."
      });
      fetchCaseAndReunification();
    } catch (err) {
      alert("Failed to complete reunification: " + (err.response?.data?.detail || err.message));
    }
  };

  const handleCancel = async () => {
    if (!window.confirm("Are you sure you want to CANCEL this reunification?")) return;
    const cancelReason = window.prompt("Reason for cancellation:");
    if (!cancelReason) return;
    
    try {
      await api.post(`/reunification/${id}/cancel?reason=${encodeURIComponent(cancelReason)}`);
      fetchCaseAndReunification();
    } catch (err) {
      alert("Failed to cancel reunification: " + (err.response?.data?.detail || err.message));
    }
  };

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;
  if (!caseData) return <ErrorState message="Case not found" />;

  const person = caseData.person;
  const reunion = caseData.reunification;
  const rStatus = reunion ? reunion.status : "PENDING";

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <button onClick={() => navigate(-1)} className="p-2 hover:bg-gray-100 rounded-full transition-colors">
          <ArrowLeft className="h-5 w-5 text-gray-600" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
            Reunification: {caseData.vrn_id}
            <span className="text-sm px-3 py-1 bg-green-50 text-green-700 rounded-full font-semibold border border-green-100 uppercase">
              {caseData.status}
            </span>
          </h1>
          <p className="text-sm text-gray-500 mt-1">{person.first_name} {person.last_name}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Column: Forms and Actions */}
        <div className="md:col-span-2 space-y-6">
        {/* Google Maps for Reunification */}
        <div className="h-[400px] w-full rounded-2xl overflow-hidden shadow-sm border border-gray-100 mb-6">
          <ReunificationGoogleMap />
        </div>
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <h2 className="text-lg font-bold border-b pb-3 mb-4 flex items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-primary" /> Reunification Details
            </h2>
            
            {rStatus === 'PENDING' || rStatus === 'REUNIFICATION_READY' ? (
              <form onSubmit={handleStart} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Meeting Location</label>
                    <input 
                      type="text" 
                      value={meetingLocation}
                      onChange={e => setMeetingLocation(e.target.value)}
                      className="w-full rounded-lg border-gray-300 border p-2 focus:ring-primary focus:border-primary"
                      placeholder="e.g., Central Hospital Lobby"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Scheduled Time</label>
                    <input 
                      type="datetime-local" 
                      value={scheduledTime}
                      onChange={e => setScheduledTime(e.target.value)}
                      className="w-full rounded-lg border-gray-300 border p-2 focus:ring-primary focus:border-primary"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Family Contact Phone</label>
                    <input 
                      type="tel" 
                      value={familyContact}
                      onChange={e => setFamilyContact(e.target.value)}
                      className="w-full rounded-lg border-gray-300 border p-2 focus:ring-primary focus:border-primary"
                      placeholder="Phone number"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Officer in Charge</label>
                    <input 
                      type="text" 
                      value={officerName}
                      onChange={e => setOfficerName(e.target.value)}
                      className="w-full rounded-lg border-gray-300 border p-2 focus:ring-primary focus:border-primary"
                      placeholder="Officer name/ID"
                      required
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                  <textarea 
                    value={notes}
                    onChange={e => setNotes(e.target.value)}
                    className="w-full rounded-lg border-gray-300 border p-2 focus:ring-primary focus:border-primary h-24"
                    placeholder="Preparation notes..."
                  />
                </div>
                <div className="flex justify-end pt-2">
                  <button type="submit" className="bg-primary text-white px-6 py-2 rounded-lg font-semibold hover:bg-primary/90 transition-colors">
                    Start Reunification
                  </button>
                </div>
              </form>
            ) : (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-y-4 gap-x-8">
                  <div>
                    <p className="text-sm text-gray-500 font-medium flex items-center gap-1"><MapPin className="h-3 w-3" /> Meeting Location</p>
                    <p className="text-base font-semibold text-gray-900">{reunion.meeting_location || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 font-medium flex items-center gap-1"><Clock className="h-3 w-3" /> Scheduled</p>
                    <p className="text-base text-gray-900">{reunion.scheduled_time ? new Date(reunion.scheduled_time).toLocaleString() : 'Not scheduled'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 font-medium flex items-center gap-1"><Phone className="h-3 w-3" /> Family Contact</p>
                    <p className="text-base text-gray-900">{reunion.family_contact || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 font-medium flex items-center gap-1"><User className="h-3 w-3" /> Officer in Charge</p>
                    <p className="text-base text-gray-900">{reunion.officer_in_charge || 'N/A'}</p>
                  </div>
                  <div className="col-span-2">
                    <p className="text-sm text-gray-500 font-medium">Notes</p>
                    <p className="text-sm text-gray-800 bg-gray-50 p-3 rounded-lg border border-gray-100 whitespace-pre-wrap">{reunion.notes || 'None'}</p>
                  </div>
                </div>

                {rStatus === 'IN_PROGRESS' && (
                  <div className="border-t pt-4 mt-6">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Completion Notes</label>
                    <textarea 
                      value={notes}
                      onChange={e => setNotes(e.target.value)}
                      className="w-full rounded-lg border-gray-300 border p-2 focus:ring-primary focus:border-primary h-20 mb-3"
                      placeholder="Add any final notes before completing..."
                    />
                    <div className="flex justify-between items-center">
                      <button 
                        onClick={handleCancel}
                        className="text-red-600 bg-red-50 hover:bg-red-100 px-4 py-2 rounded-lg font-semibold flex items-center gap-2 transition-colors"
                      >
                        <XCircle className="h-4 w-4" /> Cancel
                      </button>
                      
                      <button 
                        onClick={handleComplete}
                        className="bg-green-600 text-white px-6 py-2 rounded-lg font-bold hover:bg-green-700 flex items-center gap-2 transition-colors shadow-sm"
                      >
                        <CheckCircle className="h-5 w-5" /> COMPLETE REUNIFICATION
                      </button>
                    </div>
                  </div>
                )}
                
                {rStatus === 'REUNITED' && (
                  <div className="bg-green-50 border border-green-200 text-green-800 p-4 rounded-lg flex items-start gap-3 mt-4">
                    <CheckCircle className="h-6 w-6 text-green-600 mt-0.5 shrink-0" />
                    <div>
                      <h4 className="font-bold">Reunification Completed</h4>
                      <p className="text-sm mt-1">This case was successfully completed at {new Date(reunion.completed_time).toLocaleString()}.</p>
                    </div>
                  </div>
                )}

                {rStatus === 'CANCELLED' && (
                  <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded-lg flex items-start gap-3 mt-4">
                    <XCircle className="h-6 w-6 text-red-600 mt-0.5 shrink-0" />
                    <div>
                      <h4 className="font-bold">Reunification Cancelled</h4>
                      <p className="text-sm mt-1">This reunification attempt was cancelled. The case is back to Verified status.</p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Workflow */}
        <div className="space-y-6">
          <div className="bg-gray-50 rounded-2xl p-6 border border-gray-200">
            <h2 className="text-lg font-bold mb-4 text-gray-900">Reunification Status</h2>
            <div className="space-y-4">
              <div className={`p-3 rounded-lg border ${caseData.status === 'Verified' || caseData.status === 'Reunification Ready' ? 'bg-blue-50 border-blue-200' : 'bg-white border-gray-200'}`}>
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${caseData.status === 'Verified' || caseData.status === 'Reunification Ready' ? 'bg-blue-500' : 'bg-green-500'}`}></div>
                  <span className={`font-semibold ${caseData.status === 'Verified' || caseData.status === 'Reunification Ready' ? 'text-blue-900' : 'text-gray-900'}`}>Ready</span>
                </div>
                <p className="text-xs text-gray-500 ml-5 mt-1">Identity verified. Ready for officer preparation.</p>
              </div>

              <div className={`p-3 rounded-lg border ${rStatus === 'IN_PROGRESS' ? 'bg-amber-50 border-amber-200' : 'bg-white border-gray-200'}`}>
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${rStatus === 'IN_PROGRESS' ? 'bg-amber-500' : rStatus === 'REUNITED' ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                  <span className={`font-semibold ${rStatus === 'IN_PROGRESS' ? 'text-amber-900' : 'text-gray-900'}`}>In Progress</span>
                </div>
                <p className="text-xs text-gray-500 ml-5 mt-1">Family and officer coordinated. Active reunification.</p>
              </div>

              <div className={`p-3 rounded-lg border ${rStatus === 'REUNITED' ? 'bg-green-50 border-green-200' : 'bg-white border-gray-200'}`}>
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${rStatus === 'REUNITED' ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                  <span className={`font-semibold ${rStatus === 'REUNITED' ? 'text-green-900' : 'text-gray-900'}`}>Reunited</span>
                </div>
                <p className="text-xs text-gray-500 ml-5 mt-1">Case successfully resolved.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
