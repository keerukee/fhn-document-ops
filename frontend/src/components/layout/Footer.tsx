import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-gray-200 mt-12">
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 flex flex-col items-center">
        <p className="text-sm text-gray-500">
          &copy; {new Date().getFullYear()} First Horizon Bank. All rights reserved.
        </p>
        <p className="text-xs text-gray-400 mt-2">
          Secure and encrypted document transmission.
        </p>
      </div>
    </footer>
  );
};
