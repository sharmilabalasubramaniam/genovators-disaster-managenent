import React from 'react';
import { FileQuestion } from 'lucide-react';

export default function EmptyState({ title, description }) {
  return (
    <div className="flex h-full min-h-[400px] flex-col items-center justify-center gap-4 text-center">
      <div className="rounded-full bg-gray-100 p-3 text-gray-400">
        <FileQuestion className="h-8 w-8" />
      </div>
      <div>
        <h3 className="text-lg font-semibold">{title || 'No results found'}</h3>
        <p className="text-sm text-gray-500">{description || 'Try adjusting your search or filters.'}</p>
      </div>
    </div>
  );
}
