import { useState, useEffect } from 'react';
import {
    FileText, Calendar, User, DollarSign, ArrowRight, Trash2, Printer,
    RefreshCcw, AlertCircle, CheckCircle, Clock
} from 'lucide-react';
import apiClient from '../../config/axios';
import { toast } from 'react-hot-toast';
import { useConfig } from '../../context/ConfigContext';

const QuoteList = ({ onCreateNew }) => {
    const [quotes, setQuotes] = useState([]);
    const [loading, setLoading] = useState(true);
    const { currencies } = useConfig();
    const anchorCurrency = currencies.find(c => c.is_anchor) || { symbol: '$' };

    useEffect(() => {
        fetchQuotes();
    }, []);

    const fetchQuotes = async () => {
        setLoading(true);
        try {
            const response = await apiClient.get('/quotes');
            setQuotes(response.data);
        } catch (error) {
            console.error("Error loading quotes:", error);
            toast.error("Error al cargar cotizaciones");
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id, e) => {
        e.stopPropagation();
        if (!window.confirm("¿Seguro que deseas eliminar esta cotización?")) return;

        try {
            await apiClient.delete(`/quotes/${id}`);
            toast.success("Cotización eliminada");
            setQuotes(quotes.filter(q => q.id !== id));
        } catch (error) {
            console.error(error);
            toast.error("No se pudo eliminar");
        }
    };

    const handleConvertToSale = async (quote, e) => {
        e.stopPropagation();
        // Here we will navigate to POS or trigger conversion logic
        // For now, let's just mark it in UI or use a specialized function
        // Ideally we redirect to /pos?quote_id=123
        if (confirm(`¿Cargar cotización #${quote.id} en Caja para facturar?`)) {
            window.location.href = `/pos?quote_id=${quote.id}`;
        }
    };

    const getStatusBadge = (status) => {
        switch (status) {
            case 'CONVERTED':
                return <span className="bg-green-100 text-green-700 px-2 py-1 rounded-full text-xs font-bold flex items-center gap-1"><CheckCircle size={12} /> Facturada</span>;
            case 'EXPIRED':
                return <span className="bg-red-100 text-red-700 px-2 py-1 rounded-full text-xs font-bold flex items-center gap-1"><AlertCircle size={12} /> Vencida</span>;
            default: // PENDING
                return <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded-full text-xs font-bold flex items-center gap-1"><Clock size={12} /> Pendiente</span>;
        }
    };

    if (loading) {
        return <div className="p-8 text-center text-gray-500">Cargando cotizaciones...</div>;
    }

    if (quotes.length === 0) {
        return (
            <div className="h-full flex flex-col items-center justify-center text-gray-400">
                <FileText size={64} className="mb-4 opacity-20" />
                <h3 className="text-xl font-medium text-gray-600 mb-2">No hay cotizaciones registradas</h3>
                <p className="mb-6">Crea propuestas comerciales para tus clientes</p>
                <button
                    onClick={onCreateNew}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-bold shadow-lg transition-all flex items-center gap-2"
                >
                    Crear Primera Cotización
                </button>
            </div>
        );
    }

    return (
        <div className="h-full overflow-y-auto p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {quotes.map(quote => (
                    <div
                        key={quote.id}
                        className="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-all group overflow-hidden flex flex-col"
                    >
                        {/* Status Stripe */}
                        <div className={`h-1.5 w-full ${quote.status === 'CONVERTED' ? 'bg-green-500' : 'bg-blue-500'}`}></div>

                        <div className="p-5 flex-1">
                            <div className="flex justify-between items-start mb-3">
                                <div>
                                    <h3 className="text-lg font-bold text-gray-800">Cotización #{quote.id}</h3>
                                    <div className="text-xs text-gray-500 flex items-center gap-1 mt-1">
                                        <Calendar size={12} />
                                        {new Date(quote.date).toLocaleDateString()} {new Date(quote.date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </div>
                                </div>
                                {getStatusBadge(quote.status)}
                            </div>

                            <div className="space-y-2 mb-4">
                                <div className="flex items-center gap-2 text-sm text-gray-600">
                                    <User size={16} className="text-gray-400" />
                                    <span className="font-medium truncate block max-w-[200px]" title={quote.customer?.name}>
                                        {quote.customer?.name || "Cliente General"}
                                    </span>
                                </div>
                                <div className="flex items-center gap-2 text-sm font-semibold text-gray-800">
                                    <DollarSign size={16} className="text-gray-400" />
                                    <span className="text-lg">{anchorCurrency.symbol}{Number(quote.total_amount).toFixed(2)}</span>
                                </div>
                            </div>
                        </div>

                        {/* Actions Footer */}
                        <div className="bg-gray-50 p-3 border-t border-gray-100 flex justify-between items-center group-hover:bg-blue-50/30 transition-colors">
                            <div className="flex gap-1">
                                <button
                                    onClick={(e) => handleDelete(quote.id, e)}
                                    className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                                    title="Eliminar"
                                >
                                    <Trash2 size={18} />
                                </button>
                                {/* Print Button - Placeholder for future implementation */}
                                <button
                                    className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                    title="Imprimir PDF"
                                    onClick={(e) => e.stopPropagation()}
                                >
                                    <Printer size={18} />
                                </button>
                            </div>

                            {quote.status !== 'CONVERTED' && (
                                <button
                                    onClick={(e) => handleConvertToSale(quote, e)}
                                    className="flex items-center gap-1 px-3 py-1.5 bg-white border border-blue-200 text-blue-700 hover:bg-blue-600 hover:text-white hover:border-blue-600 rounded-lg text-sm font-bold shadow-sm transition-all"
                                >
                                    Facturar <ArrowRight size={14} />
                                </button>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default QuoteList;
