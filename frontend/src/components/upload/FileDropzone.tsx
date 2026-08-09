import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, File as FileIcon, X } from 'lucide-react';

interface FileDropzoneProps {
  onFilesAccepted: (files: File[]) => void;
}

export const FileDropzone: React.FC<FileDropzoneProps> = ({ onFilesAccepted }) => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setSelectedFiles(prev => [...prev, ...acceptedFiles]);
    onFilesAccepted([...selectedFiles, ...acceptedFiles]);
  }, [selectedFiles, onFilesAccepted]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  const removeFile = (e: React.MouseEvent, index: number) => {
    e.stopPropagation();
    const newFiles = [...selectedFiles];
    newFiles.splice(index, 1);
    setSelectedFiles(newFiles);
    onFilesAccepted(newFiles);
  };

  return (
    <div className="mt-6">
      <div 
        {...getRootProps()} 
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors duration-200 ${
          isDragActive ? 'border-fhn-navy bg-blue-50' : 'border-gray-300 hover:border-fhn-navy hover:bg-gray-50'
        }`}
      >
        <input {...getInputProps()} />
        <UploadCloud className={`mx-auto h-12 w-12 ${isDragActive ? 'text-fhn-navy' : 'text-gray-400'}`} />
        <p className="mt-4 text-sm font-medium text-gray-700">
          {isDragActive ? "Drop the files here..." : "Drag & drop files here, or click to select files"}
        </p>
        <p className="mt-2 text-xs text-gray-500">
          Supported formats: PDF, JPG, PNG (Max size: 10MB)
        </p>
      </div>

      {selectedFiles.length > 0 && (
        <div className="mt-6">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">Selected Files</h4>
          <ul className="space-y-2">
            {selectedFiles.map((file, idx) => (
              <li key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-100">
                <div className="flex items-center space-x-3">
                  <FileIcon className="h-5 w-5 text-fhn-navy" />
                  <span className="text-sm font-medium text-gray-700 truncate max-w-xs">{file.name}</span>
                </div>
                <button 
                  type="button"
                  onClick={(e) => removeFile(e, idx)}
                  className="p-1 hover:bg-gray-200 rounded-full transition-colors"
                >
                  <X className="h-4 w-4 text-gray-500" />
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
