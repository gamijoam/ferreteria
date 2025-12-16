import { useState, useEffect } from 'react';
import { useCash } from '../context/CashContext';
import { useNavigate } from 'react-router-dom';
import { ClipboardCheck, DollarSign, AlertCircle } from 'lucide-react';

const CashClose = () => {
    const { isSessionOpen, closeSession } = useCash();
    const navigate = useNavigate();

    const [systemTotal, setSystemTotal] = useState(0); // Expected calculated by system
    const [physicalCount, setPhysicalCount] = useState('');
    const [notes, setNotes] = useState('');

    // Mock fetching system totals
    useEffect(() => {
        if (isSessionOpen) {
            // Fetch from backend: initial + sales - movements
            setSystemTotal(350.00); // Mock value: 100 initial + 250 sales
        }
    }, [isSessionOpen]);

    // If session closed, redirect
    if (!isSessionOpen) {
        return (
            <div className="p-10 text-center">
                <h2 className="text-xl">Caja Cerrada</h2>
                <button
                    onClick={() => navigate('/pos')}
                    className="mt-4 text-blue-600 underline"
                >
                    Ir a Abrir Caja en POS
                </button>
            </div>
        );
    }

    const difference = (Number(physicalCount) || 0) - systemTotal;

    const handleClose = async () => {
        if (!physicalCount) return alert("Ingresa el conteo físico");

        if (window.confirm("¿Seguro que deseas cerrar el turno? Esto generará el Reporte Z.")) {
            await closeSession(Number(physicalCount));
            alert("Caja Cerrada Exitosamente");
            navigate('/');
        }
    };

    return (
        <div className="max-w-4xl mx-auto p-6">
            <div className="flex items-center space-x-3 mb-8">
                <div className="bg-blue-100 p-3 rounded-full text-blue-600">
                    <ClipboardCheck size={32} />
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-gray-800">Cierre de Caja (Arqueo)</h1>
                    <p className="text-gray-500">Verifica los montos antes de generar el Reporte Z</p>
                </div>
            </div>

            <div className="grid md:grid-cols-2 gap-8">
                {/* System Summary */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h3 className="text-lg font-bold text-gray-700 mb-4 border-b pb-2">Resumen del Sistema</h3>

                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <span className="text-gray-600">Saldo Inicial</span>
                            <span className="font-medium">$100.00</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-600">Ventas (Efectivo)</span>
                            <span className="font-medium text-green-600">+$280.00</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-600">Gastos / Retiros</span>
                            <span className="font-medium text-red-600">-$30.00</span>
                        </div>
                        <div className="border-t pt-3 flex justify-between items-center mt-4">
                            <span className="font-bold text-gray-800 text-lg">Saldo Esperado</span>
                            <span className="font-bold text-blue-600 text-2xl">${systemTotal.toFixed(2)}</span>
                        </div>
                    </div>
                </div>

                {/* Physical Count */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h3 className="text-lg font-bold text-gray-700 mb-4 border-b pb-2">Conteo Físico (Ciego)</h3>

                    <div className="mb-6">
                        <label className="block text-sm font-bold text-gray-700 mb-2">Dinero en Efectivo ($)</label>
                        <div className="relative">
                            <DollarSign className="absolute left-3 top-3.5 text-gray-400" />
                            <input
                                type="number"
                                className="w-full pl-10 p-3 border-2 border-blue-100 focus:border-blue-500 rounded-lg text-2xl font-bold text-gray-800 outline-none"
                                value={physicalCount}
                                onChange={(e) => setPhysicalCount(e.target.value)}
                                placeholder="0.00"
                            />
                        </div>
                    </div>

                    {physicalCount !== '' && (
                        <div className={`p-4 rounded-lg flex items-start space-x-3 mb-6 ${difference === 0 ? 'bg-green-50 text-green-800' : 'bg-yellow-50 text-yellow-800'}`}>
                            <AlertCircle size={24} className={difference === 0 ? 'text-green-600' : 'text-yellow-600'} />
                            <div>
                                <div className="font-bold">Diferencia: ${difference.toFixed(2)}</div>
                                <div className="text-sm">
                                    {difference === 0
                                        ? 'Cuadre perfecto.'
                                        : difference > 0 ? 'Sobrante en caja.' : 'Faltante en caja.'}
                                </div>
                            </div>
                        </div>
                    )}

                    <div className="mb-6">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Notas del Cierre</label>
                        <textarea
                            className="w-full border rounded p-2"
                            rows="2"
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
                        ></textarea>
                    </div>

                    <button
                        onClick={handleClose}
                        disabled={!physicalCount}
                        className="w-full bg-slate-800 hover:bg-slate-900 text-white font-bold py-3 rounded-lg shadow transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Cerrar Turno e Imprimir
                    </button>
                </div>
            </div>
        </div>
    );
};

export default CashClose;
