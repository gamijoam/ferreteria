import { useState, useEffect } from 'react';
import { Archive, ArrowDownCircle, ArrowUpCircle, Filter, Search } from 'lucide-react';
import AdjustmentModal from '../components/inventory/AdjustmentModal';

const Inventory = () => {
    const [kardex, setKardex] = useState([]);
    const [isModalOpen, setIsModalOpen] = useState(false);

    // Mock data for Kardex
    useEffect(() => {
        // In real app, fetch from inventoryService.getKardex()
        setKardex([
            { id: 101, date: '2025-12-16 10:30', product: 'Cemento Gris Portland', type: 'SALE', quantity_base: 2, balance: 448, note: 'Venta #1023' },
            { id: 100, date: '2025-12-16 09:15', product: 'Cemento Gris Portland', type: 'ADJUSTMENT_IN', quantity_base: 50, balance: 450, note: 'Ajuste inicial' },
            { id: 99, date: '2025-12-15 16:45', product: 'Tubería PVC', type: 'SALE', quantity_base: 5, balance: 75, note: 'Venta #1020' },
        ]);
    }, []);

    const getMovementStyle = (type) => {
        if (['SALE', 'ADJUSTMENT_OUT', 'DAMAGED', 'INTERNAL_USE', 'OUT'].includes(type)) {
            return { color: 'text-red-600', icon: <ArrowDownCircle size={16} className="mr-1" />, bg: 'bg-red-50' };
        }
        return { color: 'text-green-600', icon: <ArrowUpCircle size={16} className="mr-1" />, bg: 'bg-green-50' };
    };

    const getLabel = (type) => {
        const labels = {
            'SALE': 'Venta',
            'PURCHASE': 'Compra',
            'ADJUSTMENT_IN': 'Entrada Ajuste',
            'ADJUSTMENT_OUT': 'Salida Ajuste',
            'DAMAGED': 'Dañado',
            'INTERNAL_USE': 'Uso Interno'
        };
        return labels[type] || type;
    };

    return (
        <div className="container mx-auto">
            <div className="flex flex-col md:flex-row md:items-center justify-between mb-6 gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-800 flex items-center">
                        <Archive className="mr-2" /> Movimientos de Inventario
                    </h1>
                    <p className="text-gray-500">Historial completo de entradas y salidas (Kardex)</p>
                </div>
                <button
                    onClick={() => setIsModalOpen(true)}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded shadow-sm transition-all font-medium"
                >
                    Nuevo Ajuste Manual
                </button>
            </div>

            {/* Filters */}
            <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 mb-6 flex flex-col md:flex-row gap-4">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-2.5 text-gray-400" size={20} />
                    <input
                        type="text"
                        placeholder="Buscar por producto..."
                        className="w-full pl-10 pr-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>
                <div className="flex gap-4">
                    <input type="date" className="border rounded-md px-3 py-2 text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500" />
                    <span className="self-center text-gray-400">a</span>
                    <input type="date" className="border rounded-md px-3 py-2 text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500" />
                    <button className="p-2 border rounded-md hover:bg-gray-50 text-gray-600">
                        <Filter size={20} />
                    </button>
                </div>
            </div>

            {/* Table */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha / Hora</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Producto</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Movimiento</th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Cantidad</th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Saldo Final</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nota</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {kardex.map(item => {
                                const style = getMovementStyle(item.type);
                                return (
                                    <tr key={item.id} className="hover:bg-gray-50 transition-colors">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{item.date}</td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className="font-medium text-gray-900">{item.product}</span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${style.bg} ${style.color}`}>
                                                {style.icon}
                                                {getLabel(item.type)}
                                            </span>
                                        </td>
                                        <td className={`px-6 py-4 whitespace-nowrap text-sm text-right font-bold ${style.color}`}>
                                            {['SALE', 'ADJUSTMENT_OUT', 'DAMAGED', 'INTERNAL_USE'].includes(item.type) ? '-' : '+'}{item.quantity_base}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-medium text-gray-900">
                                            {item.balance}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 italic truncate max-w-xs">{item.note}</td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
                {kardex.length === 0 && (
                    <div className="p-10 text-center text-gray-500">
                        No hay movimientos registrados en este periodo.
                    </div>
                )}
            </div>

            <AdjustmentModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSuccess={() => console.log('Refresh Kardex')}
            />
        </div>
    );
};

export default Inventory;
