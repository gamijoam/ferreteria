import { useState, useEffect } from 'react';
import { Printer, Save, FileText, AlertCircle, CheckCircle } from 'lucide-react';
import apiClient from '../../config/axios';

const DEFAULT_TEMPLATE = `<center><bold>{{ business.name }}</bold></center>
<center>{{ business.address }}</center>
<center>RIF: {{ business.document_id }}</center>
<center>Tel: {{ business.phone }}</center>
================================
Fecha: {{ sale.date }}
Factura: #{{ sale.id }}
{% if sale.customer %}
Cliente: {{ sale.customer.name }}
{% endif %}
{% if sale.is_credit %}
<center><bold>*** A CREDITO ***</bold></center>
Saldo Pendiente: ${{ sale.balance }}
{% endif %}
================================
<left>PRODUCTO</left><right>TOTAL</right>
--------------------------------
{% for item in sale.items %}
{{ item.product.name }}
  {{ item.quantity }} x ${{ item.unit_price }} = ${{ item.subtotal }}
{% endfor %}
================================
<right><bold>TOTAL: ${{ sale.total }}</bold></right>
================================
<center>Gracias por su compra</center>
<center>{{ business.name }}</center>
<cut>`;

const TicketConfig = () => {
    const [template, setTemplate] = useState(DEFAULT_TEMPLATE);
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState(null);

    useEffect(() => {
        fetchTemplate();
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

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                    <Printer size={28} />
                    Configuración de Tickets
                </h1>
                <p className="text-gray-600 mt-1">
                    Personaliza el diseño de tus tickets de venta usando plantillas Jinja2
                </p>
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
                        className="w-full h-[600px] font-mono text-sm p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        placeholder="Escribe tu plantilla aquí..."
                        disabled={loading}
                    />

                    <div className="flex gap-3 mt-4">
                        <button
                            onClick={handleSave}
                            disabled={saving}
                            className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition font-medium"
                        >
                            <Save size={20} />
                            {saving ? 'Guardando...' : 'Guardar Configuración'}
                        </button>
                        <button
                            onClick={handleTestPrint}
                            className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium"
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
                            <h3 className="text-sm font-bold text-gray-700 mb-2">📊 Variables Disponibles</h3>
                            <div className="bg-gray-50 p-3 rounded text-xs font-mono space-y-1">
                                <div><span className="text-blue-600">business.name</span></div>
                                <div><span className="text-blue-600">business.address</span></div>
                                <div><span className="text-blue-600">business.phone</span></div>
                                <div><span className="text-blue-600">business.document_id</span></div>
                                <div className="pt-2"><span className="text-purple-600">sale.id</span></div>
                                <div><span className="text-purple-600">sale.date</span></div>
                                <div><span className="text-purple-600">sale.total</span></div>
                                <div><span className="text-purple-600">sale.is_credit</span></div>
                                <div><span className="text-purple-600">sale.balance</span></div>
                                <div><span className="text-purple-600">sale.customer.name</span></div>
                            </div>
                        </div>

                        {/* Jinja2 Syntax */}
                        <div>
                            <h3 className="text-sm font-bold text-gray-700 mb-2">🔧 Sintaxis Jinja2</h3>
                            <div className="bg-gray-50 p-3 rounded text-xs font-mono space-y-2">
                                <div>
                                    <div className="text-gray-600">Condicional:</div>
                                    <div className="text-green-600">{'{% if sale.is_credit %}'}</div>
                                    <div className="text-green-600">{'{% endif %}'}</div>
                                </div>
                                <div>
                                    <div className="text-gray-600">Loop:</div>
                                    <div className="text-green-600">{'{% for item in sale.items %}'}</div>
                                    <div className="text-green-600">{'{% endfor %}'}</div>
                                </div>
                            </div>
                        </div>

                        {/* Format Tags */}
                        <div>
                            <h3 className="text-sm font-bold text-gray-700 mb-2">🎨 Tags de Formato</h3>
                            <div className="bg-gray-50 p-3 rounded text-xs space-y-1">
                                <div><code className="text-orange-600">&lt;center&gt;</code> - Centrar</div>
                                <div><code className="text-orange-600">&lt;left&gt;</code> - Izquierda</div>
                                <div><code className="text-orange-600">&lt;right&gt;</code> - Derecha</div>
                                <div><code className="text-orange-600">&lt;bold&gt;</code> - Negrita</div>
                                <div><code className="text-orange-600">&lt;cut&gt;</code> - Cortar papel</div>
                            </div>
                        </div>

                        {/* Example */}
                        <div>
                            <h3 className="text-sm font-bold text-gray-700 mb-2">💡 Ejemplo</h3>
                            <div className="bg-gray-50 p-3 rounded text-xs font-mono">
                                <div className="text-green-600">{'{% for item in sale.items %}'}</div>
                                <div className="text-blue-600">{'{{ item.product.name }}'}</div>
                                <div className="text-blue-600">{'  {{ item.quantity }} x ${{ item.unit_price }}'}</div>
                                <div className="text-green-600">{'{% endfor %}'}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TicketConfig;
