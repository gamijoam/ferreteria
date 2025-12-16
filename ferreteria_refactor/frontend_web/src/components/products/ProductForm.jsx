import { useState } from 'react';
import { X, Plus, Trash2 } from 'lucide-react';

const ProductForm = ({ isOpen, onClose, onSubmit }) => {
    const [activeTab, setActiveTab] = useState('info');
    const [formData, setFormData] = useState({
        name: '',
        sku: '',
        category: '',
        cost: 0,
        price: 0,
        margin: 0,
        unit: 'UNID',
        presentations: []
    });

    if (!isOpen) return null;

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        let newValue = value;

        // Auto-calculate margin/price logic could go here
        if (name === 'cost' || name === 'price') {
            newValue = parseFloat(value) || 0;
        }

        setFormData(prev => {
            const updated = { ...prev, [name]: newValue };
            if (name === 'cost' || name === 'price') {
                if (updated.cost > 0 && updated.price > 0) {
                    updated.margin = ((updated.price - updated.cost) / updated.cost) * 100;
                }
            }
            return updated;
        });
    };

    const handleAddPresentation = () => {
        // Simple logic to add a presentation, could be enhanced with a small sub-modal
        const type = window.confirm("¿Es Empaque (Saco, Caja) [OK] o Fracción (Gramo, Metro) [Cancel]?") ? 'packing' : 'fraction';
        const newPres = {
            id: Date.now(),
            name: type === 'packing' ? 'Saco/Caja' : 'Fracción',
            factor: type === 'packing' ? 50 : 0.001,
            type
        };
        setFormData(prev => ({
            ...prev,
            presentations: [...prev.presentations, newPres]
        }));
    };

    const removePresentation = (id) => {
        setFormData(prev => ({
            ...prev,
            presentations: prev.presentations.filter(p => p.id !== id)
        }));
    };

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b">
                    <h3 className="text-xl font-bold text-gray-800">Nuevo Producto</h3>
                    <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
                        <X size={24} />
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex border-b">
                    <button
                        className={`flex-1 p-3 font-medium ${activeTab === 'info' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                        onClick={() => setActiveTab('info')}
                    >
                        información
                    </button>
                    <button
                        className={`flex-1 p-3 font-medium ${activeTab === 'prices' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                        onClick={() => setActiveTab('prices')}
                    >
                        Precios
                    </button>
                    <button
                        className={`flex-1 p-3 font-medium ${activeTab === 'inventory' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                        onClick={() => setActiveTab('inventory')}
                    >
                        Inventario & Unidades
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto flex-1">
                    {activeTab === 'info' && (
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Nombre del Producto</label>
                                <input type="text" name="name" value={formData.name} onChange={handleInputChange} className="mt-1 block w-full border rounded-md p-2" placeholder="Ej: Cemento Gris" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">SKU / Código</label>
                                <input type="text" name="sku" value={formData.sku} onChange={handleInputChange} className="mt-1 block w-full border rounded-md p-2" placeholder="Ej: CEM-001" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Categoría</label>
                                <input type="text" name="category" value={formData.category} onChange={handleInputChange} className="mt-1 block w-full border rounded-md p-2" />
                            </div>
                        </div>
                    )}

                    {activeTab === 'prices' && (
                        <div className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Costo ($)</label>
                                    <input type="number" name="cost" value={formData.cost} onChange={handleInputChange} className="mt-1 block w-full border rounded-md p-2" />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Precio Venta ($)</label>
                                    <input type="number" name="price" value={formData.price} onChange={handleInputChange} className="mt-1 block w-full border rounded-md p-2" />
                                </div>
                            </div>
                            <div className="bg-blue-50 p-4 rounded-md">
                                <p className="text-blue-800 font-medium">Margen Calculado: {formData.margin.toFixed(2)}%</p>
                            </div>
                        </div>
                    )}

                    {activeTab === 'inventory' && (
                        <div className="space-y-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Unidad Base</label>
                                <select name="unit" value={formData.unit} onChange={handleInputChange} className="mt-1 block w-full border rounded-md p-2">
                                    <option value="UNID">Unidad (UNID)</option>
                                    <option value="KG">Kilogramos (KG)</option>
                                    <option value="MTR">Metros (MTR)</option>
                                </select>
                            </div>

                            <div className="border-t pt-4">
                                <div className="flex items-center justify-between mb-4">
                                    <h4 className="font-medium text-gray-800">Presentaciones Adicionales</h4>
                                    <button onClick={handleAddPresentation} className="text-sm bg-green-100 text-green-700 px-3 py-1 rounded-full flex items-center hover:bg-green-200">
                                        <Plus size={16} className="mr-1" /> Agregar
                                    </button>
                                </div>

                                {formData.presentations.length === 0 && (
                                    <p className="text-gray-500 text-sm italic">No hay presentaciones adicionales definidas.</p>
                                )}

                                <div className="space-y-3">
                                    {formData.presentations.map(pres => (
                                        <div key={pres.id} className="bg-gray-50 p-3 rounded border flex items-center justify-between">
                                            <div className="flex-1 grid grid-cols-3 gap-2">
                                                <input
                                                    type="text"
                                                    value={pres.name}
                                                    className="border rounded p-1 text-sm"
                                                    placeholder="Nombre (ej: Saco)"
                                                />
                                                <input
                                                    type="number"
                                                    value={pres.factor}
                                                    className="border rounded p-1 text-sm"
                                                    placeholder="Factor"
                                                />
                                                <div className="text-xs text-gray-600 flex items-center">
                                                    {pres.type === 'packing'
                                                        ? `1 ${pres.name} = ${pres.factor} ${formData.unit}`
                                                        : `${(1 / pres.factor)} ${pres.name} = 1 ${formData.unit}`}
                                                </div>
                                            </div>
                                            <button onClick={() => removePresentation(pres.id)} className="ml-2 text-red-500 hover:text-red-700">
                                                <Trash2 size={18} />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="p-4 border-t bg-gray-50 flex justify-end space-x-3">
                    <button onClick={onClose} className="px-4 py-2 text-gray-700 hover:text-gray-900 font-medium">Cancelar</button>
                    <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 font-medium">Guardar Producto</button>
                </div>
            </div>
        </div>
    );
};

export default ProductForm;
