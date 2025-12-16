import { useState } from 'react';
import { DollarSign, CreditCard, Banknote, CheckCircle } from 'lucide-react';

const PaymentModal = ({ isOpen, onClose, totalUSD, totalBs, onConfirm }) => {
    const [method, setMethod] = useState('cash_usd');
    const [amountReceived, setAmountReceived] = useState('');
    const [processing, setProcessing] = useState(false);

    if (!isOpen) return null;

    const change = amountReceived ? Number(amountReceived) - totalUSD : 0;

    const handleConfirm = async () => {
        setProcessing(true);
        // Simulate API delay
        await new Promise(r => setTimeout(r, 1000));
        onConfirm({ method, amountReceived, totalUSD, totalBs });
        setProcessing(false);
        onClose();
    };

    return (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl overflow-hidden flex flex-col md:flex-row h-[500px]">
                {/* Left: Totals */}
                <div className="bg-slate-900 text-white p-8 md:w-2/5 flex flex-col justify-center relative">
                    <h3 className="text-gray-400 uppercase text-sm font-bold mb-6">Total a Pagar</h3>

                    <div className="mb-8">
                        <div className="text-5xl font-bold text-green-400 tracking-tight">${totalUSD.toFixed(2)}</div>
                        <div className="text-sm text-gray-400 mt-1">Dólares (USD)</div>
                    </div>

                    <div>
                        <div className="text-3xl font-bold text-blue-300 tracking-tight">Bs {totalBs.toFixed(2)}</div>
                        <div className="text-sm text-gray-400 mt-1">Bolívares (VES)</div>
                    </div>

                    <div className="mt-auto border-t border-slate-700 pt-6">
                        <div className="text-sm text-gray-400">Tasa de Cambio</div>
                        <div className="text-xl font-mono">{(totalBs / totalUSD || 0).toFixed(2)} / $</div>
                    </div>
                </div>

                {/* Right: Payment Method */}
                <div className="p-8 md:w-3/5 bg-gray-50 flex flex-col">
                    <h3 className="text-gray-800 font-bold text-xl mb-6">Método de Pago</h3>

                    <div className="grid grid-cols-2 gap-3 mb-6">
                        <button
                            onClick={() => setMethod('cash_usd')}
                            className={`p-4 rounded-lg border-2 flex flex-col items-center justify-center transition-all ${method === 'cash_usd' ? 'border-green-500 bg-green-50 text-green-700' : 'border-gray-200 text-gray-500 hover:border-gray-300'}`}
                        >
                            <DollarSign size={24} className="mb-2" />
                            <span className="font-bold text-sm">Efectivo USD</span>
                        </button>
                        <button
                            onClick={() => setMethod('pago_movil')}
                            className={`p-4 rounded-lg border-2 flex flex-col items-center justify-center transition-all ${method === 'pago_movil' ? 'border-blue-500 bg-blue-50 text-blue-700' : 'border-gray-200 text-gray-500 hover:border-gray-300'}`}
                        >
                            <Banknote size={24} className="mb-2" />
                            <span className="font-bold text-sm">Pago Móvil</span>
                        </button>
                        <button
                            onClick={() => setMethod('zelle')}
                            className={`p-4 rounded-lg border-2 flex flex-col items-center justify-center transition-all ${method === 'zelle' ? 'border-purple-500 bg-purple-50 text-purple-700' : 'border-gray-200 text-gray-500 hover:border-gray-300'}`}
                        >
                            <CreditCard size={24} className="mb-2" />
                            <span className="font-bold text-sm">Zelle</span>
                        </button>
                        <button
                            onClick={() => setMethod('point')}
                            className={`p-4 rounded-lg border-2 flex flex-col items-center justify-center transition-all ${method === 'point' ? 'border-orange-500 bg-orange-50 text-orange-700' : 'border-gray-200 text-gray-500 hover:border-gray-300'}`}
                        >
                            <CreditCard size={24} className="mb-2" />
                            <span className="font-bold text-sm">Punto Venta</span>
                        </button>
                    </div>

                    <div className="mb-6">
                        <label className="block text-sm font-bold text-gray-700 mb-2">Monto Recibido</label>
                        <input
                            type="number"
                            className="w-full text-2xl p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                            placeholder="0.00"
                            value={amountReceived}
                            onChange={(e) => setAmountReceived(e.target.value)}
                        />
                        {amountReceived && change >= 0 && (
                            <div className="mt-2 text-right">
                                <span className="text-gray-500 text-sm">Vuelto Estimado: </span>
                                <span className="font-bold text-green-600 text-lg">${change.toFixed(2)}</span>
                            </div>
                        )}
                    </div>

                    <div className="mt-auto flex justify-end gap-3">
                        <button onClick={onClose} className="px-6 py-3 text-gray-600 font-bold hover:bg-gray-200 rounded-lg">Cancelar</button>
                        <button
                            onClick={handleConfirm}
                            disabled={processing}
                            className="flex-1 bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg shadow-lg flex items-center justify-center text-lg disabled:opacity-50"
                        >
                            {processing ? 'Procesando...' : (
                                <>
                                    <CheckCircle className="mr-2" /> Finalizar Venta
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PaymentModal;
