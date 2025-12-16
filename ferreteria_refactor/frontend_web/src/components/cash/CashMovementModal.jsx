import { useState } from 'react';
import { X, DollarSign } from 'lucide-react';
import cashService from '../../services/cashService';

const CashMovementModal = ({ isOpen, onClose, onSuccess }) => {
    const [type, setType] = useState('EXPENSE'); // EXPENSE or WITHDRAWAL
    const [amount, setAmount] = useState('');
    const [reason, setReason] = useState('');

    if (!isOpen) return null;

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            // await cashService.addMovement({ type, amount, reason });
            alert("Movimiento Registrado");
            onSuccess && onSuccess();
            onClose();
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-sm overflow-hidden">
                <div className="flex justify-between items-center p-4 border-b">
                    <h3 className="font-bold text-gray-800">Registrar Movimiento</h3>
                    <button onClick={onClose}><X size={20} className="text-gray-500" /></button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
                        <div className="grid grid-cols-2 gap-2">
                            <button
                                type="button"
                                onClick={() => setType('EXPENSE')}
                                className={`py-2 rounded border text-sm font-medium ${type === 'EXPENSE' ? 'bg-orange-100 border-orange-500 text-orange-700' : 'bg-gray-50 border-gray-200'}`}
                            >
                                Gasto
                            </button>
                            <button
                                type="button"
                                onClick={() => setType('WITHDRAWAL')}
                                className={`py-2 rounded border text-sm font-medium ${type === 'WITHDRAWAL' ? 'bg-red-100 border-red-500 text-red-700' : 'bg-gray-50 border-gray-200'}`}
                            >
                                Retiro
                            </button>
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Monto ($)</label>
                        <div className="relative">
                            <DollarSign size={16} className="absolute left-3 top-3 text-gray-400" />
                            <input
                                type="number"
                                value={amount}
                                onChange={(e) => setAmount(e.target.value)}
                                className="w-full pl-9 p-2 border rounded focus:ring-1 focus:ring-blue-500 outline-none"
                                placeholder="0.00"
                                required
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Motivo</label>
                        <textarea
                            value={reason}
                            onChange={(e) => setReason(e.target.value)}
                            className="w-full p-2 border rounded focus:ring-1 focus:ring-blue-500 outline-none"
                            rows="3"
                            placeholder="Ej: Pago de almuerzo..."
                            required
                        ></textarea>
                    </div>

                    <button
                        type="submit"
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 rounded shadow"
                    >
                        Guardar
                    </button>
                </form>
            </div>
        </div>
    );
};

export default CashMovementModal;
