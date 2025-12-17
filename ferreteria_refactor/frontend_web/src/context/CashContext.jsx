import { createContext, useState, useContext, useEffect } from 'react';
import apiClient from '../config/axios';

const CashContext = createContext();

export const CashProvider = ({ children }) => {
    const [isSessionOpen, setIsSessionOpen] = useState(false);
    const [session, setSession] = useState(null);
    const [loading, setLoading] = useState(true);

    const checkStatus = async () => {
        try {
            const response = await apiClient.get('/cash/active');
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
    }, []);

    const openSession = async (sessionData) => {
        try {
            const response = await apiClient.post('/cash/open', sessionData);
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
            await apiClient.post(`/cash/${session.id}/close`, closeData);
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
