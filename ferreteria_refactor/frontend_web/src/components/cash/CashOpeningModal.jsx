import { useState } from 'react';
import { Lock } from 'lucide-react';

const CashOpeningModal = ({ onOpen }) => {
    const [amount, setAmount] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!amount) return;
        onOpen(Number(amount));
    };

    return (
        <div className="fixed inset-0 bg-gray-900 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-md p-8 text-center">
                <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <Lock size={40} className="text-red-500" />
                </div>

                <h2 className="text-2xl font-bold text-gray-800 mb-2">Caja Cerrada</h2>
                <p className="text-gray-500 mb-6">Para acceder al Punto de Venta, debes abrir un nuevo turno de caja.</p>

                <form onSubmit={handleSubmit} className="text-left">
                    <div className="mb-6">
                        <label className="block text-sm font-bold text-gray-700 mb-2">Dinero Inicial en Caja ($)</label>
                        <input
                            type="number"
                            className="w-full text-xl p-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 outline-none"
                            placeholder="0.00"
                            value={amount}
                            onChange={(e) => setAmount(e.target.value)}
                            autoFocus
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg shadow transition-colors"
                    >
                        Abrir Turno
                    </button>
                </form>
            </div>
        </div>
    );
};

export default CashOpeningModal;
