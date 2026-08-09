import React from 'react';
import { Building2 } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="bg-fhn-navy text-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-2">
            <Building2 className="h-8 w-8 text-fhn-red" />
            <span className="font-bold text-xl tracking-wide">FIRST HORIZON</span>
          </div>
          <nav>
            <span className="text-sm font-medium text-gray-200">Secure Document Portal</span>
          </nav>
        </div>
      </div>
    </header>
  );
};
