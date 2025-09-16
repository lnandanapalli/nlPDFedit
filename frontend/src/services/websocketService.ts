class WebSocketService {
    private ws: WebSocket | null = null;
    private messageHandlers: ((message: any) => void)[] = [];
    private errorHandlers: ((error: any) => void)[] = [];

    async connect(sessionId: string): Promise<void> {
        return new Promise((resolve, reject) => {
            try {
                this.ws = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);
                
                this.ws.onopen = () => {
                    console.log("WebSocket connected");
                    resolve();
                };

                this.ws.onmessage = (event) => {
                    try {
                        const message = JSON.parse(event.data);
                        this.messageHandlers.forEach(handler => handler(message));
                    } catch (error) {
                        console.error("Error parsing WebSocket message:", error);
                    }
                };

                this.ws.onerror = (error) => {
                    console.error("WebSocket error:", error);
                    this.errorHandlers.forEach(handler => handler(error));
                    reject(error);
                };

                this.ws.onclose = () => {
                    console.log("WebSocket disconnected");
                    this.ws = null;
                };
            } catch (error) {
                reject(error);
            }
        });
    }

    onMessage(handler: (message: any) => void): void {
        this.messageHandlers.push(handler);
    }

    onError(handler: (error: any) => void): void {
        this.errorHandlers.push(handler);
    }

    removeAllListeners(): void {
        this.messageHandlers = [];
        this.errorHandlers = [];
    }

    sendMessage(message: any): void {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        } else {
            console.error("WebSocket is not connected");
        }
    }

    disconnect(): void {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.removeAllListeners();
    }
}

const wsService = new WebSocketService();
export default wsService;
