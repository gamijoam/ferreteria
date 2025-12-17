import { useState, useEffect } from 'react';
import { Building2, Coins, Receipt, Save, RefreshCw, Trash2, Plus, Edit } from 'lucide-react';
import { useConfig } from '../context/ConfigContext';
import configService from '../services/configService';

const Settings = () => {
    const { business, currencies, refreshConfig } = useConfig();
    const [activeTab, setActiveTab] = useState('business');

    // Local Forms State
    const [bizForm, setBizForm] = useState({ name: '', document_id: '', address: '', phone: '' });
    const [currencyForm, setCurrencyForm] = useState({ name: '', symbol: '', rate: '', is_anchor: false, is_active: true });
    const [editingCurrency, setEditingCurrency] = useState(null);
    const [isCurrencyModalOpen, setIsCurrencyModalOpen] = useState(false);

    useEffect(() => {
        if (business) {
            setBizForm({
                name: business.name || '',
                document_id: business.document_id || '',
                address: business.address || '',
                phone: business.phone || ''
            });
        }
    }, [business]);

    const handleBizSave = async () => {
        try {
            await configService.updateBusinessInfo(bizForm);
            alert("Datos de negocio actualizados");
            refreshConfig();
        } catch (e) { console.error(e); alert("Error al guardar"); }
    };

    const handleCurrencySave = async () => {
        try {
            const payload = { ...currencyForm, rate: Number(currencyForm.rate) };
            if (editingCurrency) {
                await configService.updateCurrency(editingCurrency.id, payload);
            } else {
                await configService.createCurrency(payload);
            }
            refreshConfig();
            setIsCurrencyModalOpen(false);
            setEditingCurrency(null);
            setCurrencyForm({ name: '', symbol: '', rate: '', is_anchor: false, is_active: true });
        } catch (e) {
            console.error(e);
            alert("Error al guardar moneda"); // In real app, check for non-unique anchor error
        }
    };

    const openEditCurrency = (curr) => {
        setEditingCurrency(curr);
        setCurrencyForm(curr);
        setIsCurrencyModalOpen(true);
    };

    const handleDeleteCurrency = async (id) => {
        if (window.confirm("¿Eliminar moneda?")) {
            await configService.deleteCurrency(id);
            refreshConfig();
        }
    }

    return (
        <div className="container mx-auto p-4 max-w-5xl">
            <h1 className="text-3xl font-bold text-gray-800 mb-6">Configuración</h1>

            {/* Tabs Header */}
            <div className="flex border-b mb-6">
                <button
                    onClick={() => setActiveTab('business')}
                    className={`px-6 py-3 font-medium flex items-center ${activeTab === 'business' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                >
                    <Building2 className="mr-2" size={20} /> Negocio
                </button>
                <button
                    onClick={() => setActiveTab('currencies')}
                    className={`px-6 py-3 font-medium flex items-center ${activeTab === 'currencies' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                >
                    <Coins className="mr-2" size={20} /> Monedas y Tasas
                </button>
                <button
                    onClick={() => setActiveTab('taxes')}
                    className={`px-6 py-3 font-medium flex items-center ${activeTab === 'taxes' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                >
                    <Receipt className="mr-2" size={20} /> Impuestos
                </button>
            </div>

            {/* Business Tab */}
            {activeTab === 'business' && (
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 animate-in fade-in slide-in-from-left-4 duration-300">
                    <div className="grid md:grid-cols-2 gap-6">
                        <div>
                            <label className="block text-sm font-bold text-gray-700 mb-2">Nombre del Negocio</label>
                            <input type="text" className="w-full border p-2 rounded" value={bizForm.name} onChange={e => setBizForm({ ...bizForm, name: e.target.value })} />
                        </div>
                        <div>
                            <label className="block text-sm font-bold text-gray-700 mb-2">Documento Legal (RIF/NIT)</label>
                            <input type="text" className="w-full border p-2 rounded" value={bizForm.document_id} onChange={e => setBizForm({ ...bizForm, document_id: e.target.value })} />
                        </div>
                        <div>
                            <label className="block text-sm font-bold text-gray-700 mb-2">Teléfono</label>
                            <input type="text" className="w-full border p-2 rounded" value={bizForm.phone} onChange={e => setBizForm({ ...bizForm, phone: e.target.value })} />
                        </div>
                        <div className="md:col-span-2">
                            <label className="block text-sm font-bold text-gray-700 mb-2">Dirección</label>
                            <textarea className="w-full border p-2 rounded" rows="3" value={bizForm.address} onChange={e => setBizForm({ ...bizForm, address: e.target.value })}></textarea>
                        </div>
                    </div>

                    <div className="mt-6 flex justify-end">
                        <button onClick={handleBizSave} className="bg-blue-600 text-white px-6 py-2 rounded-lg font-bold hover:bg-blue-700 flex items-center">
                            <Save className="mr-2" size={20} /> Guardar Cambios
                        </button>
                    </div>
                </div>
            )}

            {/* Currencies Tab (Refactored Catalog) */}
            {activeTab === 'currencies' && (
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 animate-in fade-in slide-in-from-right-4 duration-300">
                    <div className="flex justify-between items-center mb-6">
                        <div>
                            <h2 className="text-xl font-bold text-gray-800">Catálogo de Monedas</h2>
                            <p className="text-gray-500 text-sm">Activa las monedas que aceptas y actualiza sus tasas.</p>
                        </div>
                        <button
                            onClick={refreshConfig}
                            className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded-lg font-medium flex items-center"
                        >
                            <RefreshCw size={18} className="mr-2" /> Actualizar
                        </button>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead className="bg-gray-50 text-gray-600 text-xs uppercase font-bold">
                                <tr>
                                    <th className="p-4">Moneda</th>
                                    <th className="p-4">Estado</th>
                                    <th className="p-4 text-center">Fijar como Base</th>
                                    <th className="p-4">Tasa de Cambio</th>
                                    <th className="p-4 text-right">Información</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y">
                                {Array.isArray(currencies) && currencies.map(curr => (
                                    <tr key={curr.id} className={`hover:bg-gray-50 ${!curr.is_active ? 'opacity-60 bg-gray-50' : ''}`}>
                                        <td className="p-4">
                                            <div className="font-bold text-gray-800">{curr.name}</div>
                                            <div className="text-xs text-gray-500 font-mono">{curr.symbol}</div>
                                        </td>
                                        <td className="p-4">
                                            <button
                                                onClick={async () => {
                                                    await configService.updateCurrency(curr.id, { is_active: !curr.is_active });
                                                    refreshConfig();
                                                }}
                                                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${curr.is_active ? 'bg-green-500' : 'bg-gray-300'}`}
                                            >
                                                <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${curr.is_active ? 'translate-x-6' : 'translate-x-1'}`} />
                                            </button>
                                        </td>
                                        <td className="p-4 text-center">
                                            <div
                                                className={`inline-flex items-center justify-center w-6 h-6 rounded-full border-2 cursor-pointer ${curr.is_anchor ? 'border-blue-600' : 'border-gray-300 hover:border-gray-400'}`}
                                                onClick={async () => {
                                                    if (curr.is_anchor) return;
                                                    if (window.confirm(`⚠️ ADVERTENCIA CRÍTICA ⚠️\n\nAl cambiar la moneda ancla a ${curr.name}, todos los precios base de los productos se asumirán en esta nueva moneda SIN CONVERSIÓN.\n\n¿Estás seguro de que deseas proceder?`)) {
                                                        await configService.updateCurrency(curr.id, { is_anchor: true, rate: 1.0 });
                                                        refreshConfig();
                                                    }
                                                }}
                                            >
                                                {curr.is_anchor && <div className="w-3 h-3 bg-blue-600 rounded-full" />}
                                            </div>
                                        </td>
                                        <td className="p-4">
                                            <div className="flex items-center">
                                                <input
                                                    type="number"
                                                    defaultValue={curr.rate}
                                                    disabled={!curr.is_active || curr.is_anchor}
                                                    onBlur={async (e) => {
                                                        const newRate = parseFloat(e.target.value);
                                                        if (newRate !== curr.rate && !curr.is_anchor) {
                                                            await configService.updateCurrency(curr.id, { rate: newRate });
                                                            refreshConfig();
                                                        }
                                                    }}
                                                    className="border border-gray-300 rounded px-2 py-1 w-32 font-mono text-right focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none disabled:bg-gray-100 disabled:text-gray-400"
                                                />
                                            </div>
                                        </td>
                                        <td className="p-4 text-right">
                                            {!curr.is_anchor && curr.is_active && (
                                                <span className="text-xs text-green-600 font-medium">Editable</span>
                                            )}
                                            {curr.is_anchor && (
                                                <span className="text-xs text-blue-600 font-bold bg-blue-50 px-2 py-1 rounded">ANCLA</span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {currencies.length === 0 && (
                            <div className="p-8 text-center bg-red-50 text-red-600 rounded mt-4">
                                <p className="font-bold">⚠️ No se encontraron monedas.</p>
                                <p className="text-sm">Esto puede indicar que el backend no devolvió datos.</p>
                                <p className="text-xs mt-2 font-mono">{JSON.stringify(currencies)}</p>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Taxes Tab */}
            {activeTab === 'taxes' && (
                <div className="bg-white p-10 rounded-xl shadow-sm border border-gray-100 text-center">
                    <Receipt className="mx-auto text-gray-300 mb-4" size={64} />
                    <h3 className="text-xl font-bold text-gray-600">Gestión de Impuestos</h3>
                    <p className="text-gray-400">Próximamente disponible.</p>
                </div>
            )}

            {/* Currency Modal */}
            {isCurrencyModalOpen && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 w-full max-w-sm">
                        <h3 className="font-bold text-xl mb-4">{editingCurrency ? 'Editar Moneda' : 'Nueva Moneda'}</h3>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-bold text-gray-700">Nombre</label>
                                <input type="text" className="w-full border p-2 rounded" value={currencyForm.name} onChange={e => setCurrencyForm({ ...currencyForm, name: e.target.value })} />
                            </div>
                            <div>
                                <label className="block text-sm font-bold text-gray-700">Símbolo</label>
                                <input type="text" className="w-full border p-2 rounded" value={currencyForm.symbol} onChange={e => setCurrencyForm({ ...currencyForm, symbol: e.target.value })} />
                            </div>
                            <div>
                                <label className="block text-sm font-bold text-gray-700">Tasa</label>
                                <input type="number" className="w-full border p-2 rounded" value={currencyForm.rate} onChange={e => setCurrencyForm({ ...currencyForm, rate: e.target.value })} disabled={currencyForm.is_anchor} />
                                {currencyForm.is_anchor && <span className="text-xs text-gray-500">La moneda principal siempre es 1.00</span>}
                            </div>
                            {!editingCurrency && (
                                <div className="flex items-center">
                                    <input type="checkbox" className="mr-2" checked={currencyForm.is_anchor} onChange={e => setCurrencyForm({ ...currencyForm, is_anchor: e.target.checked })} />
                                    <label className="text-sm">Es Moneda Principal (Anchor)</label>
                                </div>
                            )}
                        </div>
                        <div className="flex justify-end gap-2 mt-6">
                            <button onClick={() => setIsCurrencyModalOpen(false)} className="px-4 py-2 text-gray-600">Cancelar</button>
                            <button onClick={handleCurrencySave} className="px-4 py-2 bg-blue-600 text-white rounded">Guardar</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Settings;
