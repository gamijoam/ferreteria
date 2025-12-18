import { useState, useMemo } from 'react';
import { Layers, Plus, Trash2, ArrowRight, Package, Divide, Bitcoin, Info } from 'lucide-react';

const ProductUnitManager = ({ units, onUnitsChange, baseUnitType, basePrice, exchangeRates, productExchangeRateId }) => {
    const [isWizardOpen, setIsWizardOpen] = useState(false);
    const [wizardStep, setWizardStep] = useState(1); // 1: Type, 2: Details

    // Wizard State
    const [newUnit, setNewUnit] = useState({
        unit_name: '',
        type: 'packing', // 'packing' | 'fraction'
        user_input: 1, // The factor user types (e.g. 12 or 1000)
        barcode: '',
        price_usd: '',
        exchange_rate_id: ''
    });

    const resetWizard = () => {
        setNewUnit({
            unit_name: '',
            type: 'packing',
            user_input: 1,
            barcode: '',
            price_usd: '',
            exchange_rate_id: ''
        });
        setWizardStep(1);
        setIsWizardOpen(false);
    };

    const handleAddUnit = () => {
        // Calculate conversion factor based on type
        let finalFactor = parseFloat(newUnit.user_input);
        if (newUnit.type === 'fraction') {
            finalFactor = finalFactor !== 0 ? 1 / finalFactor : 0;
        }

        const unitToAdd = {
            id: Date.now(),
            unit_name: newUnit.unit_name,
            user_input: parseFloat(newUnit.user_input),
            conversion_factor: finalFactor,
            type: newUnit.type,
            barcode: newUnit.barcode,
            price_usd: parseFloat(newUnit.price_usd) || 0,
            exchange_rate_id: newUnit.exchange_rate_id ? parseInt(newUnit.exchange_rate_id) : null
        };

        onUnitsChange([...units, unitToAdd]);
        resetWizard();
    };

    // Derived Logic for Feedback
    const feedbackMessage = useMemo(() => {
        const val = parseFloat(newUnit.user_input) || 0;
        if (newUnit.type === 'packing') {
            return `Entendido: Al vender 1 ${newUnit.unit_name || '[Nueva Unidad]'}, se descontarán ${val} ${baseUnitType} del inventario.`;
        } else {
            return `Entendido: 1 ${newUnit.unit_name || '[Nueva Unidad]'} equivale a una fracción 1/${val} de ${baseUnitType}.`;
        }
    }, [newUnit.user_input, newUnit.type, newUnit.unit_name, baseUnitType]);

    // Render Wizard
    const renderWizard = () => (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[60] p-4">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden animate-fade-in-up">
                <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-6 text-white">
                    <h3 className="text-xl font-bold flex items-center">
                        <Layers className="mr-2" /> Agregar Nueva Presentación
                    </h3>
                    <p className="text-blue-100 text-sm mt-1">Paso {wizardStep} de 2: {wizardStep === 1 ? 'Tipo de Unidad' : 'Detalles'}</p>
                </div>

                <div className="p-8">
                    {wizardStep === 1 ? (
                        <div className="space-y-4">
                            <p className="text-gray-600 mb-4 font-medium">¿Qué tipo de unidad deseas agregar?</p>

                            <button
                                onClick={() => { setNewUnit({ ...newUnit, type: 'packing' }); setWizardStep(2); }}
                                className="w-full p-4 border-2 border-gray-200 hover:border-blue-500 hover:bg-blue-50 rounded-xl transition-all flex items-center group text-left"
                            >
                                <div className="bg-blue-100 text-blue-600 p-3 rounded-lg mr-4 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                                    <Package size={24} />
                                </div>
                                <div>
                                    <h4 className="font-bold text-gray-800">Unidad de Empaque (Mayorista)</h4>
                                    <p className="text-sm text-gray-500">Ej: Caja de 12, Bulto de 50. Contiene múltiples unidades base.</p>
                                </div>
                            </button>

                            <button
                                onClick={() => { setNewUnit({ ...newUnit, type: 'fraction' }); setWizardStep(2); }}
                                className="w-full p-4 border-2 border-gray-200 hover:border-indigo-500 hover:bg-indigo-50 rounded-xl transition-all flex items-center group text-left"
                            >
                                <div className="bg-indigo-100 text-indigo-600 p-3 rounded-lg mr-4 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                                    <Divide size={24} />
                                </div>
                                <div>
                                    <h4 className="font-bold text-gray-800">Unidad Fraccionaria (Menudeo)</h4>
                                    <p className="text-sm text-gray-500">Ej: Gramos, Mililitros. Es una parte de la unidad base.</p>
                                </div>
                            </button>
                        </div>
                    ) : (
                        <div className="space-y-5 animate-fade-in-right">
                            <div>
                                <label className="block text-sm font-bold text-gray-700 mb-1">Nombre de la Unidad</label>
                                <input
                                    autoFocus
                                    className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                    placeholder={newUnit.type === 'packing' ? "Ej: Caja, Bulto, Paquete" : "Ej: Gramo, Metro"}
                                    value={newUnit.unit_name}
                                    onChange={e => setNewUnit({ ...newUnit, unit_name: e.target.value })}
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-bold text-gray-700 mb-1">
                                    {newUnit.type === 'packing' ? `¿Cuántos ${baseUnitType} contiene?` : `¿En cuántas partes se divide 1 ${baseUnitType}?`}
                                </label>
                                <div className="flex items-center">
                                    <input
                                        type="number"
                                        className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none font-mono font-bold text-lg"
                                        value={newUnit.user_input}
                                        onChange={e => setNewUnit({ ...newUnit, user_input: e.target.value })}
                                    />
                                </div>
                                <div className="mt-2 text-xs bg-blue-50 text-blue-700 p-3 rounded-lg flex items-start">
                                    <Info size={16} className="mr-2 mt-0.5 flex-shrink-0" />
                                    <span>{feedbackMessage}</span>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-bold text-gray-700 mb-1">Precio USD (Opcional)</label>
                                    <input
                                        type="number"
                                        className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                        placeholder="0.00"
                                        value={newUnit.price_usd}
                                        onChange={e => setNewUnit({ ...newUnit, price_usd: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-bold text-gray-700 mb-1">Código Barra</label>
                                    <input
                                        className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                        placeholder="SCAN..."
                                        value={newUnit.barcode}
                                        onChange={e => setNewUnit({ ...newUnit, barcode: e.target.value })}
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-bold text-gray-700 mb-1">Tasa de Cambio Específica</label>
                                <select
                                    className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                    value={newUnit.exchange_rate_id}
                                    onChange={e => setNewUnit({ ...newUnit, exchange_rate_id: e.target.value })}
                                >
                                    <option value="">-- Automático / Heredado --</option>
                                    {exchangeRates.map(r => (
                                        <option key={r.id} value={r.id}>{r.name} ({r.currency_code})</option>
                                    ))}
                                </select>
                            </div>
                        </div>
                    )}
                </div>

                <div className="bg-gray-50 p-5 flex justify-end gap-3 border-t">
                    {wizardStep === 2 && (
                        <button onClick={() => setWizardStep(1)} className="px-5 py-2 text-gray-600 hover:bg-gray-200 rounded-lg font-medium transition-colors">Atrás</button>
                    )}
                    <button onClick={resetWizard} className="px-5 py-2 text-red-600 hover:bg-red-50 rounded-lg font-medium transition-colors">Cancelar</button>
                    {wizardStep === 1 ? (
                        null
                    ) : (
                        <button
                            disabled={!newUnit.unit_name || !newUnit.user_input}
                            onClick={handleAddUnit}
                            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold shadow-lg transition-all transform active:scale-95 disabled:opacity-50 disabled:scale-100"
                        >
                            Guardar Unidad
                        </button>
                    )}
                </div>
            </div>
        </div>
    );

    return (
        <div className="max-w-4xl mx-auto space-y-6 animate-fade-in-up">
            <div className="flex items-center justify-between">
                <div>
                    <h3 className="text-xl font-bold text-gray-800">Unidades y Presentaciones</h3>
                    <p className="text-gray-500 text-sm">Administra cajas, bultos y fracciones para este producto.</p>
                </div>
                <button
                    onClick={() => setIsWizardOpen(true)}
                    className="bg-gray-900 hover:bg-gray-800 text-white px-5 py-2.5 rounded-xl font-semibold shadow-lg shadow-gray-200 transition-all flex items-center"
                >
                    <Plus size={18} className="mr-2" /> Agregar Unidad
                </button>
            </div>

            {units.length === 0 ? (
                <div className="text-center py-12 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200">
                    <Layers className="mx-auto text-gray-300 mb-4" size={48} />
                    <p className="text-gray-500 font-medium">Solo se vende por unidad base ({baseUnitType}).</p>
                    <p className="text-sm text-gray-400 mt-2">Agrega presentaciones si vendes cajas o fracciones.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {units.map((unit) => (
                        <div key={unit.id} className="bg-white p-5 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow relative group">
                            <div className="flex justify-between items-start mb-3">
                                <div className="flex items-center gap-3">
                                    <div className={`p-2 rounded-lg ${unit.type === 'packing' ? 'bg-blue-100 text-blue-600' : 'bg-indigo-100 text-indigo-600'}`}>
                                        {unit.type === 'packing' ? <Package size={20} /> : <Divide size={20} />}
                                    </div>
                                    <div>
                                        <h4 className="font-bold text-gray-900">{unit.unit_name}</h4>
                                        <span className="text-xs uppercase font-bold tracking-wider text-gray-400">
                                            {unit.type === 'packing' ? 'Empaque' : 'Fracción'}
                                        </span>
                                    </div>
                                </div>
                                <button
                                    onClick={() => onUnitsChange(units.filter(u => u.id !== unit.id))}
                                    className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                                >
                                    <Trash2 size={18} />
                                </button>
                            </div>

                            <div className="space-y-2 text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
                                <div className="flex justify-between">
                                    <span>Factor:</span>
                                    <span className="font-mono font-bold">
                                        {unit.type === 'packing' ? `x${unit.user_input}` : `1/${unit.user_input}`}
                                    </span>
                                </div>
                                {unit.price_usd > 0 && (
                                    <div className="flex justify-between text-green-700">
                                        <span>Precio Fijo USD:</span>
                                        <span className="font-bold">${unit.price_usd.toFixed(2)}</span>
                                    </div>
                                )}
                                {unit.barcode && (
                                    <div className="flex justify-between">
                                        <span>Barcode:</span>
                                        <span className="font-mono">{unit.barcode}</span>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {isWizardOpen && renderWizard()}
        </div>
    );
};

export default ProductUnitManager;
