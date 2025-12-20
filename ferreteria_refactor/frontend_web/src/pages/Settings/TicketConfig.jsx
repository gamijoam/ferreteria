import { useState, useEffect } from 'react';
import { Printer, Save, FileText, AlertCircle, CheckCircle, Grid, Code } from 'lucide-react';
import apiClient from '../../config/axios';

const DEFAULT_TEMPLATE = `<center><bold>${'{{ business.name }}'}</bold></center>
<center>${'{{ business.address }}'}</center>
<center>RIF: ${'{{ business.document_id }}'}</center>
<center>Tel: ${'{{ business.phone }}'}</center>
================================
Fecha: ${'{{ sale.date }}'}
Factura: #${'{{ sale.id }}'}
${'{% if sale.customer %}'}
Cliente: ${'{{ sale.customer.name }}'}
${'{% endif %}'}
${'{% if sale.is_credit %}'}
<center><bold>*** A CREDITO ***</bold></center>
Saldo Pendiente: $${'{{ sale.balance }}'}
${'{% endif %}'}
================================
<left>PRODUCTO</left><right>TOTAL</right>
--------------------------------
${'{% for item in sale[\'items\'] %}'}
${'{{ item.product.name }}'}
  ${'{{ item.quantity }}'} x $${'{{ item.unit_price }}'} = $${'{{ item.subtotal }}'}
${'{% endfor %}'}
================================
<right><bold>TOTAL: $${'{{ sale.total }}'}</bold></right>
================================
<center>Gracias por su compra</center>
<center>${'{{ business.name }}'}</center>
<cut>`;

