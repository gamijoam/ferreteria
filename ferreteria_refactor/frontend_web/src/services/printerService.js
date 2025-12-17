import axios from 'axios';

const printerClient = axios.create({
    baseURL: 'http://localhost:8001',
    timeout: 5000 // Fail fast if bridge is not running
});

const printerService = {
    printTicket: async (saleData) => {
        // saleData: { cart, totalUSD, totalBs, paymentData } (Needs transformation to match Backend schema)

        const ticketPayload = {
            header: [
                "FERRETERIA EL NUEVO PROGRESO",
                "RIF: J-12345678-9",
                "Av. Principal Las Acacias",
                `Fecha: ${new Date().toLocaleString()}`
            ],
            items: saleData.cart.map(item => ({
                name: item.name,
                quantity: item.quantity,
                unit: item.unit_name,
                price: item.unit_price_usd,
                total: item.subtotal_usd
            })),
            totals: {
                "SUBTOTAL USD": saleData.totalUSD,
                "TOTAL BS": saleData.totalBs,
                "METODO PAGO": saleData.paymentData.method.toUpperCase(),
                "RECIBIDO": Number(saleData.paymentData.amountReceived || 0)
            },
            footer: [
                "¡Gracias por su compra!",
                "Conserve este ticket para cambios",
                "NO SE ACEPTAN DEVOLUCIONES DESPUES DE 24H"
            ]
        };

        try {
            const response = await printerClient.post('/print-ticket', ticketPayload);
            return response.data;
        } catch (error) {
            console.error("Print Error:", error);
            throw new Error("No se pudo conectar con el servicio de impresión (Hardware Bridge). Asegúrese de que esté corriendo.");
        }
    }
};

export default printerService;
