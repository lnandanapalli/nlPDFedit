from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os
from dotenv import load_dotenv

from app.api import chat, files, pdf_operations
from app.services.websocket_manager import WebSocketManager

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="PDF Assistant API",
    description="Conversational PDF manipulation API with LLM integration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket manager
websocket_manager = WebSocketManager()

# Include routers
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
app.include_router(pdf_operations.router, prefix="/api/v1/pdf", tags=["pdf_operations"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "PDF Assistant API is running"}

# WebSocket endpoint for real-time chat
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket_manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages
            await websocket_manager.send_personal_message(f"Echo: {data}", client_id)
    except WebSocketDisconnect:
        websocket_manager.disconnect(client_id)

# Serve uploaded files
@app.get("/files/{file_path:path}")
async def serve_file(file_path: str):
    file_location = f"uploads/{file_path}"
    if os.path.exists(file_location):
        return FileResponse(file_location)
    raise HTTPException(status_code=404, detail="File not found")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "PDF Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )