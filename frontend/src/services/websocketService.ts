import { WebSocketMessage } from '../types';

class WebSocketService {
    private socket: WebSocket | null = null;
    private isConnected: boolean = false;
    private reconnectAttempts: number = 0;
    private maxReconnectAttempts: number = 5;
    private baseURL: string;
    private sessionId: string | null = null;
    private messageHandlers: Map<string, (data: any) => void> = new Map();

    constructor() {
        this.baseURL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
    }

    connect(sessionId: string): Promise<void> {
        return new Promise((resolve, reject) => {
            try {
                this.sessionId = sessionId;
                const wsUrl = `${this.baseURL}/ws/${sessionId}`;
                this.socket = new WebSocket(wsUrl);

                this.socket.onopen = () => {
                    console.log('WebSocket connected');
                    this.isConnected = true;
                    this.reconnectAttempts = 0;
                    resolve();
                };

                this.socket.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    this.isConnected = false;

                    // Trigger error handler
                    if (this.messageHandlers.has('error')) {
                        const handler = this.messageHandlers.get('error');
                        if (handler) {
                            handler(error);
                        }
                    }

                    reject(error);
                };

                this.socket.onclose = () => {
                    console.log('WebSocket disconnected');
                    this.isConnected = false;
                    this.handleReconnect();
                };

                this.socket.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        this.handleMessage(data);
                    } catch (error) {
                        console.error('Error parsing WebSocket message:', error);
                    }
                };
            } catch (error) {
                console.error('Error creating WebSocket connection:', error);
                reject(error);
            }
        });
    }

    disconnect(): void {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
            this.isConnected = false;
        }
    }

    private handleReconnect(): void {
        if (this.reconnectAttempts < this.maxReconnectAttempts && this.sessionId) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

            setTimeout(() => {
                this.connect(this.sessionId!);
            }, Math.pow(2, this.reconnectAttempts) * 1000); // Exponential backoff
        } else {
            console.error('Max reconnection attempts reached');
        }
    }

    sendMessage(message: WebSocketMessage): void {
        if (this.socket && this.isConnected) {
            this.socket.send(JSON.stringify(message));
        } else {
            console.error('WebSocket is not connected');
        }
    }

    private handleMessage(data: any): void {
        console.log('Received WebSocket message:', data);

        // Handle general message listener first
        if (this.messageHandlers.has('general')) {
            const handler = this.messageHandlers.get('general');
            if (handler) {
                handler(data);
            }
        }

        // Handle specific message types
        if (data.type && this.messageHandlers.has(data.type)) {
            const handler = this.messageHandlers.get(data.type);
            if (handler) {
                handler(data);
            }
        }
    } onMessage(type: string, handler: (data: any) => void): void;
    onMessage(handler: (data: any) => void): void;
    onMessage(typeOrHandler: string | ((data: any) => void), handler?: (data: any) => void): void {
        if (typeof typeOrHandler === 'string' && handler) {
            this.messageHandlers.set(typeOrHandler, handler);
        } else if (typeof typeOrHandler === 'function') {
            // Handle general message listener
            this.messageHandlers.set('general', typeOrHandler);
        }
    }

    onError(handler: (error: any) => void): void {
        this.messageHandlers.set('error', handler);
    }

    onChatMessage(callback: (message: any) => void): void {
        this.onMessage('chat_message', callback);
    }

    removeMessageHandler(type: string): void {
        this.messageHandlers.delete(type);
    }

    removeAllListeners(): void {
        this.messageHandlers.clear();
    }

    isSocketConnected(): boolean {
        return this.isConnected;
    }
}

const wsService = new WebSocketService();
export { wsService };
export default wsService;