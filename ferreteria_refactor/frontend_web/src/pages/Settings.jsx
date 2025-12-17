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
        if (business) setBizForm(business);
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

            {/* Currencies Tab */}
            {activeTab === 'currencies' && (
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 animate-in fade-in slide-in-from-right-4 duration-300">
                    <div className="flex justify-between items-center mb-6">
                        <div>
                            <h2 className="text-xl font-bold text-gray-800">Monedas Activas</h2>
                            <p className="text-gray-500 text-sm">Gestiona las tasas de cambio para facturación y reportes.</p>
                        </div>
                        <button
                            onClick={() => { setEditingCurrency(null); setCurrencyForm({ name: '', symbol: '', rate: '', is_anchor: false, is_active: true }); setIsCurrencyModalOpen(true); }}
                            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium flex items-center"
                        >
                            <Plus size={20} className="mr-2" /> Nueva Moneda
                        </button>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead className="bg-gray-50 text-gray-600 text-xs uppercase font-bold">
                                <tr>
                                    <th className="p-4">Moneda</th>
                                    <th className="p-4">Símbolo</th>
                                    <th className="p-4">Tasa de Cambio</th>
                                    <th className="p-4 text-center">Referencia (Anchor)</th>
                                    <th className="p-4 text-center">Acciones</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y">
                                {currencies.map(curr => (
                                    <tr key={curr.id} className="hover:bg-gray-50">
                                        <td className="p-4 font-medium text-gray-800">{curr.name}</td>
                                        <td className="p-4 text-gray-600">{curr.symbol}</td>
                                        <td className="p-4 font-mono font-bold text-blue-600">{curr.rate.toFixed(4)}</td>
                                        <td className="p-4 text-center">
                                            {curr.is_anchor ? (
                                                <span className="bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded font-bold">PRINCIPAL</span>
                                            ) : <span className="text-gray-400">-</span>}
                                        </td>
                                        <td className="p-4 flex justify-center space-x-2">
                                            <button onClick={() => openEditCurrency(curr)} className="p-2 text-blue-600 hover:bg-blue-50 rounded"><Edit size={18} /></button>
                                            {!curr.is_anchor && (
                                                <button onClick={() => handleDeleteCurrency(curr.id)} className="p-2 text-red-600 hover:bg-red-50 rounded"><Trash2 size={18} /></button>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
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
