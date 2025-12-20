import apiClient from '../config/axios';

const printerService = {
    /**
     * Trigger re-print of a ticket via backend
     * @param {number} saleId - The ID of the sale to print
     */
    printTicket: async (saleId) => {
        try {
            // Updated to use the new backend endpoint
            const response = await apiClient.post(`/products/sales/${saleId}/print`);
            return response.data;
        } catch (error) {
            console.error("Print Error:", error);
            throw new Error("No se pudo enviar la orden de impresión al servidor.");
        }
    }
};

export default printerService;
