import { useState, useEffect } from 'react';
import { X, Save, AlertTriangle } from 'lucide-react';
import inventoryService from '../../services/inventoryService';

const AdjustmentModal = ({ isOpen, onClose, onSuccess }) => {
    const [step, setStep] = useState(1);
    const [searchTerm, setSearchTerm] = useState('');
    const [products, setProducts] = useState([]); // Mock or searched products
    const [selectedProduct, setSelectedProduct] = useState(null);

    const [adjustmentData, setAdjustmentData] = useState({
        type: 'ADJUSTMENT_IN', // ADJUSTMENT_IN, ADJUSTMENT_OUT, DAMAGED, INTERNAL_USE
        quantity: 1,
        unit: null, // Should hold the selected unit object { name, factor }
        reason: ''
    });

    const MOVEMENT_TYPES = [
        { value: 'ADJUSTMENT_IN', label: 'Entrada / Ajuste (+)', color: 'text-green-600' },
        { value: 'ADJUSTMENT_OUT', label: 'Salida / Ajuste (-)', color: 'text-red-600' },
        { value: 'DAMAGED', label: 'Merma / Dañado (-)', color: 'text-orange-600' },
        { value: 'INTERNAL_USE', label: 'Uso Interno (-)', color: 'text-blue-600' }
    ];

    // Mock search effect - Replace with API call in production
    useEffect(() => {
        if (searchTerm.length > 2) {
            // inventoryService.searchProducts(searchTerm).then(setProducts);
            // Mocking for UI dev:
            setProducts([
                {
                    id: 1,
                    name: 'Cemento Gris Portland',
                    sku: 'CEM-001',
                    base_unit: 'KG',
                    presentations: [
                        { name: 'Saco 50kg', factor: 50 },
                        { name: 'Saco 25kg', factor: 25 }
                    ]
                },
                { id: 2, name: 'Tubería PVC', sku: 'PLOM-55', base_unit: 'MTR', presentations: [] }
            ].filter(p => p.name.toLowerCase().includes(searchTerm.toLowerCase())));
        }
    }, [searchTerm]);

    const handleSelectProduct = (product) => {
        setSelectedProduct(product);
        // Default to base unit
        setAdjustmentData(prev => ({
            ...prev,
            unit: { name: product.base_unit, factor: 1 }
        }));
        setStep(2);
    };

    const handleSubmit = async () => {
        try {
            if (!selectedProduct || !adjustmentData.unit) return;

            const totalQuantity = Number(adjustmentData.quantity) * Number(adjustmentData.unit.factor);

            const payload = {
                product_id: selectedProduct.id,
                type: adjustmentData.type,
                quantity: totalQuantity, // Converting to base unit
                reason: adjustmentData.reason
            };

            console.log("Submitting Adjustment Payload:", payload); // For verification

            // await inventoryService.createAdjustment(payload);
            onSuccess();
            onClose();
        } catch (error) {
            console.error("Adjustment failed", error);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-lg overflow-hidden">
                <div className="flex items-center justify-between p-4 border-b">
                    <h3 className="text-xl font-bold text-gray-800">
                        {step === 1 ? 'Seleccionar Producto' : 'Detalles del Ajuste'}
                    </h3>
                    <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
                        <X size={24} />
                    </button>
                </div>

                <div className="p-6">
                    {step === 1 && (
                        <div>
                            <input
                                type="text"
                                placeholder="Buscar producto..."
                                className="w-full border rounded p-3 mb-4 focus:ring-2 focus:ring-blue-500 outline-none"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                autoFocus
                            />
                            <div className="max-h-60 overflow-y-auto space-y-2">
                                {products.length === 0 && searchTerm.length > 2 && (
                                    <p className="text-gray-500 text-center">No se encontraron productos.</p>
                                )}
                                {products.map(p => (
                                    <div
                                        key={p.id}
                                        onClick={() => handleSelectProduct(p)}
                                        className="p-3 border rounded hover:bg-blue-50 cursor-pointer transition-colors"
                                    >
                                        <div className="font-medium text-gray-800">{p.name}</div>
                                        <div className="text-sm text-gray-500">SKU: {p.sku}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {step === 2 && selectedProduct && (
                        <div className="space-y-4">
                            <div className="bg-gray-50 p-3 rounded border">
                                <span className="text-xs text-gray-500 uppercase">Producto Seleccionado</span>
                                <div className="font-bold text-gray-800">{selectedProduct.name}</div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Movimiento</label>
                                <select
                                    className="w-full border rounded p-2"
                                    value={adjustmentData.type}
                                    onChange={(e) => setAdjustmentData({ ...adjustmentData, type: e.target.value })}
                                >
                                    {MOVEMENT_TYPES.map(t => (
                                        <option key={t.value} value={t.value} className={t.color}>{t.label}</option>
                                    ))}
                                </select>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Unidad</label>
                                    <select
                                        className="w-full border rounded p-2"
                                        onChange={(e) => {
                                            const [name, factor] = e.target.value.split('|');
                                            setAdjustmentData({ ...adjustmentData, unit: { name, factor: Number(factor) } });
                                        }}
                                    >
                                        <option value={`${selectedProduct.base_unit}|1`}>{selectedProduct.base_unit} (Base)</option>
                                        {selectedProduct.presentations?.map((pres, idx) => (
                                            <option key={idx} value={`${pres.name}|${pres.factor}`}>
                                                {pres.name} (x{pres.factor} {selectedProduct.base_unit})
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Cantidad</label>
                                    <input
                                        type="number"
                                        min="1"
                                        className="w-full border rounded p-2"
                                        value={adjustmentData.quantity}
                                        onChange={(e) => setAdjustmentData({ ...adjustmentData, quantity: e.target.value })}
                                    />
                                </div>
                            </div>

                            <div className="bg-blue-50 p-2 text-sm text-blue-800 rounded">
                                <span className="font-bold">Total a ajustar:</span> {Number(adjustmentData.quantity) * (adjustmentData.unit?.factor || 1)} {selectedProduct.base_unit}
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Motivo / Nota</label>
                                <textarea
                                    className="w-full border rounded p-2 h-20"
                                    value={adjustmentData.reason}
                                    onChange={(e) => setAdjustmentData({ ...adjustmentData, reason: e.target.value })}
                                    placeholder="Explica la razón del ajuste..."
                                ></textarea>
                            </div>
                        </div>
                    )}
                </div>

                <div className="p-4 border-t bg-gray-50 flex justify-end space-x-3">
                    {step === 2 && (
                        <button onClick={() => setStep(1)} className="px-4 py-2 text-gray-600 hover:text-gray-800 font-medium">
                            Atrás
                        </button>
                    )}
                    <button onClick={onClose} className="px-4 py-2 text-gray-700 hover:text-gray-900 font-medium">
                        Cancelar
                    </button>

                    {step === 2 && (
                        <button
                            onClick={handleSubmit}
                            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 font-medium flex items-center"
                        >
                            <Save size={18} className="mr-2" />
                            Guardar Ajuste
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AdjustmentModal;
