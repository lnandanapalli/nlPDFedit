import { useState, useCallback } from 'react';
import apiService from '../services/apiService';
import { ChatMessage, ChatMessageRequest } from '../types';

export const useChat = (sessionId: string) => {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const loadChatHistory = useCallback(async () => {
        if (!sessionId) return;

        try {
            const history = await apiService.getChatHistory(sessionId);
            setMessages(history);
        } catch (err) {
            console.error('Failed to load chat history:', err);
            setError('Failed to load chat history');
        }
    }, [sessionId]);

    const sendMessage = useCallback(async (content: string) => {
        if (!sessionId || !content.trim()) return;

        setIsLoading(true);
        setError(null);

        // Add user message immediately
        const userMessage: ChatMessage = {
            id: Date.now().toString(),
            content: content.trim(),
            message_type: 'user',
            timestamp: new Date().toISOString(),
            session_id: sessionId
        };

        setMessages(prev => [...prev, userMessage]);

        try {
            const request: ChatMessageRequest = {
                content: content.trim(),
                session_id: sessionId
            };

            const response = await apiService.sendMessage(request);
            setMessages(prev => [...prev, response]);
        } catch (err: any) {
            const errorMessage = apiService.handleError(err);
            setError(errorMessage);

            // Add error message to chat
            const errorChatMessage: ChatMessage = {
                id: Date.now().toString(),
                content: `Error: ${errorMessage}`,
                message_type: 'error',
                timestamp: new Date().toISOString(),
                session_id: sessionId,
                operation_result: {
                    status: 'error',
                    error: errorMessage,
                    show_retry: true
                }
            };

            setMessages(prev => [...prev, errorChatMessage]);
        } finally {
            setIsLoading(false);
        }
    }, [sessionId]);

    const retryLastMessage = useCallback(async () => {
        const lastUserMessage = [...messages].reverse().find(msg => msg.message_type === 'user');
        if (lastUserMessage) {
            // Remove error message and retry
            setMessages(prev => prev.filter(msg => msg.message_type !== 'error'));
            await sendMessage(lastUserMessage.content);
        }
    }, [messages, sendMessage]);

    const clearHistory = useCallback(async () => {
        if (!sessionId) return;

        try {
            await apiService.clearChatHistory(sessionId);
            setMessages([]);
            setError(null);
        } catch (err) {
            const errorMessage = apiService.handleError(err);
            setError(errorMessage);
        }
    }, [sessionId]);

    return {
        messages,
        isLoading,
        error,
        sendMessage,
        retryLastMessage,
        clearHistory,
        loadChatHistory
    };
};