import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

const apiService = {
    uploadFile: async (file: File, sessionId: string) => {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("session_id", sessionId);

        const response = await axios.post(`${API_BASE_URL}/api/v1/files/upload`, formData, {
            headers: { "Content-Type": "multipart/form-data" }
        });
        return response.data;
    },

    getFiles: async (sessionId: string) => {
        const response = await axios.get(`${API_BASE_URL}/api/v1/files/list/${sessionId}`);
        return response.data;
    },

    sendMessage: async (request: any) => {
        const response = await axios.post(`${API_BASE_URL}/api/v1/chat/message`, request);
        return response.data;
    },

    getChatHistory: async (sessionId: string) => {
        const response = await axios.get(`${API_BASE_URL}/api/v1/chat/history/${sessionId}`);
        return response.data;
    },

    clearChatHistory: async (sessionId: string) => {
        const response = await axios.delete(`${API_BASE_URL}/api/v1/chat/history/${sessionId}`);
        return response.data;
    },

    downloadFile: async (fileId: string) => {
        const response = await axios.get(`${API_BASE_URL}/api/v1/files/download/${fileId}`, {
            responseType: 'blob'
        });
        return response.data;
    },

    deleteFile: async (fileId: string, sessionId: string) => {
        const response = await axios.delete(`${API_BASE_URL}/api/v1/files/${fileId}?session_id=${sessionId}`);
        return response.data;
    },

    downloadBlob: (blob: Blob, filename: string) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    },

    handleError: (error: any): string => {
        if (error.response?.data?.detail) {
            // Handle FastAPI validation errors (array of error objects)
            if (Array.isArray(error.response.data.detail)) {
                return error.response.data.detail
                    .map((err: any) => err.msg || 'Validation error')
                    .join(', ');
            }
            // Handle single error message
            return error.response.data.detail;
        }
        if (error.response?.data?.message) {
            return error.response.data.message;
        }
        if (error.message) {
            return error.message;
        }
        return "An unexpected error occurred";
    }
};

export default apiService;
