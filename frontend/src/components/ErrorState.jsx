import React from 'react';
import { AlertTriangle } from 'lucide-react';

export default function ErrorState({ message }) {
  return (
    <div className="flex h-full min-h-[400px] flex-col items-center justify-center gap-4 text-center">
      <div className="rounded-full bg-red-100 p-3 text-red-600">
        <AlertTriangle className="h-8 w-8" />
      </div>
      <div>
        <h3 className="text-lg font-semibold">Something went wrong</h3>
        <p className="text-sm text-gray-500">{message || 'An unexpected error occurred.'}</p>
      </div>
    </div>
  );
}
