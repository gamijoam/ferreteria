import apiClient from '../config/axios';

const cashService = {
    getStatus: async () => {
        // GET /cash/session/current
        // Should return { is_open: boolean, session: { id, initial_cash, ... } }
        const response = await apiClient.get('/cash/session/current');
        return response.data;
    },

    openSession: async (data) => {
        // data: { initial_cash: number }
        const response = await apiClient.post('/cash/session/open', data);
        return response.data;
    },

    closeSession: async (data) => {
        // data: { final_count: number, notes: string }
        const response = await apiClient.post('/cash/session/close', data);
        return response.data;
    },

    addMovement: async (data) => {
        // data: { type: 'EXPENSE'|'WITHDRAWAL', amount: number, reason: string }
        const response = await apiClient.post('/cash/movement', data);
        return response.data;
    }
};

export default cashService;
