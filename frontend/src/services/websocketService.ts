import { io, Socket } from 'socket.io-client';
import { WebSocketMessage } from '../types';

class WebSocketService {
    private socket: Socket | null = null;
    private isConnected: boolean = false;
    private reconnectAttempts: number = 0;
    private maxReconnectAttempts: number = 5;
    private baseURL: string;

    constructor() {
        this.baseURL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
    }

    connect(sessionId: string): Promise<void> {
        return new Promise((resolve, reject) => {
            try {
                this.socket = io(this.baseURL, {
                    transports: ['websocket'],
                    query: {
                        session_id: sessionId
                    }
                });

                this.socket.on('connect', () => {
                    console.log('WebSocket connected');
                    this.isConnected = true;
                    this.reconnectAttempts = 0;
                    resolve();
                });

                this.socket.on('disconnect', () => {
                    console.log('WebSocket disconnected');
                    this.isConnected = false;
                    this.handleReconnect(sessionId);
                });

                this.socket.on('connect_error', (error: any) => {
                    console.error('WebSocket connection error:', error);
                    this.isConnected = false;
                    if (this.reconnectAttempts === 0) {
                        reject(error);
                    }
                });
            } catch (error) {
                console.error('Failed to create WebSocket connection:', error);
                reject(error);
            }
        });
    }

    disconnect(): void {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
            this.isConnected = false;
        }
    }

    private handleReconnect(sessionId: string): void {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

            setTimeout(() => {
                this.connect(sessionId).catch((error) => {
                    console.error('Reconnection failed:', error);
                });
            }, 1000 * this.reconnectAttempts); // Exponential backoff
        } else {
            console.error('Max reconnection attempts reached');
        }
    }

    sendMessage(message: WebSocketMessage): void {
        if (this.socket && this.isConnected) {
            this.socket.emit('message', message);
        } else {
            console.warn('WebSocket is not connected');
        }
    }

    onMessage(callback: (message: WebSocketMessage) => void): void {
        if (this.socket) {
            this.socket.on('message', callback);
        }
    }

    onChatMessage(callback: (message: any) => void): void {
        if (this.socket) {
            this.socket.on('chat_message', callback);
        }
    }

    onOperationUpdate(callback: (update: any) => void): void {
        if (this.socket) {
            this.socket.on('operation_update', callback);
        }
    }

    onError(callback: (error: any) => void): void {
        if (this.socket) {
            this.socket.on('error', callback);
        }
    }

    removeAllListeners(): void {
        if (this.socket) {
            this.socket.removeAllListeners();
        }
    }

    getConnectionStatus(): boolean {
        return this.isConnected;
    }
}

export const wsService = new WebSocketService();
export default WebSocketService;