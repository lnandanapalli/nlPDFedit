export interface PDFFileInfo {
    id: string;
    name: string;
    original_filename: string;
    file_path: string;
    file_size: number;
    page_count: number;
    created_at: string;
    parent_id?: string;
    is_temporary: boolean;
}

export interface ChatMessage {
    id: string;
    content: string;
    message_type: 'user' | 'assistant' | 'system' | 'error';
    timestamp: string;
    session_id: string;
    operation_result?: {
        operation?: string;
        parameters?: any;
        status?: string;
        error?: string;
        show_retry?: boolean;
        show_download_button?: boolean;
        download_ready?: boolean;
        result_file?: {
            id: string;
            name: string;
            path: string;
            download_url: string;
            file_size?: number;
            page_count?: number;
            file_type?: string;
        };
    };
}

export interface SessionState {
    session_id: string;
    current_pdf_id?: string;
    pdf_files: PDFFileInfo[];
    chat_history: ChatMessage[];
    created_at: string;
}

export interface FileUploadResponse {
    file_id: string;
    filename: string;
    file_size: number;
    page_count: number;
    upload_path: string;
}

export interface ChatMessageRequest {
    content: string;
    session_id?: string;
}

export interface PDFOperationRequest {
    operation_type: string;
    input_pdf_ids: string[];
    parameters: Record<string, any>;
    session_id: string;
}

export interface APIError {
    error: string;
    detail?: string;
    error_code?: string;
}

export interface WebSocketMessage {
    type: 'connection' | 'chat_message' | 'operation_update' | 'error';
    data?: any;
    message?: string;
    client_id?: string;
}