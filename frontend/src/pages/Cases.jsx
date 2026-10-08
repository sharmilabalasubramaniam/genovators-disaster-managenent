import React, { useEffect, useState } from 'react';
import { ChevronRight } from 'lucide-react';
import api from '../services/api';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';

export default function Cases() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.get('/cases')
      .then(res => {
        setCases(res.data);
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
        <h2 className="text-lg font-bold">All Cases</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-border text-text-muted">
              <th className="pb-4 font-medium">ID</th>
              <th className="pb-4 font-medium">Person</th>
              <th className="pb-4 font-medium">Status</th>
              <th className="pb-4 font-medium">Last Update</th>
              <th className="pb-4"></th>
            </tr>
          </thead>
          <tbody>
            {cases.map((c) => (
              <tr key={c.id} className="border-b border-border hover:bg-gray-50/50">
                <td className="py-4 font-semibold text-primary">{c.vrn_id}</td>
                <td className="py-4">
                  <div className="flex flex-col">
                    <span className="font-semibold text-text-main">{c.person.first_name} {c.person.last_name}</span>
                    <span className="text-xs text-text-muted">{c.person.gender}, {c.person.age}</span>
                  </div>
                </td>
                <td className="py-4">
                  <span className="rounded-full px-3 py-1.5 text-xs font-semibold bg-gray-100">{c.status}</span>
                </td>
                <td className="py-4 text-text-main">
                  {new Date(c.updated_at).toLocaleDateString()}
                </td>
                <td className="py-4 text-right">
                  <ChevronRight className="ml-auto h-4 w-4 cursor-pointer text-text-muted" />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
