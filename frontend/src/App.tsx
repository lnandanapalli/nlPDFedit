import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ChatInterface from './components/ChatInterface';
import FileUpload from './components/FileUpload';
import PDFList from './components/PDFList';
import { useSession } from './hooks/useSession';
import { wsService } from './services/websocketService';
import { PDFFileInfo } from './types';
import './App.css';

const App: React.FC = () => {
  const { sessionId, createNewSession } = useSession();
  const [files, setFiles] = useState<PDFFileInfo[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (sessionId) {
      // Connect to WebSocket
      wsService.connect(sessionId)
        .then(() => {
          setIsConnected(true);
          console.log('Connected to WebSocket');
        })
        .catch((error) => {
          console.error('Failed to connect to WebSocket:', error);
          setIsConnected(false);
        });

      // Setup WebSocket listeners
      wsService.onMessage((message) => {
        console.log('Received WebSocket message:', message);
      });

      wsService.onError((error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      });

      return () => {
        wsService.removeAllListeners();
        wsService.disconnect();
      };
    }
  }, [sessionId]);

  const handleFileUpload = (newFile: PDFFileInfo) => {
    setFiles(prev => [...prev, newFile]);
  };

  const handleFileDelete = (fileId: string) => {
    setFiles(prev => prev.filter(file => file.id !== fileId));
  };

  const handleNewSession = () => {
    createNewSession();
    setFiles([]);
    window.location.reload(); // Simple way to reset the entire app state
  };

  if (!sessionId) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-900 text-white">
        {/* Header */}
        <header className="bg-gray-800 border-b border-gray-700 p-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <h1 className="text-2xl font-bold text-blue-400">
              PDF Chat Assistant
            </h1>
            <div className="flex items-center space-x-4">
              <div className={`flex items-center space-x-2 ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
                <span className="text-sm">{isConnected ? 'Connected' : 'Disconnected'}</span>
              </div>
              <button
                onClick={handleNewSession}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium transition-colors"
              >
                New Session
              </button>
            </div>
          </div>
        </header>

        <Routes>
          <Route path="/" element={
            <div className="max-w-7xl mx-auto p-4">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-120px)]">
                {/* Left Sidebar - File Management */}
                <div className="lg:col-span-1 space-y-4">
                  <FileUpload 
                    sessionId={sessionId} 
                    onFileUploaded={handleFileUpload}
                  />
                  <PDFList 
                    files={files}
                    onFileDeleted={handleFileDelete}
                    sessionId={sessionId}
                  />
                </div>

                {/* Main Chat Area */}
                <div className="lg:col-span-2">
                  <ChatInterface 
                    sessionId={sessionId}
                    files={files}
                    isConnected={isConnected}
                  />
                </div>
              </div>
            </div>
          } />
        </Routes>
      </div>
    </Router>
  );
};

export default App;