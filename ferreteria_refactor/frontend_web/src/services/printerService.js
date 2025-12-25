import apiClient from '../config/axios';

const printerService = {
    /**
     * Trigger re-print of a ticket via backend
     * @param {number} saleId - The ID of the sale to print
     */
    printTicket: async (saleId) => {
        try {
            // 1. Get Payload from Backend (SaaS)
            const response = await apiClient.post(`/products/sales/${saleId}/print`);
            const payload = response.data;

            if (!payload.template || !payload.context) {
                console.warn("Backend returned incomplete payload:", payload);
                if (payload.message) return payload; // Maybe it's just a message
            }

            // 2. Send to Local Hardware Bridge (Localhost)
            // Use fetch directly to avoid apiClient interceptors/base URLs
            const bridgeResponse = await fetch("http://localhost:5001/print", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            if (!bridgeResponse.ok) {
                const errText = await bridgeResponse.text();
                throw new Error(`Bridge Error: ${bridgeResponse.statusText} - ${errText}`);
            }

            return await bridgeResponse.json();
        } catch (error) {
            console.error("Print Error:", error);
            // Enhance error message
            if (error.message.includes("Failed to fetch")) {
                throw new Error("No se puede conectar con el Puente de Impresión (Hardware Bridge). Verifique que 'BridgeInvensoft.exe' esté ejecutándose en el puerto 5001.");
            }
            throw error;
        }
    }
};

export default printerService;
