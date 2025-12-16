import { useState, useEffect } from 'react';
import { Trash2, Save, X } from 'lucide-react';

const EditItemModal = ({ isOpen, onClose, item, onUpdate, onDelete }) => {
    const [quantity, setQuantity] = useState(1);

    useEffect(() => {
        if (item) setQuantity(item.quantity);
    }, [item]);

    if (!isOpen || !item) return null;

    return (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-sm p-6">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-bold text-gray-800">Editar Cantidad</h3>
                    <button onClick={onClose}><X className="text-gray-400" /></button>
                </div>

                <div className="text-center mb-6">
                    <h4 className="font-medium text-gray-700">{item.name}</h4>
                    <span className="text-sm bg-blue-100 text-blue-700 px-2 py-0.5 rounded">{item.unit_name}</span>
                </div>

                <div className="flex justify-center mb-8">
                    <input
                        type="number"
                        className="text-center text-4xl font-bold border-b-2 border-blue-500 w-32 focus:outline-none"
                        value={quantity}
                        onChange={(e) => setQuantity(Number(e.target.value))}
                        autoFocus
                    />
                </div>

                <div className="flex gap-3">
                    <button
                        onClick={() => { onDelete(item.id); onClose(); }}
                        className="flex-1 bg-red-100 text-red-600 py-3 rounded-lg font-bold hover:bg-red-200 flex justify-center items-center"
                    >
                        <Trash2 size={20} className="mr-2" /> Eliminar
                    </button>
                    <button
                        onClick={() => { onUpdate(item.id, quantity); onClose(); }}
                        className="flex-[2] bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700 flex justify-center items-center"
                    >
                        <Save size={20} className="mr-2" /> Actualizar
                    </button>
                </div>
            </div>
        </div>
    );
};

export default EditItemModal;
