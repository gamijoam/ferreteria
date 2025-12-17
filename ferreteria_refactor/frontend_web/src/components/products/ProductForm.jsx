import { useState, useEffect } from 'react';
import { X, Plus, Trash2, Package, DollarSign, Barcode, Tag, Layers, AlertTriangle } from 'lucide-react';
import { useConfig } from '../../context/ConfigContext';

const ProductForm = ({ isOpen, onClose, onSubmit, initialData = null }) => {
    const { getActiveCurrencies, convertPrice, currencies } = useConfig();
    const anchorCurrency = currencies.find(c => c.is_anchor) || { symbol: '$' };

    const [activeTab, setActiveTab] = useState('general');
    const [formData, setFormData] = useState({
        name: '',
        sku: '',
        category: '',
        cost: 0,
        price: 0,
        stock: 0,
        min_stock: 5,
        location: '',
        margin: 0,
        unit_type: 'UNID',
        units: []
    });

    // Reset or Populate on simple change
    useEffect(() => {
        if (isOpen) {
            if (initialData) {
                // Map backend units to frontend format
                const mappedUnits = (initialData.units || []).map(u => {
                    // Determine type based on conversion_factor
                    const isPacking = u.conversion_factor >= 1;
                    const type = isPacking ? 'packing' : 'fraction';

                    // Calculate user_input from conversion_factor
                    // For packing: factor is the number (e.g., 12 units)
                    // For fraction: factor is 1/n, so user_input is 1/factor (e.g., 1/0.001 = 1000)
                    const user_input = isPacking
                        ? u.conversion_factor
                        : (u.conversion_factor > 0 ? 1 / u.conversion_factor : 1000);

                    return {
                        id: u.id || Date.now() + Math.random(), // Use backend id or generate temp id
                        unit_name: u.unit_name,
                        user_input: user_input,
                        conversion_factor: u.conversion_factor,
                        type: type,
                        barcode: u.barcode || '',
                        price_usd: u.price_usd || 0
                    };
                });

                setFormData({
                    name: initialData.name || '',
                    sku: initialData.sku || '',
                    category: initialData.category_id || '',
                    cost: initialData.cost_price || 0,
                    price: initialData.price || 0,
                    stock: initialData.stock || 0,
                    min_stock: initialData.min_stock || 5,
                    location: initialData.location || '',
                    unit_type: initialData.unit_type || 'UNID',
                    margin: initialData.price > 0
                        ? ((initialData.price - initialData.cost_price) / initialData.price) * 100
                        : 0,
                    units: mappedUnits
                });
            } else {
                // Reset for new product
                setFormData({
                    name: '', sku: '', category: '',
                    cost: 0, price: 0, stock: 0, min_stock: 5, location: '',
                    margin: 0, unit_type: 'UNID', units: []
                });
            }
            setActiveTab('general');
        }
    }, [isOpen, initialData]);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        let newValue = value;

        if (['cost', 'price', 'stock', 'min_stock'].includes(name)) {
            newValue = parseFloat(value) || 0;
        }

        setFormData(prev => {
            const updated = { ...prev, [name]: newValue };
            if (name === 'cost' || name === 'price') {
                if (updated.price > 0) {
                    updated.margin = ((updated.price - updated.cost) / updated.price) * 100;
                } else {
                    updated.margin = 0;
                }
            }
            return updated;
        });
    };

    // ... Unit Management (keep existing helper functions)
    const handleAddUnit = (type) => {
        const newUnit = {
            id: Date.now(),
            unit_name: '',
            user_input: type === 'packing' ? 12 : 1000,
            conversion_factor: 1,
            type: type,
            barcode: '',
            price_usd: 0
        };
        setFormData(prev => ({ ...prev, units: [...prev.units, newUnit] }));
    };

    const handleUnitChange = (id, field, value) => {
        setFormData(prev => ({
            ...prev,
            units: prev.units.map(u => (u.id === id ? { ...u, [field]: value } : u))
        }));
    };

    const removeUnit = (id) => {
        setFormData(prev => ({ ...prev, units: prev.units.filter(u => u.id !== id) }));
    };

    const handleSubmit = () => {
        const payload = {
            name: formData.name,
            sku: formData.sku,
            category_id: parseInt(formData.category) || null,
            cost_price: parseFloat(formData.cost),
            price: parseFloat(formData.price),
            stock: parseFloat(formData.stock), // Now explicitly sending stock
            min_stock: parseFloat(formData.min_stock),
            unit_type: formData.unit_type,
            location: formData.location,
            units: formData.units.map(u => {
                let factor = parseFloat(u.user_input);
                if (u.type === 'fraction') factor = factor !== 0 ? 1 / factor : 0;
                return {
                    unit_name: u.unit_name,
                    conversion_factor: factor,
                    barcode: u.barcode,
                    price_usd: parseFloat(u.price_usd) || null,
                    is_default: false
                };
            })
        };
        onSubmit(payload);
    };

    if (!isOpen) return null;

    const TabButton = ({ id, label, icon: Icon }) => (
        <button
            onClick={() => setActiveTab(id)}
            className={`flex items-center px-6 py-4 font-medium transition-colors border-b-2 ${activeTab === id
                ? 'border-blue-600 text-blue-600 bg-blue-50/50'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                }`}
        >
            <Icon size={18} className="mr-2" />
            {label}
        </button>
    );

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
                {/* Header */}
                <div className="flex items-center justify-between p-5 border-b bg-gray-50">
                    <div>
                        <h3 className="text-2xl font-bold text-gray-800">
                            {initialData ? 'Editar Producto' : 'Nuevo Producto'}
                        </h3>
                        <p className="text-gray-500 text-sm mt-1">
                            Complete la información del inventario
                        </p>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-gray-200 rounded-full transition-colors text-gray-500">
                        <X size={24} />
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex border-b bg-white sticky top-0 z-10">
                    <TabButton id="general" label="General" icon={Barcode} />
                    <TabButton id="pricing" label="Precios & Stock" icon={DollarSign} />
                    <TabButton id="units" label="Presentaciones" icon={Layers} />
                </div>

                {/* Content */}
                <div className="p-8 overflow-y-auto flex-1 bg-gray-50/30">
                    {activeTab === 'general' && (
                        <div className="space-y-6 max-w-3xl mx-auto anime-fade-in">
                            <div className="grid grid-cols-2 gap-6">
                                <div className="col-span-2">
                                    <label className="block text-sm font-semibold text-gray-700 mb-1">Nombre del Producto <span className="text-red-500">*</span></label>
                                    <input
                                        type="text"
                                        name="name"
                                        value={formData.name}
                                        onChange={handleInputChange}
                                        className="w-full border-gray-300 rounded-lg shadow-sm focus:border-blue-500 focus:ring-blue-500 py-3 px-4 text-lg"
                                        placeholder="Ej: Cemento Gris Portland Tipo I"
                                        autoFocus
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-1">SKU / Código <span className="text-gray-400 font-normal">(Opcional)</span></label>
                                    <div className="relative">
                                        <Barcode className="absolute left-3 top-3 text-gray-400" size={18} />
                                        <input
                                            type="text"
                                            name="sku"
                                            value={formData.sku}
                                            onChange={handleInputChange}
                                            className="w-full pl-10 border-gray-300 rounded-lg shadow-sm focus:border-blue-500 focus:ring-blue-500 py-2.5"
                                            placeholder="SCAN-001"
                                        />
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-1">Categoría</label>
                                    <div className="relative">
                                        <Tag className="absolute left-3 top-3 text-gray-400" size={18} />
                                        <input
                                            type="text"
                                            name="category"
                                            value={formData.category}
                                            onChange={handleInputChange}
                                            className="w-full pl-10 border-gray-300 rounded-lg shadow-sm focus:border-blue-500 focus:ring-blue-500 py-2.5"
                                            placeholder="Materiales, Herramientas..."
                                        />
                                    </div>
                                </div>
                                <div className="col-span-2">
                                    <label className="block text-sm font-semibold text-gray-700 mb-1">Ubicación en Almacén</label>
                                    <input
                                        type="text"
                                        name="location"
                                        value={formData.location}
                                        onChange={handleInputChange}
                                        className="w-full border-gray-300 rounded-lg shadow-sm focus:border-blue-500 focus:ring-blue-500 py-2.5"
                                        placeholder="Pasillo 4, Estante B"
                                    />
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'pricing' && (
                        <div className="space-y-8 max-w-3xl mx-auto anime-fade-in">
                            {/* Stock Section - Prominent */}
                            <div className="bg-blue-50 rounded-xl p-6 border border-blue-100">
                                <h4 className="text-lg font-bold text-blue-800 mb-4 flex items-center">
                                    <Package className="mr-2" size={20} /> Inventario Inicial
                                </h4>
                                <div className="grid grid-cols-2 gap-6">
                                    <div>
                                        <label className="block text-sm font-bold text-blue-900 mb-1">Stock Actual (Cantidad Real)</label>
                                        <input
                                            type="number"
                                            name="stock"
                                            value={formData.stock}
                                            onChange={handleInputChange}
                                            className="w-full border-blue-200 rounded-lg shadow-sm focus:border-blue-500 focus:ring-blue-500 py-3 text-xl font-bold text-gray-800 bg-white"
                                            placeholder="0"
                                        />
                                        <p className="text-xs text-blue-600 mt-1">Este valor actualizará el inventario inmediatamente.</p>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-semibold text-gray-700 mb-1">Stock Mínimo (Alerta)</label>
                                        <input
                                            type="number"
                                            name="min_stock"
                                            value={formData.min_stock}
                                            onChange={handleInputChange}
                                            className="w-full border-gray-300 rounded-lg shadow-sm focus:border-blue-500 focus:ring-blue-500 py-3"
                                            placeholder="5.0"
                                        />
                                    </div>
                                </div>
                            </div>

                            <hr className="border-gray-200" />

                            {/* Pricing Section */}
                            <div className="grid grid-cols-2 gap-8">
                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-1">Costo de Compra ({anchorCurrency.symbol})</label>
                                    <div className="relative">
                                        <span className="absolute left-3 top-3 text-gray-500 font-bold">{anchorCurrency.symbol}</span>
                                        <input
                                            type="number"
                                            name="cost"
                                            value={formData.cost}
                                            onChange={handleInputChange}
                                            className="w-full pl-8 border-gray-300 rounded-lg shadow-sm focus:border-blue-500 focus:ring-blue-500 py-3 text-lg"
                                            placeholder="0.00"
                                        />
                                    </div>
                                    <div className="mt-2 text-xs text-gray-500 space-y-1">
                                        {getActiveCurrencies().map(curr => !curr.is_anchor && (
                                            <div key={curr.id}>≈ {convertPrice(formData.cost, curr.symbol).toFixed(2)} {curr.symbol}</div>
                                        ))}
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-sm font-bold text-green-700 mb-1">Precio de Venta ({anchorCurrency.symbol})</label>
                                    <div className="relative">
                                        <span className="absolute left-3 top-3 text-gray-500 font-bold">{anchorCurrency.symbol}</span>
                                        <input
                                            type="number"
                                            name="price"
                                            value={formData.price}
                                            onChange={handleInputChange}
                                            className="w-full pl-8 border-green-300 rounded-lg shadow-sm focus:border-green-500 focus:ring-green-500 py-3 text-lg font-bold text-gray-900 bg-green-50/30"
                                            placeholder="0.00"
                                        />
                                    </div>
                                    <div className="mt-2 text-xs text-gray-500 space-y-1">
                                        {getActiveCurrencies().map(curr => !curr.is_anchor && (
                                            <div key={curr.id}>≈ {convertPrice(formData.price, curr.symbol).toFixed(2)} {curr.symbol}</div>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            <div className={`p-4 rounded-lg flex items-center justify-between ${formData.margin < 0 ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'}`}>
                                <span className="font-semibold">Margen de Ganancia:</span>
                                <span className="text-2xl font-bold">{formData.margin.toFixed(2)}%</span>
                            </div>
                        </div>
                    )}

                    {activeTab === 'units' && (
                        <div className="space-y-8 max-w-3xl mx-auto anime-fade-in relative">
                            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                                <label className="block text-sm font-bold text-gray-800 mb-2">Unidad Base del Producto</label>
                                <p className="text-sm text-gray-500 mb-4">¿Cómo se vende este producto principalmente?</p>
                                <select
                                    name="unit_type"
                                    value={formData.unit_type}
                                    onChange={handleInputChange}
                                    className="w-full border-gray-300 rounded-lg shadow-sm focus:border-blue-500 focus:ring-blue-500 py-3"
                                >
                                    <option value="UNID">Unidad (Pieza)</option>
                                    <option value="KG">Kilogramos (Peso)</option>
                                    <option value="MTR">Metros (Longitud)</option>
                                    <option value="LTR">Litros (Volumen)</option>
                                    <option value="SERV">Servicio</option>
                                </select>
                            </div>

                            <div className="flex items-center justify-between mt-8 mb-4">
                                <div>
                                    <h4 className="text-lg font-bold text-gray-800">Presentaciones Adicionales</h4>
                                    <p className="text-xs text-gray-500">Agrega unidades alternas de venta</p>
                                </div>
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => handleAddUnit('fraction')}
                                        className="bg-orange-50 text-orange-600 hover:bg-orange-100 px-4 py-2 rounded-full font-medium flex items-center transition-colors text-sm"
                                    >
                                        <Plus size={16} className="mr-1" /> Fracción
                                    </button>
                                    <button
                                        onClick={() => handleAddUnit('packing')}
                                        className="bg-blue-50 text-blue-600 hover:bg-blue-100 px-4 py-2 rounded-full font-medium flex items-center transition-colors text-sm"
                                    >
                                        <Plus size={16} className="mr-1" /> Empaque
                                    </button>
                                </div>
                            </div>

                            {formData.units.length === 0 ? (
                                <div className="text-center py-10 bg-gray-50 rounded-xl border-dashed border-2 border-gray-200">
                                    <Layers className="mx-auto text-gray-300 mb-2" size={48} />
                                    <p className="text-gray-500 font-medium">No hay presentaciones adicionales</p>
                                    <p className="text-xs text-gray-400">Solo se venderá por {formData.unit_type}</p>
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    {formData.units.map(unit => (
                                        <div key={unit.id} className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow relative group">
                                            <button
                                                onClick={() => removeUnit(unit.id)}
                                                className="absolute top-4 right-4 text-gray-300 hover:text-red-500 transition-colors"
                                            >
                                                <Trash2 size={18} />
                                            </button>

                                            <div className="flex items-center gap-3 mb-4">
                                                <span className={`px-2 py-1 text-[10px] font-bold uppercase rounded tracking-wider ${unit.type === 'packing' ? 'bg-purple-100 text-purple-700' : 'bg-orange-100 text-orange-700'}`}>
                                                    {unit.type === 'packing' ? 'Empaque' : 'Fracción'}
                                                </span>
                                                <h5 className="font-bold text-gray-800 text-lg">{unit.unit_name || 'Nueva Unidad'}</h5>
                                            </div>

                                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                                <div>
                                                    <label className="block text-[10px] font-bold text-gray-500 uppercase mb-1">Nombre Unidad</label>
                                                    <input
                                                        type="text"
                                                        value={unit.unit_name}
                                                        onChange={(e) => handleUnitChange(unit.id, 'unit_name', e.target.value)}
                                                        className="w-full border-gray-200 rounded p-2 text-sm focus:border-blue-500 focus:ring-blue-500"
                                                        placeholder="Caja, Bulk..."
                                                    />
                                                </div>
                                                <div>
                                                    <label className="block text-[10px] font-bold text-gray-500 uppercase mb-1">
                                                        {unit.type === 'packing' ? `Contiene (x ${formData.unit_type})` : `Equivale a (1/${formData.unit_type})`}
                                                    </label>
                                                    <input
                                                        type="number"
                                                        value={unit.user_input}
                                                        onChange={(e) => handleUnitChange(unit.id, 'user_input', e.target.value)}
                                                        className="w-full border-gray-200 rounded p-2 text-sm focus:border-blue-500 focus:ring-blue-500 font-medium"
                                                        placeholder="Cantidad"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="block text-[10px] font-bold text-gray-500 uppercase mb-1">Precio Específico ($)</label>
                                                    <input
                                                        type="number"
                                                        value={unit.price_usd}
                                                        onChange={(e) => handleUnitChange(unit.id, 'price_usd', e.target.value)}
                                                        className="w-full border-gray-200 rounded p-2 text-sm focus:border-green-500 focus:ring-green-500 text-green-700 font-bold"
                                                        placeholder="Opcional"
                                                    />
                                                </div>
                                                <div className="col-span-3">
                                                    <label className="block text-[10px] font-bold text-gray-500 uppercase mb-1">Código de Barras</label>
                                                    <input
                                                        type="text"
                                                        value={unit.barcode}
                                                        onChange={(e) => handleUnitChange(unit.id, 'barcode', e.target.value)}
                                                        className="w-full border-gray-200 rounded p-2 text-sm text-gray-600 font-mono bg-gray-50"
                                                        placeholder="Escanea el código de la caja/unidad..."
                                                    />
                                                </div>
                                            </div>

                                            <div className="mt-3 text-xs text-blue-600 bg-blue-50 rounded px-3 py-2 flex items-center">
                                                <AlertTriangle size={12} className="mr-1" />
                                                {unit.type === 'packing'
                                                    ? `Una ${unit.unit_name || 'unidad'} contiene ${unit.user_input} ${formData.unit_type}s`
                                                    : `Un ${formData.unit_type} equivale a ${unit.user_input} ${unit.unit_name}s`}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
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
