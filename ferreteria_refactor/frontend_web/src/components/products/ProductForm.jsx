import { useState } from 'react';
import { X, Plus, Trash2 } from 'lucide-react';

import { useConfig } from '../../context/ConfigContext';

const ProductForm = ({ isOpen, onClose, onSubmit }) => {
    const { getActiveCurrencies, convertPrice, currencies } = useConfig();
    const anchorCurrency = currencies.find(c => c.is_anchor) || { symbol: '$' };

    const [activeTab, setActiveTab] = useState('info');
    const [formData, setFormData] = useState({
        name: '',
        sku: '',
        category: '',
        cost: 0,
        price: 0,
        margin: 0,
        unit: 'UNID',
        cost: 0,
        price: 0,
        margin: 0,
        unit: 'UNID',
        units: [] // New standard structure
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

    // Unit Management
    const handleAddUnit = () => {
        const type = window.confirm("¿Es Empaque (Saco, Caja) [OK] o Fracción (Gramo, Metro) [Cancel]?") ? 'packing' : 'fraction';
        const newUnit = {
            id: Date.now(),
            unit_name: type === 'packing' ? 'Caja' : 'Gramo',
            user_input: type === 'packing' ? 12 : 1000, // Visual number
            conversion_factor: 1, // Calculated later
            type: type, // packing | fraction
            barcode: '',
            price_usd: 0
        };
        setFormData(prev => ({
            ...prev,
            units: [...prev.units, newUnit]
        }));
    };

    const handleUnitChange = (id, field, value) => {
        setFormData(prev => ({
            ...prev,
            units: prev.units.map(u => {
                if (u.id !== id) return u;
                return { ...u, [field]: value };
            })
        }));
    };

    const removeUnit = (id) => {
        setFormData(prev => ({
            ...prev,
            units: prev.units.filter(u => u.id !== id)
        }));
    };

    const handleSubmit = () => {
        // Prepare Payload
        const payload = {
            name: formData.name,
            sku: formData.sku,
            category_id: parseInt(formData.category) || null, // Assuming category is ID now, or handle text if needed
            cost_price: parseFloat(formData.cost),
            price: parseFloat(formData.price),
            stock: 0, // Initial stock usually 0 or handled elsewhere
            // Convert UI units to Backend Schema
            units: formData.units.map(u => {
                let factor = parseFloat(u.user_input);
                if (u.type === 'fraction') {
                    // Example: 1000g = 1Kg. Factor = 1/1000 = 0.001
                    factor = factor !== 0 ? 1 / factor : 0;
                }
                return {
                    unit_name: u.unit_name,
                    conversion_factor: factor,
                    barcode: u.barcode,
                    price_usd: parseFloat(u.price_usd) || null,
                    is_default: false
                };
            })
        };

        console.log("Submitting Payload:", payload);
        onSubmit(payload);
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
                                    <label className="block text-sm font-medium text-gray-700">Costo ({anchorCurrency.symbol})</label>
                                    <div className="relative mt-1 rounded-md shadow-sm">
                                        <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                                            <span className="text-gray-500 sm:text-sm">{anchorCurrency.symbol}</span>
                                        </div>
                                        <input
                                            type="number"
                                            name="cost"
                                            value={formData.cost}
                                            onChange={handleInputChange}
                                            className="block w-full rounded-md border-gray-300 pl-7 p-2 focus:border-blue-500 focus:ring-blue-500 sm:text-sm border"
                                            placeholder="0.00"
                                        />
                                    </div>
                                    {/* Currency Helper */}
                                    <div className="mt-1 flex flex-col gap-0.5">
                                        {getActiveCurrencies().map(curr => (
                                            <span key={curr.id} className="text-xs text-gray-500">
                                                ≈ {convertPrice(formData.cost || 0, curr.symbol).toFixed(2)} {curr.symbol}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Precio Venta ({anchorCurrency.symbol})</label>
                                    <div className="relative mt-1 rounded-md shadow-sm">
                                        <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                                            <span className="text-gray-500 sm:text-sm">{anchorCurrency.symbol}</span>
                                        </div>
                                        <input
                                            type="number"
                                            name="price"
                                            value={formData.price}
                                            onChange={handleInputChange}
                                            className="block w-full rounded-md border-gray-300 pl-7 p-2 focus:border-blue-500 focus:ring-blue-500 sm:text-sm border"
                                            placeholder="0.00"
                                        />
                                    </div>
                                    {/* Currency Helper */}
                                    <div className="mt-1 flex flex-col gap-0.5">
                                        {getActiveCurrencies().map(curr => (
                                            <span key={curr.id} className="text-xs text-gray-500">
                                                ≈ {convertPrice(formData.price || 0, curr.symbol).toFixed(2)} {curr.symbol}
                                            </span>
                                        ))}
                                    </div>
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
                                    <h4 className="font-medium text-gray-800">Presentaciones / Unidades</h4>
                                    <button onClick={handleAddUnit} className="text-sm bg-green-100 text-green-700 px-3 py-1 rounded-full flex items-center hover:bg-green-200">
                                        <Plus size={16} className="mr-1" /> Agregar
                                    </button>
                                </div>

                                {formData.units.length === 0 && (
                                    <p className="text-gray-500 text-sm italic">No hay presentaciones adicionales definidas.</p>
                                )}

                                <div className="space-y-3">
                                    {formData.units.map(unit => (
                                        <div key={unit.id} className="bg-gray-50 p-3 rounded border flex flex-col gap-2">
                                            <div className="flex justify-between items-center">
                                                <span className="text-xs font-semibold uppercase text-gray-500">{unit.type === 'packing' ? 'Empaque (Contenedor)' : 'Fracción (Sub-unidad)'}</span>
                                                <button onClick={() => removeUnit(unit.id)} className="text-red-500 hover:text-red-700">
                                                    <Trash2 size={16} />
                                                </button>
                                            </div>
                                            <div className="grid grid-cols-4 gap-2">
                                                <div className="col-span-1">
                                                    <label className="text-[10px] text-gray-500 block">Nombre</label>
                                                    <input
                                                        type="text"
                                                        value={unit.unit_name}
                                                        onChange={(e) => handleUnitChange(unit.id, 'unit_name', e.target.value)}
                                                        className="border rounded p-1 text-sm w-full"
                                                        placeholder="Ej: Caja"
                                                    />
                                                </div>
                                                <div className="col-span-1">
                                                    <label className="text-[10px] text-gray-500 block">
                                                        {unit.type === 'packing' ? 'Contiene' : 'Equivale a 1/'}
                                                    </label>
                                                    <input
                                                        type="number"
                                                        value={unit.user_input}
                                                        onChange={(e) => handleUnitChange(unit.id, 'user_input', e.target.value)}
                                                        className="border rounded p-1 text-sm w-full"
                                                        placeholder="Cantidad"
                                                    />
                                                </div>
                                                <div className="col-span-1">
                                                    <label className="text-[10px] text-gray-500 block">Precio (Opcional)</label>
                                                    <input
                                                        type="number"
                                                        value={unit.price_usd}
                                                        onChange={(e) => handleUnitChange(unit.id, 'price_usd', e.target.value)}
                                                        className="border rounded p-1 text-sm w-full"
                                                        placeholder="$"
                                                    />
                                                </div>
                                                <div className="col-span-1">
                                                    <label className="text-[10px] text-gray-500 block">Código Barras</label>
                                                    <input
                                                        type="text"
                                                        value={unit.barcode}
                                                        onChange={(e) => handleUnitChange(unit.id, 'barcode', e.target.value)}
                                                        className="border rounded p-1 text-sm w-full"
                                                        placeholder="||||||"
                                                    />
                                                </div>
                                            </div>
                                            <div className="text-xs text-blue-600 bg-blue-50 p-1 rounded">
                                                {unit.type === 'packing'
                                                    ? `1 ${unit.unit_name} contiene ${unit.user_input} ${formData.unit}s`
                                                    : `1 ${formData.unit} equivale a ${unit.user_input} ${unit.unit_name}s`}
                                            </div>
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
                    <button onClick={handleSubmit} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 font-medium">Guardar Producto</button>
                </div>
            </div>
        </div>
    );
};

export default ProductForm;
