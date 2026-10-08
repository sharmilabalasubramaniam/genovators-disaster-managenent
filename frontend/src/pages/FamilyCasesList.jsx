import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';
import api from '../services/api';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';

export default function FamilyCasesList() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    api.get('/cases')
      .then(res => {
        // Filter only cases that have family reports
        const familyCases = res.data.filter(c => c.family_reports && c.family_reports.length > 0);
        setCases(familyCases);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  return (
    <div className="rounded-2xl bg-white p-6 shadow-sm">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-lg font-bold">My Submitted Cases</h2>
        <button onClick={() => navigate('/family/report')} className="rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white">
          Report Missing Person
        </button>
      </div>
      
      {cases.length === 0 ? (
        <div className="py-12 text-center text-gray-500">
          <p>No missing person reports submitted yet.</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-border text-text-muted">
                <th className="pb-4 font-medium">VRN ID</th>
                <th className="pb-4 font-medium">Person</th>
                <th className="pb-4 font-medium">Last Known Location</th>
                <th className="pb-4 font-medium">Date Reported</th>
                <th className="pb-4 font-medium">Status</th>
                <th className="pb-4 font-medium">Last Updated</th>
                <th className="pb-4"></th>
              </tr>
            </thead>
            <tbody>
              {cases.map((c) => {
                const location = c.location_records?.find(l => l.location_type === 'Last Known')?.address || 'Unknown';
                const reportDate = c.family_reports[0]?.reported_at ? new Date(c.family_reports[0].reported_at).toLocaleDateString() : 'Unknown';
                
                return (
                  <tr key={c.id} onClick={() => navigate(`/cases/${c.vrn_id}`)} className="border-b border-border hover:bg-gray-50/50 cursor-pointer">
                    <td className="py-4 font-semibold text-primary">{c.vrn_id}</td>
                    <td className="py-4">
                      <div className="flex flex-col">
                        <span className="font-semibold text-text-main">{c.person.first_name} {c.person.last_name}</span>
                        <span className="text-xs text-text-muted">{c.person.gender}, {c.person.age}</span>
                      </div>
                    </td>
                    <td className="py-4 text-gray-700">{location}</td>
                    <td className="py-4 text-gray-700">{reportDate}</td>
                    <td className="py-4">
                      <span className="rounded-full px-3 py-1.5 text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-100">{c.status}</span>
                    </td>
                    <td className="py-4 text-gray-500">
                      {new Date(c.updated_at).toLocaleDateString()}
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
  );
}
