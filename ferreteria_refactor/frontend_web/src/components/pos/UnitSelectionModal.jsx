import { Package, Box } from 'lucide-react';

const UnitSelectionModal = ({ isOpen, onClose, product, onSelect }) => {
    if (!isOpen || !product) return null;

    // Base unit option
    const baseOption = {
        name: product.unit || 'UNID',
        price_usd: product.price,
        factor: 1,
        is_base: true
    };

    // Combine base with presentations
    const options = [baseOption, ...(product.presentations || [])];

    return (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 backdrop-blur-sm">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden transform transition-all">
                <div className="bg-slate-800 p-4 text-white text-center">
                    <h3 className="text-xl font-bold">¿Qué vas a vender?</h3>
                    <p className="text-slate-300 text-sm mt-1">{product.name}</p>
                </div>

                <div className="p-6 grid gap-4">
                    {options.map((opt, idx) => (
                        <button
                            key={idx}
                            onClick={() => { onSelect(opt); onClose(); }}
                            className="group relative flex items-center justify-between p-4 border-2 border-slate-200 rounded-lg hover:border-blue-600 hover:bg-blue-50 transition-all"
                        >
                            <div className="flex items-center space-x-4">
                                <div className={`p-3 rounded-full ${opt.is_base ? 'bg-orange-100 text-orange-600' : 'bg-purple-100 text-purple-600'}`}>
                                    {opt.is_base ? <Package size={24} /> : <Box size={24} />}
                                </div>
                                <div className="text-left">
                                    <div className="font-bold text-gray-800 text-lg">{opt.name}</div>
                                    <div className="text-xs text-gray-500">Factor: {opt.factor}</div>
                                </div>
                            </div>
                            <div className="text-right">
                                <div className="font-bold text-blue-600 text-xl">${opt.price_usd?.toFixed(2)}</div>
                            </div>
                        </button>
                    ))}
                </div>

                <div className="p-4 bg-gray-50 text-center">
                    <button onClick={onClose} className="text-gray-500 hover:text-gray-700 underline">Cancelar</button>
                </div>
            </div>
        </div>
    );
};

export default UnitSelectionModal;
