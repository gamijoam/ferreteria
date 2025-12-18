import { useState, useEffect } from 'react';
import { DollarSign, CreditCard, Banknote, CheckCircle, Calculator, Users, X } from 'lucide-react';
import { useConfig } from '../../context/ConfigContext';
import apiClient from '../../config/axios';
import toast from 'react-hot-toast';

const PaymentModal = ({ isOpen, onClose, totalUSD, totalsByCurrency, cart, onConfirm }) => {
    const { getActiveCurrencies, convertPrice, getExchangeRate } = useConfig();
    const currencies = [{ id: 'base', symbol: 'USD', name: 'Dólar', rate: 1, is_anchor: true }, ...getActiveCurrencies()];

    // State for multiple payments
    const [payments, setPayments] = useState([]);
    const [processing, setProcessing] = useState(false);

    // Credit sale states
    const [isCreditSale, setIsCreditSale] = useState(false);
    const [customers, setCustomers] = useState([]);
    const [selectedCustomer, setSelectedCustomer] = useState(null);

    useEffect(() => {
        if (isOpen) {
            setPayments([{ amount: '', currency: 'USD', method: 'Efectivo' }]);
            setIsCreditSale(false);
            setSelectedCustomer(null);
            fetchCustomers();
        }
    }, [isOpen]);

    const fetchCustomers = async () => {
        try {
            const response = await apiClient.get('/customers', { params: { limit: 100 } });
            setCustomers(response.data);
        } catch (error) {
            console.error('Error fetching customers:', error);
        }
    };

    if (!isOpen) return null;

    // Calculate Totals
    const totalPaidUSD = payments.reduce((acc, p) => {
        const amount = parseFloat(p.amount) || 0;
        const rate = getExchangeRate(p.currency);
        return acc + (amount / (rate || 1));
    }, 0);

    const remainingUSD = totalUSD - totalPaidUSD;
    const changeUSD = totalPaidUSD - totalUSD;
    const isComplete = remainingUSD <= 0.01;

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
        if (isCreditSale && !selectedCustomer) {
            alert('Debe seleccionar un cliente para venta a crédito');
            return;
        }

        if (!isCreditSale && !isComplete && Math.abs(remainingUSD) > 0.01) {
            alert('El pago no está completo');
            return;
        }

        setProcessing(true);

        try {
            const saleData = {
                total_amount: totalUSD,
                currency: "USD",
                exchange_rate: getExchangeRate('Bs') || 1,
                payment_method: isCreditSale ? "Credito" : (payments[0]?.method || "Efectivo"),
                payments: isCreditSale ? [] : payments.map(p => ({
                    amount: parseFloat(p.amount) || 0,
                    currency: p.currency,
                    payment_method: p.method,
                    exchange_rate: getExchangeRate(p.currency) || 1
                })),
                items: cart.map(item => ({
                    product_id: item.product_id,
                    quantity: item.quantity,
                    unit_price_usd: item.unit_price_usd || item.price_unit_usd,
                    conversion_factor: item.conversion_factor || 1,
                    discount: 0,
                    discount_type: "NONE"
                })),
                is_credit: isCreditSale,
                customer_id: isCreditSale ? selectedCustomer.id : null,
                notes: ""
            };

            // ... (inside handleConfirm)

            await apiClient.post('/products/sales/', saleData);

            onConfirm({
                payments: isCreditSale ? [] : payments,
                totalPaidUSD: isCreditSale ? 0 : totalPaidUSD,
                changeUSD: isCreditSale ? 0 : (changeUSD > 0 ? changeUSD : 0),
                isCreditSale,
                customer: isCreditSale ? selectedCustomer : null
            });

            setProcessing(false);
            onClose();
        } catch (error) {
            console.error('Error creating sale:', error);
            const errorMessage = error.response?.data?.detail || error.message || "Error desconocido al procesar venta";
            toast.error(errorMessage);
            setProcessing(false);
        }
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
                        <div className="space-y-4 mb-8 flex-1 overflow-y-auto">
                            {currencies.map(curr => {
                                // If it's the anchor currency (USD), show totalUSD directly
                                const amount = curr.is_anchor
                                    ? totalUSD
                                    : (totalsByCurrency?.[curr.currency_code] || 0);

                                return (
                                    <div key={curr.symbol} className="flex justify-between items-center border-b border-gray-700 pb-2">
                                        <span className="text-gray-400 text-sm">{curr.name}</span>
                                        <span className="font-mono text-blue-300 flex flex-col items-end">
                                            <span>{amount.toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} {curr.symbol}</span>
                                            {curr.symbol !== 'USD' && (
                                                <span className="text-xs text-gray-500">Tasa Ref: {curr.rate.toLocaleString('es-VE')}</span>
                                            )}
                                        </span>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {!isCreditSale && (
                        <div className={`mt-auto p-4 rounded-lg ${isComplete ? 'bg-green-600/20 border border-green-500' : 'bg-red-600/20 border border-red-500'}`}>
                            {isComplete ? (
                                <div className="text-center">
                                    <div className="text-sm text-green-300 mb-1">Cambio / Vuelto</div>
                                    <div className="text-3xl font-bold text-green-400">${changeUSD.toFixed(2)}</div>
                                </div>
                            ) : (
                                <div className="text-center">
                                    <div className="text-sm text-red-300 mb-1">Falta por Pagar</div>
                                    <div className="text-3xl font-bold text-red-400">${Math.abs(remainingUSD).toFixed(2)}</div>
                                </div>
                            )}
                        </div>
                    )}

                    {isCreditSale && selectedCustomer && (
                        <div className="mt-auto p-4 rounded-lg bg-blue-600/20 border border-blue-500">
                            <div className="text-center">
                                <div className="text-sm text-blue-300 mb-1">Cliente</div>
                                <div className="text-lg font-bold text-blue-400">{selectedCustomer.name}</div>
                                <div className="text-xs text-blue-300 mt-2">
                                    Límite: ${selectedCustomer.credit_limit?.toFixed(2) || '0.00'}
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Right: Payment Input */}
                <div className="p-8 md:w-2/3 bg-gray-50 flex flex-col">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="text-gray-800 font-bold text-xl flex items-center">
                            <Banknote className="mr-2" /> Método de Pago
                        </h3>
                        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
                            <X size={24} />
                        </button>
                    </div>

                    {/* Credit Sale Toggle */}
                    <div className="mb-6 p-4 bg-blue-50 border-2 border-blue-200 rounded-lg">
                        <label className="flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={isCreditSale}
                                onChange={(e) => setIsCreditSale(e.target.checked)}
                                className="w-5 h-5 mr-3"
                            />
                            <Users className="mr-2 text-blue-600" size={20} />
                            <span className="font-semibold text-blue-800">Venta a Crédito</span>
                        </label>
                    </div>

                    {/* Customer Selection (only for credit sales) */}
                    {isCreditSale && (
                        <div className="mb-6">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Seleccionar Cliente *
                            </label>
                            <select
                                value={selectedCustomer?.id || ''}
                                onChange={(e) => {
                                    const customer = customers.find(c => c.id === parseInt(e.target.value));
                                    setSelectedCustomer(customer);
                                }}
                                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                            >
                                <option value="">-- Seleccione un cliente --</option>
                                {customers.map(customer => (
                                    <option key={customer.id} value={customer.id}>
                                        {customer.name} - {customer.id_number || 'Sin ID'}
                                    </option>
                                ))}
                            </select>
                            {selectedCustomer && (
                                <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded text-sm">
                                    <p className="font-semibold text-green-800">
                                        Límite: ${selectedCustomer.credit_limit?.toFixed(2) || '0.00'}
                                    </p>
                                    <p className="text-green-700">
                                        Plazo: {selectedCustomer.payment_term_days || 15} días
                                    </p>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Payment Rows (only for cash sales) */}
                    {!isCreditSale && (
                        <>
                            <div className="flex justify-end mb-3">
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
                                            {currencies.map(curr => (
                                                <option key={curr.symbol} value={curr.symbol}>{curr.symbol}</option>
                                            ))}
                                        </select>

                                        <input
                                            type="number"
                                            step="0.01"
                                            placeholder="Monto"
                                            className="flex-1 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5"
                                            value={payment.amount}
                                            onChange={(e) => updatePayment(index, 'amount', e.target.value)}
                                        />

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
                        </>
                    )}

                    {/* Actions */}
                    <div className="mt-auto flex gap-4">
                        <button
                            onClick={onClose}
                            className="flex-1 px-6 py-3 border-2 border-gray-300 rounded-lg hover:bg-gray-50 font-semibold transition-colors"
                        >
                            Cancelar
                        </button>
                        <button
                            onClick={handleConfirm}
                            disabled={processing || (!isCreditSale && !isComplete) || (isCreditSale && !selectedCustomer)}
                            className={`flex-1 px-6 py-3 rounded-lg font-semibold transition-colors flex items-center justify-center gap-2 ${processing || (!isCreditSale && !isComplete) || (isCreditSale && !selectedCustomer)
                                ? 'bg-gray-300 cursor-not-allowed'
                                : 'bg-green-600 hover:bg-green-700 text-white'
                                }`}
                        >
                            {processing ? (
                                'Procesando...'
                            ) : isCreditSale ? (
                                <>
                                    <CreditCard size={20} />
                                    Registrar Venta a Crédito
                                </>
                            ) : (
                                <>
                                    <CheckCircle size={20} />
                                    Confirmar Pago
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
