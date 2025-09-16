import React, { useState, useRef } from 'react';
import { apiService } from '../services/apiService';
import { PDFFileInfo } from '../types';

interface FileUploadProps {
  sessionId: string;
  onFileUploaded: (file: PDFFileInfo) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ sessionId, onFileUploaded }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.includes('pdf')) {
      setError('Please select a PDF file');
      return;
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return;
    }

    await uploadFile(file);
  };

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
    event.stopPropagation();
  };

  const handleDrop = async (event: React.DragEvent) => {
    event.preventDefault();
    event.stopPropagation();

    const files = Array.from(event.dataTransfer.files);
    const pdfFile = files.find((file: File) => file.type.includes('pdf'));

    if (!pdfFile) {
      setError('Please drop a PDF file');
      return;
    }

    // Directly handle the file upload
    await uploadFile(pdfFile);
  };

  const uploadFile = async (file: File) => {
    setIsUploading(true);
    setError(null);

    try {
      const response = await apiService.uploadFile(file, sessionId);
      
      // Convert response to PDFFileInfo format
      const newFile: PDFFileInfo = {
        id: response.file_id,
        name: response.filename,
        original_filename: response.filename,
        file_path: response.upload_path,
        file_size: response.file_size,
        page_count: response.page_count,
        created_at: new Date().toISOString(),
        is_temporary: false
      };

      onFileUploaded(newFile);
      
      // Clear file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err: any) {
      const errorMessage = apiService.handleError(err);
      setError(errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Upload PDF</h3>
      
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isUploading
            ? 'border-blue-500 bg-blue-900/20'
            : 'border-gray-600 hover:border-gray-500 hover:bg-gray-700/50'
        }`}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        {isUploading ? (
          <div className="text-blue-400">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400 mx-auto mb-2"></div>
            <p>Uploading...</p>
          </div>
        ) : (
          <div className="text-gray-400">
            <svg 
              className="mx-auto h-12 w-12 text-gray-500 mb-4" 
              stroke="currentColor" 
              fill="none" 
              viewBox="0 0 48 48"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <p className="text-lg mb-2">Drop a PDF file here</p>
            <p className="text-sm mb-4">or</p>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-medium transition-colors"
            >
              Choose File
            </button>
            <p className="text-xs mt-2 text-gray-500">Maximum file size: 10MB</p>
          </div>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        onChange={handleFileSelect}
        className="hidden"
        disabled={isUploading}
      />

      {error && (
        <div className="mt-4 p-3 bg-red-900 border border-red-600 rounded-lg text-red-100 text-sm">
          {error}
        </div>
      )}
    </div>
  );
};

export default FileUpload;