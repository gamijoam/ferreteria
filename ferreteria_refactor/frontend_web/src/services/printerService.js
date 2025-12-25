import apiClient from '../config/axios';

// Hardware Bridge Client ID (should match .env in Hardware Bridge)
const HARDWARE_CLIENT_ID = 'escritorio-caja-1';

const printerService = {
    /**
     * Trigger print via WebSocket to Hardware Bridge
     * @param {number} saleId - The ID of the sale to print
     */
    printTicket: async (saleId) => {
        try {
            // Send print command to backend, which forwards to Hardware Bridge via WebSocket
            const response = await apiClient.post(`/products/print/remote`, {
                client_id: HARDWARE_CLIENT_ID,
                sale_id: saleId
            });

            return response.data;
        } catch (error) {
            console.error("Print Error:", error);

            // Enhanced error messages
            if (error.response?.status === 503) {
                throw new Error("Hardware Bridge no está conectado. Verifique que 'BridgeInvensoft.exe' esté ejecutándose.");
            } else if (error.response?.status === 500) {
                throw new Error(error.response?.data?.detail || "Error al enviar comando de impresión");
            } else if (error.message.includes("Network Error")) {
                throw new Error("No se puede conectar con el servidor. Verifique su conexión a internet.");
            }

            throw error;
        }
    }
};

export default printerService;
