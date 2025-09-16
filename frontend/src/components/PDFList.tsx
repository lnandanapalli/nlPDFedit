import React, { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/apiService';
import { PDFFileInfo } from '../types';

interface PDFListProps {
  files: PDFFileInfo[];
  onFileDeleted: (fileId: string) => void;
  sessionId: string;
}

const PDFList: React.FC<PDFListProps> = ({ files, onFileDeleted, sessionId }) => {
  const [loadingFiles, setLoadingFiles] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);

  const loadFiles = useCallback(async () => {
    try {
      const sessionFiles = await apiService.getFiles(sessionId);
      // Update parent component with files from session
      sessionFiles.forEach(file => {
        if (!files.find(f => f.id === file.id)) {
          // File exists in session but not in local state - this shouldn't normally happen
          // but we'll handle it gracefully
        }
      });
    } catch (err) {
      console.error('Failed to load files:', err);
      setError('Failed to load files');
    }
  }, [sessionId, files]);

  useEffect(() => {
    if (sessionId) {
      loadFiles();
    }
  }, [sessionId, loadFiles]);

  const handleDownload = async (file: PDFFileInfo) => {
    setLoadingFiles(prev => new Set([...prev, file.id]));
    setError(null);

    try {
      const blob = await apiService.downloadFile(file.id);
      apiService.downloadBlob(blob, file.original_filename);
    } catch (err: any) {
      const errorMessage = apiService.handleError(err);
      setError(errorMessage);
    } finally {
      setLoadingFiles(prev => {
        const newSet = new Set(prev);
        newSet.delete(file.id);
        return newSet;
      });
    }
  };

  const handleDelete = async (file: PDFFileInfo) => {
    if (!window.confirm(`Are you sure you want to delete "${file.original_filename}"?`)) {
      return;
    }

    setLoadingFiles(prev => new Set([...prev, file.id]));
    setError(null);

    try {
      await apiService.deleteFile(file.id);
      onFileDeleted(file.id);
    } catch (err: any) {
      const errorMessage = apiService.handleError(err);
      setError(errorMessage);
    } finally {
      setLoadingFiles(prev => {
        const newSet = new Set(prev);
        newSet.delete(file.id);
        return newSet;
      });
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString([], {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">PDF Files</h3>
        <span className="text-sm text-gray-400">
          {files.length} file{files.length !== 1 ? 's' : ''}
        </span>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-900 border border-red-600 rounded-lg text-red-100 text-sm">
          {error}
        </div>
      )}

      {files.length === 0 ? (
        <div className="text-center text-gray-400 py-8">
          <svg 
            className="mx-auto h-12 w-12 text-gray-500 mb-4" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
            />
          </svg>
          <p className="text-lg mb-2">No PDF files uploaded</p>
          <p className="text-sm">Upload a PDF file to get started</p>
        </div>
      ) : (
        <div className="space-y-3">
          {files.map((file) => (
            <div key={file.id} className="bg-gray-700 rounded-lg p-4 border border-gray-600">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <h4 className="text-white font-medium truncate" title={file.original_filename}>
                    {file.original_filename}
                  </h4>
                  <div className="flex items-center space-x-4 mt-1 text-sm text-gray-400">
                    <span>{formatFileSize(file.file_size)}</span>
                    <span>•</span>
                    <span>{file.page_count} page{file.page_count !== 1 ? 's' : ''}</span>
                    <span>•</span>
                    <span>{formatDate(file.created_at)}</span>
                  </div>
                </div>

                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={() => handleDownload(file)}
                    disabled={loadingFiles.has(file.id)}
                    className="p-2 text-gray-400 hover:text-blue-400 hover:bg-gray-600 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Download"
                  >
                    {loadingFiles.has(file.id) ? (
                      <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
                    ) : (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    )}
                  </button>

                  <button
                    onClick={() => handleDelete(file)}
                    disabled={loadingFiles.has(file.id)}
                    className="p-2 text-gray-400 hover:text-red-400 hover:bg-gray-600 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Delete"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PDFList;