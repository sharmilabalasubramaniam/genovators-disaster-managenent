import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronRight, Activity, Users, AlertCircle, Clock } from 'lucide-react';
import api from '../services/api';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';

export default function OrganizationDashboard({ orgType }) {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const orgLabels = {
    hospital: { title: "Hospital Dashboard", recordKey: "hospital_records", registerLink: "/hospital/register" },
    shelter: { title: "Shelter Dashboard", recordKey: "shelter_records", registerLink: "/shelter/register" },
    rescue: { title: "Rescue Dashboard", recordKey: "rescue_records", registerLink: "/rescue/register" }
  };
  const labels = orgLabels[orgType];

  useEffect(() => {
    api.get('/cases')
      .then(res => {
        // Filter only cases that have the specific organization's records
        const orgCases = res.data.filter(c => c[labels.recordKey] && c[labels.recordKey].length > 0);
        setCases(orgCases);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [labels.recordKey]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">{labels.title}</h1>
        <button onClick={() => navigate(labels.registerLink)} className="rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white">
          Register Found Person
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-2xl bg-white p-6 shadow-sm border border-gray-100 flex items-center space-x-4">
          <div className="p-3 bg-blue-50 text-blue-600 rounded-full"><Users className="w-6 h-6" /></div>
          <div>
            <p className="text-sm font-medium text-gray-500">Registered</p>
            <p className="text-2xl font-bold text-gray-900">{cases.length}</p>
          </div>
        </div>
        <div className="rounded-2xl bg-white p-6 shadow-sm border border-gray-100 flex items-center space-x-4">
          <div className="p-3 bg-amber-50 text-amber-600 rounded-full"><Activity className="w-6 h-6" /></div>
          <div>
            <p className="text-sm font-medium text-gray-500">Potential Matches</p>
            <p className="text-2xl font-bold text-gray-900">0</p>
          </div>
        </div>
        <div className="rounded-2xl bg-white p-6 shadow-sm border border-gray-100 flex items-center space-x-4">
          <div className="p-3 bg-red-50 text-red-600 rounded-full"><AlertCircle className="w-6 h-6" /></div>
          <div>
            <p className="text-sm font-medium text-gray-500">Pending Review</p>
            <p className="text-2xl font-bold text-gray-900">0</p>
          </div>
        </div>
        <div className="rounded-2xl bg-white p-6 shadow-sm border border-gray-100 flex items-center space-x-4">
          <div className="p-3 bg-green-50 text-green-600 rounded-full"><Clock className="w-6 h-6" /></div>
          <div>
            <p className="text-sm font-medium text-gray-500">Recently Added</p>
            <p className="text-2xl font-bold text-gray-900">{cases.filter(c => new Date(c.created_at) > new Date(Date.now() - 86400000)).length}</p>
          </div>
        </div>
      </div>

      <div className="rounded-2xl bg-white p-6 shadow-sm border border-gray-100">
        <h2 className="text-lg font-bold mb-4">Recent Records</h2>
        {cases.length === 0 ? (
          <div className="py-12 text-center text-gray-500">
            <p>No persons registered yet.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-border text-text-muted">
                  <th className="pb-4 font-medium">Record ID</th>
                  <th className="pb-4 font-medium">Person Info</th>
                  <th className="pb-4 font-medium">Location</th>
                  <th className="pb-4 font-medium">Date Found</th>
                  <th className="pb-4 font-medium">Status</th>
                  <th className="pb-4"></th>
                </tr>
              </thead>
              <tbody>
                {cases.map((c) => {
                  const location = c.location_records?.find(l => l.location_type === 'Found')?.address || 'Unknown';
                  const recordList = c[labels.recordKey];
                  const firstRecord = recordList && recordList.length > 0 ? recordList[0] : {};
                  let foundDate = 'Unknown';
                  if (orgType === 'hospital' && firstRecord.admission_date) {
                    foundDate = new Date(firstRecord.admission_date).toLocaleString();
                  } else if (orgType === 'shelter' && firstRecord.check_in_date) {
                    foundDate = new Date(firstRecord.check_in_date).toLocaleString();
                  } else if (orgType === 'rescue' && firstRecord.rescue_date) {
                    foundDate = new Date(firstRecord.rescue_date).toLocaleString();
                  }
                  
                  return (
                    <tr key={c.id} onClick={() => navigate(`/cases/${c.vrn_id}`)} className="border-b border-border hover:bg-gray-50/50 cursor-pointer">
                      <td className="py-4 font-semibold text-primary">{c.vrn_id}</td>
                      <td className="py-4">
                        <div className="flex flex-col">
                          <span className="font-semibold text-text-main">{c.person.first_name} {c.person.last_name}</span>
                          <span className="text-xs text-text-muted">Age: {c.person.age || '?'}, {c.person.gender || '?'}</span>
                        </div>
                      </td>
                      <td className="py-4 text-gray-700">{location}</td>
                      <td className="py-4 text-gray-700">{foundDate}</td>
                      <td className="py-4">
                        <span className="rounded-full px-3 py-1.5 text-xs font-semibold bg-gray-100 text-gray-800 border border-gray-200 uppercase">{c.status}</span>
                      </td>
                      <td className="py-4 text-right">
                        <ChevronRight className="ml-auto h-4 w-4 text-gray-400" />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
