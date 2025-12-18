import { createContext, useState, useContext, useEffect } from 'react';
import apiClient from '../config/axios';
import { useWebSocket } from './WebSocketContext';

const CashContext = createContext();

export const CashProvider = ({ children }) => {
    const [isSessionOpen, setIsSessionOpen] = useState(false);
    const [session, setSession] = useState(null);
    const [loading, setLoading] = useState(true);
    const { subscribe } = useWebSocket();

    const checkStatus = async () => {
        try {
            const response = await apiClient.get('/cash/sessions/current');
            setIsSessionOpen(true);
            setSession(response.data);
        } catch (error) {
            // No active session
            setIsSessionOpen(false);
            setSession(null);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        checkStatus();

        // WebSocket Subscriptions
        const unsubOpen = subscribe('cash_session:opened', (data) => {
            console.log('💵 Session Opened Real-time:', data);

            // To be safe, we might want to fetch full session details because 'data' from WS might be partial
            // But for now let's assume valid
            setIsSessionOpen(true);
            // Ideally we should setSession, but if WS data is small, fetch full
            checkStatus(); // Safe way: re-check status
        });

        const unsubClose = subscribe('cash_session:closed', (data) => {
            console.log('💵 Session Closed Real-time:', data);
            setIsSessionOpen(false);
            setSession(null);
        });

        return () => {
            unsubOpen();
            unsubClose();
        };
    }, [subscribe]);

    const openSession = async (sessionData) => {
        try {
            const response = await apiClient.post('/cash/sessions/open', sessionData);
            setIsSessionOpen(true);
            setSession(response.data);
            return true;
        } catch (error) {
            console.error('Error opening session:', error);
            alert('Error al abrir caja: ' + (error.response?.data?.detail || error.message));
            return false;
        }
    };

    const closeSession = async (closeData) => {
        try {
            if (!session) return false;
            await apiClient.post(`/cash/sessions/${session.id}/close`, closeData);
            setIsSessionOpen(false);
            setSession(null);
            return true;
        } catch (error) {
            console.error('Error closing session:', error);
            alert('Error al cerrar caja: ' + (error.response?.data?.detail || error.message));
            return false;
        }
    };

    return (
        <CashContext.Provider value={{
            isSessionOpen,
            session,
            loading,
            openSession,
            closeSession,
            refreshStatus: checkStatus
        }}>
            {children}
        </CashContext.Provider>
    );
};

export const useCash = () => useContext(CashContext);
