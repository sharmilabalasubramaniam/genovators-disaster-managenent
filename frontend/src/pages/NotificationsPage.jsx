import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import { Bell, Check, Trash2, ArrowRight } from 'lucide-react';

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const fetchNotifications = () => {
    setLoading(true);
    api.get('/notifications/')
      .then(res => {
        setNotifications(res.data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.response?.data?.detail || err.message || "Failed to load notifications");
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  const markAsRead = async (id) => {
    try {
      await api.patch(`/notifications/${id}/read`);
      setNotifications(notifications.map(n => n.id === id ? { ...n, status: 'READ' } : n));
    } catch (err) {
      console.error(err);
    }
  };

  const markAllAsRead = async () => {
    try {
      await api.patch('/notifications/read-all/all');
      setNotifications(notifications.map(n => ({ ...n, status: 'READ' })));
    } catch (err) {
      console.error(err);
    }
  };

  if (loading && notifications.length === 0) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  const getPriorityColor = (priority) => {
    switch(priority) {
      case 'HIGH': return 'bg-red-100 text-red-800 border-red-200';
      case 'MEDIUM': return 'bg-amber-100 text-amber-800 border-amber-200';
      default: return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Bell className="h-6 w-6 text-primary" /> Notifications
        </h1>
        {notifications.some(n => n.status === 'UNREAD') && (
          <button 
            onClick={markAllAsRead}
            className="text-sm font-semibold text-primary hover:text-primary-hover flex items-center gap-1"
          >
            <Check className="h-4 w-4" /> Mark all as read
          </button>
        )}
      </div>

      {notifications.length === 0 ? (
        <div className="bg-white rounded-2xl p-12 text-center shadow-sm border border-gray-100">
          <Bell className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-gray-900">No Notifications</h3>
          <p className="text-gray-500 mt-1">You're all caught up!</p>
        </div>
      ) : (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <ul className="divide-y divide-gray-100">
            {notifications.map((notif) => (
              <li key={notif.id} className={`p-4 hover:bg-gray-50 transition-colors ${notif.status === 'UNREAD' ? 'bg-blue-50/30' : ''}`}>
                <div className="flex gap-4">
                  <div className="flex-shrink-0 mt-1">
                    <div className={`w-2 h-2 rounded-full ${notif.status === 'UNREAD' ? 'bg-primary' : 'bg-transparent'}`}></div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`text-xs px-2 py-0.5 rounded-full font-semibold border ${getPriorityColor(notif.priority)}`}>
                            {notif.priority}
                          </span>
                          <span className="text-xs text-gray-500 font-medium bg-gray-100 px-2 py-0.5 rounded border border-gray-200">
                            {notif.notification_type}
                          </span>
                        </div>
                        <h4 className={`text-base font-semibold ${notif.status === 'UNREAD' ? 'text-gray-900' : 'text-gray-700'}`}>
                          {notif.title}
                        </h4>
                        <p className="text-sm text-gray-600 mt-1">{notif.message}</p>
                      </div>
                      <span className="text-xs text-gray-400 whitespace-nowrap">
                        {new Date(notif.created_at).toLocaleString()}
                      </span>
                    </div>
                    
                    <div className="mt-3 flex gap-3">
                      {notif.case_id && (
                        <button 
                          onClick={() => {
                            if (notif.status === 'UNREAD') markAsRead(notif.id);
                            navigate(`/cases/${notif.case_id}`);
                          }}
                          className="text-xs font-semibold text-primary flex items-center hover:underline"
                        >
                          View Case <ArrowRight className="h-3 w-3 ml-1" />
                        </button>
                      )}
                      {notif.status === 'UNREAD' && (
                        <button 
                          onClick={() => markAsRead(notif.id)}
                          className="text-xs font-medium text-gray-500 hover:text-gray-800"
                        >
                          Mark as read
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
