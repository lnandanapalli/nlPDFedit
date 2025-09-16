import { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';

export const useSession = () => {
    const [sessionId, setSessionId] = useState<string>('');

    useEffect(() => {
        // Get or create session ID
        const storedSessionId = localStorage.getItem('pdf_chat_session_id');

        if (storedSessionId) {
            setSessionId(storedSessionId);
        } else {
            const newSessionId = uuidv4();
            localStorage.setItem('pdf_chat_session_id', newSessionId);
            setSessionId(newSessionId);
        }
    }, []);

    const createNewSession = () => {
        const newSessionId = uuidv4();
        localStorage.setItem('pdf_chat_session_id', newSessionId);
        setSessionId(newSessionId);
        return newSessionId;
    };

    return { sessionId, createNewSession };
};