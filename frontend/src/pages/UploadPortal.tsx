import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

import { Header } from '../components/layout/Header';
import { Footer } from '../components/layout/Footer';
import { DocumentItem } from '../components/upload/DocumentItem';
import type { DocStatus } from '../components/upload/DocumentItem';
import { FileDropzone } from '../components/upload/FileDropzone';
import { CheckCircle, ShieldCheck } from 'lucide-react';

interface ExpectedDocument {
  id: string;
  document_type: string;
  status: DocStatus;
  is_extra?: boolean;
}

interface UploadRequestResponse {
  id: string;
  customer_name: string;
  status: string;
  expires_at: string;
  expected_documents: ExpectedDocument[];
}

export const UploadPortal: React.FC = () => {
  const { referenceId } = useParams<{ referenceId: string }>();
  const [requestData, setRequestData] = useState<UploadRequestResponse | null>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  // Mocking the data fetch for demonstration since backend isn't running yet
  useEffect(() => {
    // In a real app:
    // axios.get(`/api/v1/public/requests/${referenceId}`)
    //   .then(res => setRequestData(res.data));
    
    // Mock Data
    setTimeout(() => {
      setRequestData({
        id: referenceId || 'unknown',
        customer_name: 'John Doe',
        status: 'PENDING',
        expires_at: new Date(Date.now() + 7*24*60*60*1000).toISOString(),
        expected_documents: [
          { id: '1', document_type: 'W-2 Form (2025)', status: 'PENDING' },
          { id: '2', document_type: 'Driver License', status: 'PENDING' }
        ]
      });
    }, 500);
  }, [referenceId]);

  const handleUpload = async () => {
    if (files.length === 0) return;
    setIsUploading(true);
    
    // In a real app: Create FormData, append files and mapping metadata, POST to backend.
    /*
    const formData = new FormData();
    files.forEach(f => formData.append('files', f));
    formData.append('document_ids', '1,2'); 
    await axios.post(`/api/v1/public/requests/${referenceId}/upload`, formData);
    */
    
    setTimeout(() => {
      setIsUploading(false);
      
      if (requestData) {
        // Mark N pending documents as UPLOADED based on number of files
        let filesProcessed = 0;
        const updatedDocs = requestData.expected_documents.map(d => {
          if (!d.is_extra && d.status === 'PENDING' && filesProcessed < files.length) {
            filesProcessed++;
            return { ...d, status: 'UPLOADED' as DocStatus };
          }
          return d;
        });

        // Add remaining files as extras (up to 3 total)
        let currentExtras = updatedDocs.filter(d => d.is_extra).length;
        while (filesProcessed < files.length && currentExtras < 3) {
          updatedDocs.push({
            id: `extra-${Date.now()}-${filesProcessed}`,
            document_type: files[filesProcessed].name || "Supplemental Document",
            status: 'UPLOADED',
            is_extra: true
          });
          filesProcessed++;
          currentExtras++;
        }
        
        setRequestData({
          ...requestData,
          expected_documents: updatedDocs
        });
        
        setFiles([]);
        if (filesProcessed < files.length) {
          alert(`Successfully uploaded ${filesProcessed} document(s). Maximum of 3 extra documents allowed.`);
        } else {
          alert(`Successfully uploaded ${filesProcessed} document(s).`);
        }
      }
    }, 1500);
  };

  const handleFinish = async () => {
    // In a real app: await axios.post(`/api/v1/public/requests/${referenceId}/finish`);
    setUploadSuccess(true);
  };

  if (!requestData) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-fhn-gray">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-fhn-navy"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-fhn-gray">
      <Header />
      
      <main className="flex-grow max-w-4xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          {/* Top Banner */}
          <div className="bg-fhn-navy px-8 py-6 text-white flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold">Secure Document Upload</h1>
              <p className="text-blue-200 mt-1">Prepared for {requestData.customer_name}</p>
            </div>
            <ShieldCheck className="h-12 w-12 text-fhn-red opacity-80" />
          </div>
          
          <div className="p-8">
            {uploadSuccess ? (
              <div className="text-center py-12">
                <CheckCircle className="mx-auto h-20 w-20 text-green-500 mb-6" />
                <h2 className="text-2xl font-bold text-gray-800">Upload Successful</h2>
                <p className="text-gray-600 mt-2">Your documents have been securely transmitted to First Horizon.</p>
                <p className="text-sm text-gray-500 mt-6">You may now close this window.</p>
              </div>
            ) : (
              <>
                <div className="mb-8">
                  <h3 className="text-lg font-bold text-fhn-dark mb-4 border-b pb-2">Required Documents</h3>
                  <div className="space-y-3">
                    {requestData.expected_documents.filter(d => !d.is_extra).map(doc => (
                      <DocumentItem key={doc.id} id={doc.id} type={doc.document_type} status={doc.status} />
                    ))}
                  </div>
                </div>

                <div className="mb-8">
                  <h3 className="text-lg font-bold text-fhn-dark mb-4 border-b pb-2">Supplemental Documents (Optional)</h3>
                  <div className="space-y-3 mb-4">
                    {requestData.expected_documents.filter(d => d.is_extra).map(doc => (
                      <DocumentItem key={doc.id} id={doc.id} type={doc.document_type} status={doc.status} />
                    ))}
                    {requestData.expected_documents.filter(d => d.is_extra).length === 0 && (
                      <p className="text-sm text-gray-500 italic">No extra documents uploaded.</p>
                    )}
                  </div>
                </div>

                <div className="mb-8">
                  <div className="flex justify-between items-end mb-4 border-b pb-2">
                    <h3 className="text-lg font-bold text-fhn-dark">Upload Files</h3>
                    <span className="text-sm font-medium text-fhn-red">
                      {requestData.expected_documents.filter(d => !d.is_extra && d.status === 'PENDING').length} required remaining
                    </span>
                  </div>
                  <FileDropzone onFilesAccepted={setFiles} />
                </div>

                <div className="flex justify-between pt-4 border-t">
                  <div>
                    {requestData.expected_documents.filter(d => !d.is_extra).every(d => d.status !== 'PENDING') && (
                      <button 
                        onClick={handleFinish}
                        className="px-6 py-3 rounded-md font-semibold text-fhn-navy border border-fhn-navy hover:bg-gray-100 transition-colors shadow-sm"
                      >
                        Finish & Lock Request
                      </button>
                    )}
                  </div>
                  <button 
                    onClick={handleUpload}
                    disabled={files.length === 0 || isUploading}
                    className={`px-6 py-3 rounded-md font-semibold text-white transition-colors flex items-center space-x-2 ${
                      files.length === 0 || isUploading 
                      ? 'bg-gray-400 cursor-not-allowed' 
                      : 'bg-fhn-red hover:bg-red-700 shadow-md hover:shadow-lg'
                    }`}
                  >
                    {isUploading ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        <span>Uploading...</span>
                      </>
                    ) : (
                      <span>Submit Documents</span>
                    )}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};
