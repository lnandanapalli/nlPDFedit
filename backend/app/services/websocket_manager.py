from typing import Dict, List
from fastapi import WebSocket
import json
import asyncio


class WebSocketManager:
    def __init__(self):
        # Store active connections
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        await self.send_personal_message(
            json.dumps({
                "type": "connection",
                "message": f"Connected to PDF Assistant",
                "client_id": client_id
            }),
            client_id
        )
        
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            
    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(message)
            except Exception as e:
                print(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)
                
    async def broadcast_message(self, message: str):
        disconnected_clients = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
            
    async def send_chat_message(self, message: dict, client_id: str):
        """Send a formatted chat message"""
        await self.send_personal_message(
            json.dumps({
                "type": "chat_message",
                "data": message
            }),
            client_id
        )
        
    async def send_operation_update(self, operation_data: dict, client_id: str):
        """Send PDF operation status update"""
        await self.send_personal_message(
            json.dumps({
                "type": "operation_update",
                "data": operation_data
            }),
            client_id
        )
        
    async def send_error(self, error_message: str, client_id: str):
        """Send error message"""
        await self.send_personal_message(
            json.dumps({
                "type": "error",
                "message": error_message
            }),
            client_id
        )
        
    def get_connected_clients(self) -> List[str]:
        """Get list of connected client IDs"""
        return list(self.active_connections.keys())
        
    def is_connected(self, client_id: str) -> bool:
        """Check if client is connected"""
        return client_id in self.active_connections