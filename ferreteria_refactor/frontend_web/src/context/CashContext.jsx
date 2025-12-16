import { createContext, useState, useContext, useEffect } from 'react';
import cashService from '../services/cashService';

const CashContext = createContext();

export const CashProvider = ({ children }) => {
    const [isSessionOpen, setIsSessionOpen] = useState(false);
    const [session, setSession] = useState(null);
    const [loading, setLoading] = useState(true);

    const checkStatus = async () => {
        try {
            // Mocking API response for dev if backend not ready
            // const data = await cashService.getStatus();

            // MOCK LOGIC for Proto: Check localStorage or default to false
            const mockOpen = localStorage.getItem('cash_session_open') === 'true';
            setIsSessionOpen(mockOpen);
            if (mockOpen) setSession({ id: 1, initial_cash: 100 }); // Mock session

            // Real implementation:
            // setIsSessionOpen(data.is_open);
            // setSession(data.session);
        } catch (error) {
            console.error("Failed to check cash status", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        checkStatus();
    }, []);

    const openSession = async (amount) => {
        // await cashService.openSession({ initial_cash: amount });
        localStorage.setItem('cash_session_open', 'true');
        setIsSessionOpen(true);
        setSession({ id: Date.now(), initial_cash: amount });
        return true;
    };

    const closeSession = async (finalCount) => {
        // await cashService.closeSession({ final_count: finalCount });
        localStorage.removeItem('cash_session_open');
        setIsSessionOpen(false);
        setSession(null);
        return true;
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
