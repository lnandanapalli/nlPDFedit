import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
    ChatMessage,
    ChatMessageRequest,
    PDFFileInfo,
    PDFOperationRequest,
    FileUploadResponse,
    SessionState
} from '../types';

class APIService {
    private api: AxiosInstance;
    private baseURL: string;

    constructor() {
        this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
        this.api = axios.create({
            baseURL: this.baseURL,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json',
            },
        });

        // Add response interceptor for error handling
        this.api.interceptors.response.use(
            (response: AxiosResponse) => response,
            (error: any) => {
                console.error('API Error:', error.response?.data || error.message);
                return Promise.reject(error);
            }
        );
    }

    // Health check
    async health(): Promise<{ status: string }> {
        const response = await this.api.get('/health');
        return response.data;
    }

    // Chat endpoints
    async sendMessage(request: ChatMessageRequest): Promise<ChatMessage> {
        const response = await this.api.post('/api/chat/send', request);
        return response.data;
    }

    async getChatHistory(sessionId: string): Promise<ChatMessage[]> {
        const response = await this.api.get(`/api/chat/history/${sessionId}`);
        return response.data;
    }

    async clearChatHistory(sessionId: string): Promise<{ message: string }> {
        const response = await this.api.delete(`/api/chat/history/${sessionId}`);
        return response.data;
    }

    // File management endpoints
    async uploadFile(file: File, sessionId: string): Promise<FileUploadResponse> {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('session_id', sessionId);

        const response = await this.api.post('/api/files/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    }

    async getFiles(sessionId: string): Promise<PDFFileInfo[]> {
        const response = await this.api.get(`/api/files/${sessionId}`);
        return response.data;
    }

    async deleteFile(fileId: string): Promise<{ message: string }> {
        const response = await this.api.delete(`/api/files/${fileId}`);
        return response.data;
    }

    async downloadFile(fileId: string): Promise<Blob> {
        const response = await this.api.get(`/api/files/download/${fileId}`, {
            responseType: 'blob',
        });
        return response.data;
    }

    // PDF operations endpoint
    async performPDFOperation(request: PDFOperationRequest): Promise<PDFFileInfo> {
        const response = await this.api.post('/api/pdf/operation', request);
        return response.data;
    }

    // Session management
    async getSession(sessionId: string): Promise<SessionState> {
        const response = await this.api.get(`/api/session/${sessionId}`);
        return response.data;
    }

    async createSession(): Promise<{ session_id: string }> {
        const response = await this.api.post('/api/session/create');
        return response.data;
    }

    // Utility method to handle file downloads
    downloadBlob(blob: Blob, filename: string): void {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    }

    // Error handling helper
    handleError(error: any): string {
        if (error.response?.data?.error) {
            return error.response.data.error;
        } else if (error.message) {
            return error.message;
        }
        return 'An unexpected error occurred';
    }
}

export const apiService = new APIService();
export default APIService;