const TicketConfig = () => {
    const [template, setTemplate] = useState(DEFAULT_TEMPLATE);
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState(null);
    const [view, setView] = useState('gallery'); // 'gallery' or 'editor'
    const [presets, setPresets] = useState([]);

    useEffect(() => {
        fetchTemplate();
        fetchPresets();
    }, []);

    const fetchTemplate = async () => {
        setLoading(true);
        try {
            const response = await apiClient.get('/config/business');
            if (response.data.ticket_template) {
                setTemplate(response.data.ticket_template);
            }
        } catch (error) {
            console.error('Error fetching template:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchPresets = async () => {
        try {
            const response = await apiClient.get('/config/ticket-templates/presets');
            setPresets(Object.entries(response.data).map(([id, preset]) => ({
                id,
                ...preset
            })));
        } catch (error) {
            console.error('Error fetching presets:', error);
        }
    };

    const handleSave = async () => {
        setSaving(true);
        setMessage(null);
        try {
            await apiClient.put('/config/business', {
                ticket_template: template
            });
            setMessage({ type: 'success', text: '✅ Plantilla guardada exitosamente' });
        } catch (error) {
            console.error('Error saving template:', error);
            setMessage({ type: 'error', text: '❌ Error al guardar plantilla' });
        } finally {
            setSaving(false);
        }
    };

    const handleTestPrint = async () => {
        setMessage(null);
        try {
            await apiClient.post('/config/test-print');
            setMessage({ type: 'success', text: '🖨️ Ticket de prueba enviado a impresora' });
        } catch (error) {
            console.error('Error printing test:', error);
            setMessage({ type: 'error', text: '❌ Error al imprimir prueba: ' + (error.response?.data?.detail || error.message) });
        }
    };

    const handleReset = () => {
        if (confirm('¿Restaurar plantilla por defecto? Se perderán los cambios no guardados.')) {
            setTemplate(DEFAULT_TEMPLATE);
        }
    };

    const handleApplyPreset = async (presetId) => {
        setMessage(null);
        try {
            await apiClient.post(`/config/ticket-templates/apply/${presetId}`);
            await fetchTemplate(); // Reload template
            setMessage({ type: 'success', text: '✅ Plantilla aplicada exitosamente' });
            setView('editor'); // Switch to editor view
        } catch (error) {
            console.error('Error applying preset:', error);
            setMessage({ type: 'error', text: '❌ Error al aplicar plantilla' });
        }
    };

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                    <Printer size={28} />
                    Configuración de Tickets
                </h1>
                <p className="text-gray-600 mt-1">
                    Personaliza el diseño de tus tickets de venta
                </p>
            </div>

            {/* View Tabs */}
            <div className="mb-6 flex gap-2 border-b">
                <button
                    onClick={() => setView('gallery')}
                    className={`px-4 py-2 font-medium flex items-center gap-2 transition-colors ${view === 'gallery'
                            ? 'border-b-2 border-blue-600 text-blue-600'
                            : 'text-gray-500 hover:text-gray-700'
                        }`}
                >
                    <Grid size={20} />
                    Galería de Plantillas
                </button>
                <button
                    onClick={() => setView('editor')}
                    className={`px-4 py-2 font-medium flex items-center gap-2 transition-colors ${view === 'editor'
                            ? 'border-b-2 border-blue-600 text-blue-600'
                            : 'text-gray-500 hover:text-gray-700'
                        }`}
                >
                    <Code size={20} />
                    Editor Avanzado
                </button>
            </div>

            {message && (
                <div className={`mb-4 p-4 rounded-lg flex items-center gap-2 ${message.type === 'success'
                        ? 'bg-green-50 text-green-800 border border-green-200'
                        : 'bg-red-50 text-red-800 border border-red-200'
                    }`}>
                    {message.type === 'success' ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
                    {message.text}
                </div>
            )}

            {/* Gallery View */}
            {view === 'gallery' && (
                <div>
                    <h2 className="text-xl font-bold text-gray-800 mb-4">Plantillas Predefinidas</h2>
                    <p className="text-gray-600 mb-6">
                        Selecciona una plantilla lista para usar. Puedes personalizarla después en el editor avanzado.
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {presets.map(preset => (
                            <div key={preset.id} className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow">
                                <div className="p-6">
                                    <h3 className="text-lg font-bold text-gray-800 mb-2">{preset.name}</h3>
                                    <p className="text-gray-600 text-sm mb-4">{preset.description}</p>

                                    {/* Preview */}
                                    <div className="bg-gray-50 rounded p-4 mb-4 font-mono text-xs text-gray-700 h-48 overflow-hidden border border-gray-200">
                                        <div className="text-center font-bold">MI NEGOCIO</div>
                                        <div className="text-center text-xs">Calle Principal #123</div>
                                        <div className="text-center text-xs">RIF: J-12345678</div>
                                        <div className="border-t border-gray-300 my-2"></div>
                                        <div className="text-xs">Factura: #001</div>
                                        <div className="text-xs">Fecha: 19/12/2025</div>
                                        <div className="border-t border-gray-300 my-2"></div>
                                        <div className="text-xs">Producto 1</div>
                                        <div className="text-xs text-right">$10.00</div>
                                        <div className="text-xs">Producto 2</div>
                                        <div className="text-xs text-right">$15.00</div>
                                        <div className="border-t border-gray-300 my-2"></div>
                                        <div className="text-right font-bold">TOTAL: $25.00</div>
                                    </div>

                                    <button
                                        onClick={() => handleApplyPreset(preset.id)}
                                        className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                                    >
                                        Usar Esta Plantilla
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Editor View */}
            {view === 'editor' && (
                <div className="grid grid-cols-3 gap-6">
                    {/* Editor */}
                    <div className="col-span-2 bg-white rounded-lg shadow-md p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
                                <FileText size={20} />
                                Editor de Plantilla
                            </h2>
                            <div className="flex gap-2">
                                <button
                                    onClick={handleReset}
                                    className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition"
                                >
                                    Restaurar Defecto
                                </button>
                            </div>
                        </div>

                        <textarea
                            value={template}
                            onChange={(e) => setTemplate(e.target.value)}
                            className="w-full h-96 p-4 border border-gray-300 rounded-lg font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="Escribe tu plantilla aquí..."
                        />

                        <div className="flex gap-3 mt-4">
                            <button
                                onClick={handleSave}
                                disabled={saving}
                                className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-medium flex items-center justify-center gap-2 transition"
                            >
                                <Save size={20} />
                                {saving ? 'Guardando...' : 'Guardar Configuración'}
                            </button>
                            <button
                                onClick={handleTestPrint}
                                className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2 transition"
                            >
                                <Printer size={20} />
                                Imprimir Prueba
                            </button>
                        </div>
                    </div>

                    {/* Reference Panel */}
                    <div className="col-span-1 bg-white rounded-lg shadow-md p-6">
                        <h2 className="text-lg font-semibold text-gray-800 mb-4">Referencia Rápida</h2>

                        <div className="space-y-4">
                            {/* Variables */}
                            <div>
                                <h3 className="font-semibold text-gray-700 mb-2">Variables Disponibles</h3>
                                <div className="text-sm space-y-1 font-mono">
                                    <div className="text-blue-600">business.name</div>
                                    <div className="text-blue-600">business.address</div>
                                    <div className="text-blue-600">business.phone</div>
                                    <div className="text-purple-600">sale.id</div>
                                    <div className="text-purple-600">sale.date</div>
                                    <div className="text-purple-600">sale.total</div>
                                    <div className="text-purple-600">sale['items']</div>
                                </div>
                            </div>

                            {/* Jinja2 Syntax */}
                            <div>
                                <h3 className="font-semibold text-gray-700 mb-2">Sintaxis Jinja2</h3>
                                <div className="text-sm space-y-2">
                                    <div className="bg-gray-50 p-2 rounded font-mono text-xs">
                                        {'{{ variable }}'}
                                    </div>
                                    <div className="bg-gray-50 p-2 rounded font-mono text-xs">
                                        {'{% if condition %}...{% endif %}'}
                                    </div>
                                    <div className="bg-gray-50 p-2 rounded font-mono text-xs">
                                        {'{% for item in sale[\'items\'] %}...{% endfor %}'}
                                    </div>
                                </div>
                            </div>

                            {/* Format Tags */}
                            <div>
                                <h3 className="font-semibold text-gray-700 mb-2">Tags de Formato</h3>
                                <div className="text-sm space-y-1">
                                    <div className="font-mono text-xs">&lt;center&gt;...&lt;/center&gt;</div>
                                    <div className="font-mono text-xs">&lt;left&gt;...&lt;/left&gt;</div>
                                    <div className="font-mono text-xs">&lt;right&gt;...&lt;/right&gt;</div>
                                    <div className="font-mono text-xs">&lt;bold&gt;...&lt;/bold&gt;</div>
                                    <div className="font-mono text-xs">&lt;cut&gt;</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TicketConfig;
