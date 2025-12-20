import { useState, useEffect } from 'react';
import { X, Plus, Trash2, Package, DollarSign, Barcode, Tag, Layers, AlertTriangle, AlertCircle, Coins } from 'lucide-react';
import { useConfig } from '../../context/ConfigContext';
import apiClient from '../../config/axios';
import ProductUnitManager from './ProductUnitManager';
import ComboManager from './ComboManager';

const ProductForm = ({ isOpen, onClose, onSubmit, initialData = null }) => {
    const { getActiveCurrencies, convertPrice, currencies } = useConfig();
    const anchorCurrency = currencies.find(c => c.is_anchor) || { symbol: '$' };

    const [activeTab, setActiveTab] = useState('general');
    const [categories, setCategories] = useState([]);
    const [exchangeRates, setExchangeRates] = useState([]);
    const [formData, setFormData] = useState({
        name: '',
        sku: '',
        category_id: null,
        cost: 0,
        price: 0,
        stock: 0,
        min_stock: 5,
        location: '',
        margin: 0,
        unit_type: 'UNID',
        exchange_rate_id: null,
        is_combo: false,  // NEW: Combo flag
        units: [],
        combo_items: []  // NEW: Combo components
    });

    // Reset or Populate on simple change
    useEffect(() => {
        if (isOpen) {
            // Fetch categories
            fetchCategories();
            // Fetch exchange rates
            fetchExchangeRates();

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
                        id: u.id || Date.now() + Math.random(),
                        unit_name: u.unit_name,
                        user_input: user_input,
                        conversion_factor: u.conversion_factor,
                        type: type,
                        barcode: u.barcode || '',
                        price_usd: u.price_usd || 0,
                        exchange_rate_id: u.exchange_rate_id || null  // NEW
                    };
                });

                setFormData({
                    name: initialData.name || '',
                    sku: initialData.sku || '',
                    category_id: initialData.category_id || null,
                    cost: initialData.cost_price || 0,
                    price: initialData.price || 0,
                    stock: initialData.stock || 0,
                    min_stock: initialData.min_stock || 5,
                    location: initialData.location || '',
                    unit_type: initialData.unit_type || 'UNID',
                    margin: initialData.price > 0
                        ? ((initialData.price - initialData.cost_price) / initialData.price) * 100
                        : 0,
                    exchange_rate_id: initialData.exchange_rate_id || null,
                    is_combo: initialData.is_combo || false,  // NEW
                    units: mappedUnits,
                    combo_items: initialData.combo_items || []  // NEW
                });
            } else {
                // Reset for new product
                setFormData({
                    name: '', sku: '', category_id: null,
                    cost: 0, price: 0, stock: 0, min_stock: 5, location: '',
                    margin: 0, unit_type: 'UNID', exchange_rate_id: null,
                    is_combo: false, units: [], combo_items: []
                });
            }
            setActiveTab('general');
        }
    }, [isOpen, initialData]);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        let newValue = value;

        // For numeric fields, allow empty string (for better UX while typing)
        // Convert to number only if value is not empty
        if (['cost', 'price', 'stock', 'min_stock'].includes(name)) {
            newValue = value === '' ? '' : parseFloat(value) || 0;
        }

        setFormData(prev => {
            const updated = { ...prev, [name]: newValue };
            if (name === 'cost' || name === 'price') {
                const cost = typeof updated.cost === 'number' ? updated.cost : parseFloat(updated.cost) || 0;
                const price = typeof updated.price === 'number' ? updated.price : parseFloat(updated.price) || 0;
                if (price > 0) {
                    updated.margin = ((price - cost) / price) * 100;
                } else {
                    updated.margin = 0;
                }
            }
            return updated;
        });
    };

    const fetchCategories = async () => {
        try {
            const response = await apiClient.get('/categories');
            setCategories(response.data);
        } catch (error) {
            console.error('Error fetching categories:', error);
        }
    };

    const fetchExchangeRates = async () => {
        try {
            const response = await apiClient.get('/config/exchange-rates', {
                params: { is_active: true }
            });
            setExchangeRates(response.data);
        } catch (error) {
            console.error('Error fetching exchange rates:', error);
        }
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
        // Validation
        if (!formData.name.trim()) {
            alert('El nombre del producto es obligatorio');
            return;
        }
        if (parseFloat(formData.price) <= 0 || isNaN(parseFloat(formData.price))) {
            alert('El precio debe ser mayor a 0');
            return;
        }
        if (isNaN(parseFloat(formData.stock))) {
            alert('El stock debe ser un número válido');
            return;
        }

        const payload = {
            name: formData.name,
            sku: formData.sku,
            category_id: parseInt(formData.category_id) || null,
            cost_price: parseFloat(formData.cost) || 0,
            price: parseFloat(formData.price),
            stock: parseFloat(formData.stock) || 0,
            min_stock: parseFloat(formData.min_stock) || 0,
            unit_type: formData.unit_type,
            location: formData.location,
            exchange_rate_id: formData.exchange_rate_id ? parseInt(formData.exchange_rate_id) : null,  // Parse as integer
            is_combo: formData.is_combo,  // NEW: Combo flag
            units: formData.units.map(u => {
                let factor = parseFloat(u.user_input);
                if (u.type === 'fraction') factor = factor !== 0 ? 1 / factor : 0;
                return {
                    unit_name: u.unit_name,
                    conversion_factor: factor,
                    barcode: u.barcode,
                    price_usd: parseFloat(u.price_usd) || null,
                    is_default: false,
                    exchange_rate_id: u.exchange_rate_id ? parseInt(u.exchange_rate_id) : null  // Parse as integer
                };
            }),
            combo_items: formData.is_combo ? formData.combo_items.map(ci => ({  // NEW: Combo items
                child_product_id: ci.child_product_id,
                quantity: parseFloat(ci.quantity)
            })) : []
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
                    <TabButton id="combos" label="Combos" icon={Package} />
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
                                        <select
                                            name="category_id"
                                            value={formData.category_id || ''}
                                            onChange={handleInputChange}
                                            className="w-full pl-10 border-gray-300 rounded-lg shadow-sm focus:border-blue-500 focus:ring-blue-500 py-2.5"
                                        >
                                            <option value="">-- Sin categoría --</option>
                                            {categories.filter(cat => !cat.parent_id).map(parent => (
                                                <optgroup key={parent.id} label={parent.name}>
                                                    <option value={parent.id}>{parent.name}</option>
                                                    {categories.filter(child => child.parent_id === parent.id).map(child => (
                                                        <option key={child.id} value={child.id}>
                                                            └─ {child.name}
                                                        </option>
                                                    ))}
                                                </optgroup>
                                            ))}
                                            {/* Standalone categories without children */}
                                            {categories.filter(cat => !cat.parent_id && !categories.some(c => c.parent_id === cat.id)).length === 0 && categories.filter(cat => !cat.parent_id).map(cat => (
                                                <option key={cat.id} value={cat.id}>{cat.name}</option>
                                            ))}
                                        </select>
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

                                {/* Combo Checkbox */}
                                <div className="col-span-2 mt-4">
                                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                                        <label className="flex items-center cursor-pointer">
                                            <input
                                                type="checkbox"
                                                checked={formData.is_combo}
                                                onChange={(e) => setFormData({ ...formData, is_combo: e.target.checked })}
                                                className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                            />
                                            <span className="ml-3 text-sm font-medium text-gray-900">
                                                🎁 Este producto es un Combo/Bundle
                                            </span>
                                        </label>
                                        <p className="text-xs text-gray-600 mt-2 ml-8">
                                            Los combos son productos virtuales compuestos por otros productos.
                                            El stock se descuenta de los componentes, no del combo.
                                        </p>
                                    </div>
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

                                </div>
                            </div>

                            {/* NEW: Exchange Rate Selector */}
                            <div className="bg-purple-50 rounded-xl p-6 border border-purple-100">
                                <h4 className="text-lg font-bold text-purple-800 mb-2 flex items-center">
                                    <Coins className="mr-2" size={20} /> Perfil de Tasa de Cambio
                                </h4>
                                <p className="text-sm text-purple-600 mb-4">Selecciona qué tasa usar para calcular precios en otras monedas</p>

                                <select
                                    name="exchange_rate_id"
                                    value={formData.exchange_rate_id || ''}
                                    onChange={handleInputChange}
                                    className="w-full border-purple-200 rounded-lg shadow-sm focus:border-purple-500 focus:ring-purple-500 py-3 bg-white"
                                >
                                    <option value="">Usar Predeterminada (por moneda)</option>
                                    {exchangeRates.map(rate => (
                                        <option key={rate.id} value={rate.id}>
                                            {rate.name} - {rate.currency_code} ({Number(rate.rate).toFixed(2)})
                                        </option>
                                    ))}
                                </select>

                                {formData.exchange_rate_id && formData.price > 0 && (
                                    <div className="mt-4 p-3 bg-white rounded-lg border border-purple-200">
                                        <p className="text-xs font-semibold text-purple-700 mb-2">Vista Previa de Precio:</p>
                                        {(() => {
                                            const selectedRate = exchangeRates.find(r => r.id === parseInt(formData.exchange_rate_id));
                                            if (selectedRate) {
                                                const convertedPrice = formData.price * Number(selectedRate.rate);
                                                return (
                                                    <p className="text-lg font-bold text-purple-900">
                                                        {convertedPrice.toFixed(2)} {selectedRate.currency_symbol}
                                                        <span className="text-sm font-normal text-purple-600 ml-2">
                                                            (usando {selectedRate.name})
                                                        </span>
                                                    </p>
                                                );
                                            }
                                            return null;
                                        })()}
                                    </div>
                                )}
                            </div>

                            <div className={`p-4 rounded-lg flex items-center justify-between ${formData.margin < 0 ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'}`}>
                                <span className="font-semibold">Margen de Ganancia:</span>
                                <span className="text-2xl font-bold">{formData.margin.toFixed(2)}%</span>
                            </div>
                        </div>
                    )}

                    {activeTab === 'units' && (
                        <ProductUnitManager
                            units={formData.units}
                            onUnitsChange={(newUnits) => setFormData(prev => ({ ...prev, units: newUnits }))}
                            baseUnitType={formData.unit_type}
                            basePrice={formData.price}
                            exchangeRates={exchangeRates}
                            productExchangeRateId={formData.exchange_rate_id}
                        />
                    )}

                    {activeTab === 'combos' && (
                        <div className="space-y-6 max-w-4xl mx-auto anime-fade-in">
                            {/* Header */}
                            <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-6 border border-purple-200">
                                <h4 className="text-xl font-bold text-purple-900 mb-2 flex items-center">
                                    <Package className="mr-2" size={24} />
                                    Gestión de Combos/Bundles
                                </h4>
                                <p className="text-sm text-purple-700">
                                    Define los productos que componen este combo y sus cantidades.
                                </p>
                            </div>

                            {/* Combo Toggle */}
                            {!formData.is_combo && (
                                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
                                    <AlertCircle className="mx-auto mb-3 text-yellow-600" size={48} />
                                    <p className="text-gray-700 mb-4">
                                        Este producto no está marcado como combo.
                                    </p>
                                    <button
                                        type="button"
                                        onClick={() => setFormData({ ...formData, is_combo: true })}
                                        className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
                                    >
                                        Convertir en Combo
                                    </button>
                                </div>
                            )}

                            {/* Combo Manager */}
                            {formData.is_combo && (
                                <ComboManager
                                    productId={initialData?.id}
                                    initialComboItems={formData.combo_items || []}
                                    onChange={(items) => setFormData({ ...formData, combo_items: items })}
                                />
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
