import React from 'react';
import { CheckCircle, Clock, AlertCircle } from 'lucide-react';

export type DocStatus = 'PENDING' | 'UPLOADED' | 'PROCESSING' | 'VALIDATED' | 'FAILED';

export interface DocumentItemProps {
  id: string;
  type: string;
  status: DocStatus;
}

export const DocumentItem: React.FC<DocumentItemProps> = ({ type, status }) => {
  const getStatusIcon = () => {
    switch (status) {
      case 'VALIDATED':
      case 'UPLOADED':
        return <CheckCircle className="text-green-500 h-5 w-5" />;
      case 'PROCESSING':
        return <Clock className="text-yellow-500 h-5 w-5" />;
      case 'FAILED':
        return <AlertCircle className="text-red-500 h-5 w-5" />;
      default:
        return <AlertCircle className="text-gray-400 h-5 w-5" />;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'VALIDATED': return 'Verified';
      case 'UPLOADED': return 'Uploaded';
      case 'PROCESSING': return 'Processing';
      case 'FAILED': return 'Failed Verification';
      default: return 'Required';
    }
  };

  return (
    <div className="flex items-center justify-between p-4 bg-white border border-gray-100 rounded-lg shadow-sm mb-3">
      <div className="flex items-center space-x-3">
        {getStatusIcon()}
        <span className="font-medium text-gray-700">{type}</span>
      </div>
      <span className={`text-sm font-semibold px-2 py-1 rounded-full ${
        status === 'PENDING' ? 'bg-gray-100 text-gray-600' :
        status === 'FAILED' ? 'bg-red-50 text-red-600' :
        status === 'PROCESSING' ? 'bg-yellow-50 text-yellow-600' :
        'bg-green-50 text-green-600'
      }`}>
        {getStatusText()}
      </span>
    </div>
  );
};
