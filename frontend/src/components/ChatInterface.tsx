import React, { useState, useEffect, useRef } from 'react';
import { useChat } from '../hooks/useChat';
import { PDFFileInfo, ChatMessage } from '../types';

interface ChatInterfaceProps {
  sessionId: string;
  files: PDFFileInfo[];
  isConnected: boolean;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ sessionId, files, isConnected }) => {
  const { messages, isLoading, error, sendMessage, retryLastMessage, clearHistory, loadChatHistory } = useChat(sessionId);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadChatHistory();
  }, [loadChatHistory]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    await sendMessage(inputValue);
    setInputValue('');
  };

  const handleRetry = async () => {
    await retryLastMessage();
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const renderMessage = (message: ChatMessage) => {
    const isUser = message.message_type === 'user';
    const isError = message.message_type === 'error';
    
    return (
      <div key={message.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
        <div className={`max-w-3xl rounded-lg p-4 ${
          isUser 
            ? 'bg-blue-600 text-white' 
            : isError 
            ? 'bg-red-900 border border-red-600 text-red-100'
            : 'bg-gray-700 text-gray-100'
        }`}>
          <div className="whitespace-pre-wrap">{message.content}</div>
          
          {message.operation_result?.show_retry && (
            <div className="mt-3 pt-3 border-t border-gray-600">
              <button
                onClick={handleRetry}
                className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm font-medium transition-colors"
                disabled={isLoading}
              >
                {isLoading ? 'Retrying...' : 'Retry'}
              </button>
            </div>
          )}
          
          <div className={`text-xs mt-2 ${isUser ? 'text-blue-200' : 'text-gray-400'}`}>
            {formatTimestamp(message.timestamp)}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full bg-gray-800 rounded-lg">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <h2 className="text-lg font-semibold text-white">Chat Assistant</h2>
        <div className="flex items-center space-x-2">
          <div className={`text-sm ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
            {isConnected ? 'Online' : 'Offline'}
          </div>
          <button
            onClick={clearHistory}
            className="px-3 py-1 bg-gray-600 hover:bg-gray-500 rounded text-sm transition-colors"
          >
            Clear Chat
          </button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-400 mt-8">
            <p className="text-lg mb-2">Welcome to PDF Chat Assistant!</p>
            <p className="text-sm">
              Upload PDF files and start chatting to perform operations like:
            </p>
            <ul className="text-sm mt-2 space-y-1">
              <li>• Extract text from pages</li>
              <li>• Merge multiple PDFs</li>
              <li>• Split PDFs into separate files</li>
              <li>• Rotate pages</li>
              <li>• Add watermarks</li>
              <li>• Compress files</li>
            </ul>
            {files.length > 0 && (
              <p className="text-blue-400 mt-4">
                You have {files.length} PDF file{files.length > 1 ? 's' : ''} uploaded. 
                Try asking something like "Extract text from the first 3 pages"
              </p>
            )}
          </div>
        ) : (
          messages.map(renderMessage)
        )}
        
        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-700 rounded-lg p-4 max-w-3xl">
              <div className="flex items-center space-x-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
                <span className="text-gray-300 text-sm">Assistant is thinking...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-gray-700">
        {error && (
          <div className="mb-3 p-3 bg-red-900 border border-red-600 rounded-lg text-red-100 text-sm">
            {typeof error === 'string' ? error : 'An error occurred'}
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={
              files.length === 0 
                ? "Upload a PDF file first, then ask me anything..." 
                : "Ask me anything about your PDFs..."
            }
            className="flex-1 px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={isLoading || !isConnected}
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim() || !isConnected}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg text-white font-medium transition-colors"
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;