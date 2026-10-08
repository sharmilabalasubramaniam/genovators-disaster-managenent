import React from 'react';
import { useLocation } from 'react-router-dom';
export default function PlaceholderPage() {
  const location = useLocation();
  return <div className="p-6 bg-white rounded-2xl capitalize">{location.pathname.replace('/', '')} Placeholder</div>;
}
