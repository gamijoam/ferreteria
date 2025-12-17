import { useState } from 'react';
import { Package, Tag, Trash2, AlertCircle, Plus, DollarSign, TrendingUp } from 'lucide-react';

/**
 * ProductUnitManager - Dedicated component for managing product units/presentations
 * Provides an intuitive wizard interface with visual feedback
 */
const ProductUnitManager = ({
    units = [],
    onUnitsChange,
    baseUnitType = 'UNID',
    basePrice = 0,
    exchangeRates = [],
    productExchangeRateId = null
}) => {
    // Wizard state
    const [wizardData, setWizardData] = useState({
        unit_name: '',
        type: 'packing', // 'packing' or 'fraction'
        user_input: '',
        price_usd: '',
        barcode: '',
        exchange_rate_id: null
    });

    const resetWizard = () => {
        setWizardData({
            unit_name: '',
            type: 'packing',
            user_input: '',
            price_usd: '',
            barcode: '',
            exchange_rate_id: null
        });
    };

    const handleWizardChange = (field, value) => {
        setWizardData(prev => ({ ...prev, [field]: value }));
    };

    const handleAddUnit = () => {
        // Validation
        if (!wizardData.unit_name.trim()) {
            alert('Por favor ingresa un nombre para la presentación');
            return;
        }
        if (!wizardData.user_input || parseFloat(wizardData.user_input) <= 0) {
            alert('Por favor ingresa una cantidad válida');
            return;
        }

        // Calculate conversion factor
        let conversionFactor;
        if (wizardData.type === 'packing') {
            conversionFactor = parseFloat(wizardData.user_input);
        } else {
            conversionFactor = 1 / parseFloat(wizardData.user_input);
        }

        const newUnit = {
            id: Date.now(), // Temporary ID for local state
            unit_name: wizardData.unit_name.trim(),
            type: wizardData.type,
            user_input: parseFloat(wizardData.user_input),
            conversion_factor: conversionFactor,
            price_usd: wizardData.price_usd ? parseFloat(wizardData.price_usd) : 0,
            barcode: wizardData.barcode.trim(),
            exchange_rate_id: wizardData.exchange_rate_id || null
        };

        // Add to units array
        onUnitsChange([...units, newUnit]);
        resetWizard();
    };

    const handleDeleteUnit = (unitId) => {
        // CRITICAL FIX: Filter out the unit by ID
        const updatedUnits = units.filter(u => u.id !== unitId);
        onUnitsChange(updatedUnits);
    };

    // Calculate displayed price for a unit
    const calculateDisplayPrice = (unit) => {
        if (unit.price_usd && unit.price_usd > 0) {
            return unit.price_usd;
        }
        return basePrice * unit.conversion_factor;
    };

    // Get exchange rate name
    const getExchangeRateName = (rateId) => {
        if (!rateId) return 'Heredar del Producto';
        const rate = exchangeRates.find(r => r.id === rateId);
        return rate ? `${rate.name} (${rate.currency_code})` : 'Tasa Desconocida';
    };

    // Visual formula text
    const getFormulaText = () => {
        if (!wizardData.user_input || parseFloat(wizardData.user_input) <= 0) {
            return 'Ingresa una cantidad para ver la fórmula';
        }

        const quantity = parseFloat(wizardData.user_input);
        const unitName = wizardData.unit_name || 'Presentación';

        if (wizardData.type === 'packing') {
            return `Esto significa que 1 ${unitName} descontará ${quantity} ${baseUnitType} del inventario.`;
        } else {
            return `Esto significa que 1 ${baseUnitType} equivale a ${quantity} ${unitName}s.`;
        }
    };

    return (
        <div className="space-y-6">
            {/* Wizard Panel */}
            <div className="bg-gradient-to-br from-indigo-50 to-purple-50 p-6 rounded-2xl border-2 border-indigo-200 shadow-sm">
                <h3 className="text-lg font-black text-indigo-900 mb-4 flex items-center gap-2">
                    <Plus className="text-indigo-600" size={22} />
                    Crear Nueva Presentación
                </h3>

                <div className="space-y-4">
                    {/* Unit Name */}
                    <div>
                        <label className="block text-sm font-bold text-gray-700 mb-2">
                            Nombre de la Presentación
                        </label>
                        <input
                            type="text"
                            value={wizardData.unit_name}
                            onChange={(e) => handleWizardChange('unit_name', e.target.value)}
                            className="w-full border-2 border-indigo-200 rounded-xl p-3 text-gray-800 font-medium focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 outline-none"
                            placeholder="Ej: Caja, Saco, Gramo, Metro..."
                        />
                    </div>

                    {/* Type Selector */}
                    <div>
                        <label className="block text-sm font-bold text-gray-700 mb-3">
                            Tipo de Relación
                        </label>
                        <div className="grid grid-cols-2 gap-3">
                            <button
                                type="button"
                                onClick={() => handleWizardChange('type', 'packing')}
                                className={`p-4 rounded-xl border-2 transition-all ${wizardData.type === 'packing'
                                        ? 'border-purple-500 bg-purple-100 shadow-md'
                                        : 'border-gray-200 bg-white hover:border-purple-300'
                                    }`}
                            >
                                <Package className={`mx-auto mb-2 ${wizardData.type === 'packing' ? 'text-purple-600' : 'text-gray-400'}`} size={28} />
                                <p className={`text-sm font-bold ${wizardData.type === 'packing' ? 'text-purple-900' : 'text-gray-600'}`}>
                                    EMPAQUE
                                </p>
                                <p className="text-xs text-gray-500 mt-1">Contiene X unidades</p>
                            </button>

                            <button
                                type="button"
                                onClick={() => handleWizardChange('type', 'fraction')}
                                className={`p-4 rounded-xl border-2 transition-all ${wizardData.type === 'fraction'
                                        ? 'border-orange-500 bg-orange-100 shadow-md'
                                        : 'border-gray-200 bg-white hover:border-orange-300'
                                    }`}
                            >
                                <Tag className={`mx-auto mb-2 ${wizardData.type === 'fraction' ? 'text-orange-600' : 'text-gray-400'}`} size={28} />
                                <p className={`text-sm font-bold ${wizardData.type === 'fraction' ? 'text-orange-900' : 'text-gray-600'}`}>
                                    FRACCIÓN
                                </p>
                                <p className="text-xs text-gray-500 mt-1">Es parte de la unidad</p>
                            </button>
                        </div>
                    </div>

                    {/* Quantity Input */}
                    <div>
                        <label className="block text-sm font-bold text-gray-700 mb-2">
                            {wizardData.type === 'packing'
                                ? `¿Cuántas ${baseUnitType}s contiene?`
                                : `¿Cuántos ${wizardData.unit_name || 'unidades'} hay en 1 ${baseUnitType}?`
                            }
                        </label>
                        <input
                            type="number"
                            step="0.01"
                            value={wizardData.user_input}
                            onChange={(e) => handleWizardChange('user_input', e.target.value)}
                            className={`w-full border-2 rounded-xl p-3 text-2xl font-black text-center outline-none focus:ring-4 ${wizardData.type === 'packing'
                                    ? 'border-purple-300 text-purple-700 focus:border-purple-500 focus:ring-purple-100'
                                    : 'border-orange-300 text-orange-700 focus:border-orange-500 focus:ring-orange-100'
                                }`}
                            placeholder="0"
                        />
                    </div>

                    {/* Visual Formula */}
                    <div className={`p-4 rounded-xl border-2 ${wizardData.type === 'packing' ? 'bg-purple-50 border-purple-200' : 'bg-orange-50 border-orange-200'
                        }`}>
                        <div className="flex items-start gap-2">
                            <AlertCircle className={wizardData.type === 'packing' ? 'text-purple-600' : 'text-orange-600'} size={20} />
                            <p className={`text-sm font-bold ${wizardData.type === 'packing' ? 'text-purple-900' : 'text-orange-900'}`}>
                                {getFormulaText()}
                            </p>
                        </div>
                    </div>

                    {/* Optional Fields */}
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-xs font-bold text-gray-600 uppercase mb-2">
                                💵 Precio Específico (Opcional)
                            </label>
                            <div className="relative">
                                <span className="absolute left-3 top-3 text-gray-400 font-bold">$</span>
                                <input
                                    type="number"
                                    step="0.01"
                                    value={wizardData.price_usd}
                                    onChange={(e) => handleWizardChange('price_usd', e.target.value)}
                                    className="w-full pl-8 border-gray-200 rounded-xl p-3 text-sm focus:border-green-400 focus:ring-4 focus:ring-green-100 outline-none"
                                    placeholder="Auto"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs font-bold text-gray-600 uppercase mb-2">
                                💱 Tasa de Cambio
                            </label>
                            <select
                                value={wizardData.exchange_rate_id || ''}
                                onChange={(e) => handleWizardChange('exchange_rate_id', e.target.value ? parseInt(e.target.value) : null)}
                                className="w-full border-gray-200 rounded-xl p-3 text-sm focus:border-indigo-400 focus:ring-4 focus:ring-indigo-100 outline-none"
                            >
                                <option value="">🔗 Heredar</option>
                                {exchangeRates.map(rate => (
                                    <option key={rate.id} value={rate.id}>
                                        {rate.name} - {rate.currency_code}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>

                    <div>
                        <label className="block text-xs font-bold text-gray-600 uppercase mb-2">
                            📟 Código de Barras (Opcional)
                        </label>
                        <input
                            type="text"
                            value={wizardData.barcode}
                            onChange={(e) => handleWizardChange('barcode', e.target.value)}
                            className="w-full border-gray-200 rounded-xl p-3 text-sm font-mono focus:border-blue-400 focus:ring-4 focus:ring-blue-100 outline-none"
                            placeholder="Escanea o ingresa manualmente..."
                        />
                    </div>

                    {/* Add Button */}
                    <button
                        type="button"
                        onClick={handleAddUnit}
                        className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-bold py-4 rounded-xl shadow-lg transition-all hover:-translate-y-0.5 flex items-center justify-center gap-2"
                    >
                        <Plus size={20} />
                        Agregar Presentación
                    </button>
                </div>
            </div>

            {/* Units List (Cards) */}
            <div>
                <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                    <Package className="text-blue-600" size={22} />
                    Presentaciones Creadas ({units.length})
                </h3>

                {units.length === 0 ? (
                    <div className="text-center py-12 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200">
                        <Package className="mx-auto text-gray-300 mb-3" size={48} />
                        <p className="text-gray-400 font-medium">No hay presentaciones adicionales</p>
                        <p className="text-xs text-gray-400 mt-2">Solo se venderá por {baseUnitType}</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {units.map(unit => (
                            <div
                                key={unit.id}
                                className={`relative bg-white p-5 rounded-2xl border-2 shadow-sm hover:shadow-md transition-all ${unit.type === 'packing' ? 'border-purple-200' : 'border-orange-200'
                                    }`}
                            >
                                {/* Delete Button */}
                                <button
                                    type="button"
                                    onClick={() => handleDeleteUnit(unit.id)}
                                    className="absolute top-3 right-3 p-2 text-gray-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all"
                                    title="Eliminar presentación"
                                >
                                    <Trash2 size={18} />
                                </button>

                                {/* Header */}
                                <div className="flex items-center gap-3 mb-3 pr-10">
                                    <span className={`px-3 py-1 text-xs font-black uppercase rounded-lg ${unit.type === 'packing'
                                            ? 'bg-purple-600 text-white'
                                            : 'bg-orange-600 text-white'
                                        }`}>
                                        {unit.type === 'packing' ? '📦' : '✂️'}
                                    </span>
                                    <h4 className="text-lg font-bold text-gray-800">{unit.unit_name}</h4>
                                </div>

                                {/* Formula Badge */}
                                <div className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-bold mb-3 ${unit.type === 'packing' ? 'bg-purple-100 text-purple-700' : 'bg-orange-100 text-orange-700'
                                    }`}>
                                    <TrendingUp size={14} />
                                    {unit.type === 'packing'
                                        ? `×${unit.user_input} ${baseUnitType}`
                                        : `÷${unit.user_input}`
                                    }
                                </div>

                                {/* Price Display */}
                                <div className="mb-3">
                                    <p className="text-xs text-gray-500 font-medium mb-1">Precio Calculado</p>
                                    <p className="text-2xl font-black text-green-600 flex items-center gap-1">
                                        <DollarSign size={20} />
                                        {calculateDisplayPrice(unit).toFixed(2)}
                                    </p>
                                    {unit.price_usd > 0 && (
                                        <span className="text-xs text-green-600 font-medium">✓ Precio Fijo</span>
                                    )}
                                </div>

                                {/* Exchange Rate */}
                                <div className="text-xs text-gray-600 border-t pt-2 space-y-1">
                                    <p>
                                        <span className="font-bold">Tasa:</span> {getExchangeRateName(unit.exchange_rate_id)}
                                    </p>
                                    {unit.barcode && (
                                        <p>
                                            <span className="font-bold">Código:</span> <span className="font-mono">{unit.barcode}</span>
                                        </p>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Help Section */}
            <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-4">
                <h5 className="font-bold text-blue-900 mb-2 flex items-center gap-2 text-sm">
                    <AlertCircle size={16} />
                    ¿Cuándo usar cada tipo?
                </h5>
                <div className="space-y-1 text-xs text-blue-800">
                    <p><span className="font-bold text-purple-700">📦 EMPAQUE:</span> Cajas, Sacos, Pallets (múltiples unidades juntas).</p>
                    <p><span className="font-bold text-orange-700">✂️ FRACCIÓN:</span> Gramos, Metros, Litros (partes de la unidad base).</p>
                </div>
            </div>
        </div>
    );
};

export default ProductUnitManager;
