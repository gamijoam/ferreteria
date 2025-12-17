import { useState, useEffect } from 'react';
import { DollarSign, CreditCard, Banknote, CheckCircle, Calculator } from 'lucide-react';
import { useConfig } from '../../context/ConfigContext';

const PaymentModal = ({ isOpen, onClose, totalUSD, onConfirm }) => {
    const { getActiveCurrencies, convertPrice, getExchangeRate } = useConfig();
    const currencies = [{ id: 'base', symbol: 'USD', name: 'Dólar', rate: 1, is_anchor: true }, ...getActiveCurrencies()];

    // State for multiple payments: [{ amount: 0, currency: 'USD', method: 'Efectivo' }]
    const [payments, setPayments] = useState([]);
    const [processing, setProcessing] = useState(false);

    // Initialize with one default payment entry
    useEffect(() => {
        if (isOpen) {
            setPayments([{ amount: '', currency: 'USD', method: 'Efectivo' }]);
        }
    }, [isOpen]);

    if (!isOpen) return null;

    // Calculate Totals
    const totalPaidUSD = payments.reduce((acc, p) => {
        const amount = parseFloat(p.amount) || 0;
        const rate = getExchangeRate(p.currency);
        // If rate is 0 or undefined, avoid division by zero (shouldn't happen with valid config)
        return acc + (amount / (rate || 1));
    }, 0);

    const remainingUSD = totalUSD - totalPaidUSD;
    const changeUSD = totalPaidUSD - totalUSD;
    const isComplete = remainingUSD <= 0.01; // Tolerance

    const addPaymentRow = () => {
        setPayments([...payments, { amount: '', currency: 'USD', method: 'Efectivo' }]);
    };

    const removePaymentRow = (index) => {
        const newPayments = [...payments];
        newPayments.splice(index, 1);
        setPayments(newPayments);
    };

    const updatePayment = (index, field, value) => {
        const newPayments = [...payments];
        newPayments[index][field] = value;
        setPayments(newPayments);
    };

    const handleConfirm = async () => {
        if (!isComplete && Math.abs(remainingUSD) > 0.01) return;
        setProcessing(true);
        // Simulate API delay
        await new Promise(r => setTimeout(r, 1000));

        // Pass summarized payment data
        onConfirm({
            payments,
            totalPaidUSD,
            changeUSD: changeUSD > 0 ? changeUSD : 0
        });

        setProcessing(false);
        onClose();
    };

    return (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl overflow-hidden flex flex-col md:flex-row h-[600px]">
                {/* Left: Totals Summary */}
                <div className="bg-slate-900 text-white p-8 md:w-1/3 flex flex-col relative">
                    <h3 className="text-gray-400 uppercase text-sm font-bold mb-6">Resumen de Pago</h3>

                    <div className="mb-8">
                        <div className="text-sm text-gray-400">Total a Pagar</div>
                        <div className="text-4xl font-bold text-white tracking-tight">${totalUSD.toFixed(2)}</div>
                    </div>

                    <div className="space-y-4 mb-8 flex-1 overflow-y-auto">
                        {currencies.map(curr => (
                            <div key={curr.symbol} className="flex justify-between items-center border-b border-gray-700 pb-2">
                                <span className="text-gray-400 text-sm">{curr.name}</span>
                                <span className="font-mono text-blue-300">
                                    {convertPrice(totalUSD, curr.symbol).toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} {curr.symbol}
                                </span>
                            </div>
                        ))}
                    </div>

                    <div className={`mt-auto p-4 rounded-lg ${isComplete ? 'bg-green-600/20 border border-green-500' : 'bg-red-600/20 border border-red-500'}`}>
                        {isComplete ? (
                            <div className="text-center">
                                <div className="text-sm text-green-300 mb-1">Cambio / Vuelto</div>
                                <div className="text-3xl font-bold text-green-400">${changeUSD.toFixed(2)}</div>
                            </div>
                        ) : (
                            <div className="text-center">
                                <div className="text-sm text-red-300 mb-1">Faltante</div>
                                <div className="text-3xl font-bold text-red-400">${remainingUSD.toFixed(2)}</div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Right: Hybrid Payment Form */}
                <div className="p-8 md:w-2/3 bg-gray-50 flex flex-col">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="text-gray-800 font-bold text-xl flex items-center">
                            <Banknote className="mr-2" /> Pagos Recibidos
                        </h3>
                        <button
                            onClick={addPaymentRow}
                            className="text-sm bg-blue-100 text-blue-700 px-3 py-1 rounded-full font-bold hover:bg-blue-200 transition"
                        >
                            + Agregar Método
                        </button>
                    </div>

                    <div className="flex-1 overflow-y-auto space-y-3 mb-6 pr-2">
                        {payments.map((payment, index) => (
                            <div key={index} className="flex gap-2 items-center bg-white p-3 rounded-lg shadow-sm border border-gray-200">
                                <select
                                    className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5"
                                    value={payment.method}
                                    onChange={(e) => updatePayment(index, 'method', e.target.value)}
                                >
                                    <option value="Efectivo">Efectivo</option>
                                    <option value="Pago Movil">Pago Móvil</option>
                                    <option value="Punto de Venta">Punto Venta</option>
                                    <option value="Zelle">Zelle</option>
                                    <option value="Transferencia">Transferencia</option>
                                </select>

                                <select
                                    className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5 w-24"
                                    value={payment.currency}
                                    onChange={(e) => updatePayment(index, 'currency', e.target.value)}
                                >
                                    {currencies.map(c => (
                                        <option key={c.symbol} value={c.symbol}>{c.symbol}</option>
                                    ))}
                                </select>

                                <div className="relative flex-1">
                                    <input
                                        type="number"
                                        className="block w-full p-2.5 text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500"
                                        placeholder="Monto"
                                        value={payment.amount}
                                        onChange={(e) => updatePayment(index, 'amount', e.target.value)}
                                        autoFocus={index === payments.length - 1} // Autofocus on new rows
                                    />
                                </div>

                                {payments.length > 1 && (
                                    <button
                                        onClick={() => removePaymentRow(index)}
                                        className="text-red-400 hover:text-red-600 p-2"
                                    >
                                        &times;
                                    </button>
                                )}
                            </div>
                        ))}
                    </div>

                    <div className="mt-auto flex justify-end gap-3">
                        <button onClick={onClose} className="px-6 py-3 text-gray-600 font-bold hover:bg-gray-200 rounded-lg">Cancelar</button>
                        <button
                            onClick={handleConfirm}
                            disabled={!isComplete || processing}
                            className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-lg shadow-lg flex items-center justify-center text-lg"
                        >
                            {processing ? 'Procesando...' : (
                                <>
                                    <CheckCircle className="mr-2" /> Completar Venta
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

