import { useState, useEffect } from 'react';
import { Calendar, Search, TrendingUp, TrendingDown, AlertTriangle, DollarSign, Clock, User, CheckCircle, XCircle, ChevronDown, ChevronUp } from 'lucide-react';
import cashService from '../services/cashService';

const CashHistory = () => {
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [expandedId, setExpandedId] = useState(null);

    // Date filters
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');

    useEffect(() => {
        // Load last 30 days by default
        const today = new Date();
        const thirtyDaysAgo = new Date(today);
        thirtyDaysAgo.setDate(today.getDate() - 30);

        setEndDate(today.toISOString().split('T')[0]);
        setStartDate(thirtyDaysAgo.toISOString().split('T')[0]);

        fetchHistory({
            startDate: thirtyDaysAgo.toISOString().split('T')[0],
            endDate: today.toISOString().split('T')[0]
        });
    }, []);

    const fetchHistory = async (filters) => {
        setLoading(true);
        setError('');
        try {
            const data = await cashService.getHistory(filters);
            setSessions(Array.isArray(data) ? data : []);
        } catch (err) {
            setError(err.response?.data?.detail || 'Error al cargar el historial');
            setSessions([]);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = () => {
        fetchHistory({ startDate, endDate });
    };

    const toggleExpand = (id) => {
        setExpandedId(expandedId === id ? null : id);
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('es-VE', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const formatCurrency = (amount, currency = 'USD') => {
        const value = parseFloat(amount || 0);
        if (currency === 'USD' || currency === '$') {
            return `$${value.toFixed(2)}`;
        }
        return `${currency} ${value.toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    };

    const calculateDifference = (session) => {
        const expected = parseFloat(session.expected_cash || 0);
        const actual = parseFloat(session.final_cash || 0);
        return actual - expected;
    };

    const getDifferenceColor = (diff) => {
        if (Math.abs(diff) < 0.01) return 'text-green-600 bg-green-50 border-green-200';
        if (diff > 0) return 'text-green-600 bg-green-50 border-green-200';
        return 'text-red-600 bg-red-50 border-red-200';
    };

    const getDifferenceIcon = (diff) => {
        if (Math.abs(diff) < 0.01) return <CheckCircle size={20} />;
        if (diff > 0) return <TrendingUp size={20} />;
        return <TrendingDown size={20} />;
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-6">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h1 className="text-3xl font-black text-gray-800 flex items-center gap-3">
                                <div className="p-3 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl shadow-lg">
                                    <DollarSign className="text-white" size={32} />
                                </div>
                                Historial de Caja
                            </h1>
                            <p className="text-gray-600 mt-2">Auditoría de cierres de caja y movimientos financieros</p>
                        </div>
                    </div>

                    {/* Date Filters */}
                    <div className="flex flex-wrap gap-4 items-end">
                        <div className="flex-1 min-w-[200px]">
                            <label className="block text-sm font-bold text-gray-700 mb-2">
                                <Calendar className="inline mr-1" size={16} />
                                Desde
                            </label>
                            <input
                                type="date"
                                value={startDate}
                                onChange={(e) => setStartDate(e.target.value)}
                                className="w-full border-2 border-gray-300 rounded-xl p-3 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 outline-none"
                            />
                        </div>

                        <div className="flex-1 min-w-[200px]">
                            <label className="block text-sm font-bold text-gray-700 mb-2">
                                <Calendar className="inline mr-1" size={16} />
                                Hasta
                            </label>
                            <input
                                type="date"
                                value={endDate}
                                onChange={(e) => setEndDate(e.target.value)}
                                className="w-full border-2 border-gray-300 rounded-xl p-3 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 outline-none"
                            />
                        </div>

                        <button
                            onClick={handleSearch}
                            disabled={loading}
                            className="px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-bold rounded-xl hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 transition-all shadow-lg flex items-center gap-2"
                        >
                            <Search size={20} />
                            Buscar
                        </button>
                    </div>
                </div>

                {/* Error Message */}
                {error && (
                    <div className="bg-red-50 border-2 border-red-200 rounded-xl p-4 mb-6 flex items-center gap-3">
                        <AlertTriangle className="text-red-600" size={24} />
                        <p className="text-red-800 font-medium">{error}</p>
                    </div>
                )}

                {/* Loading State */}
                {loading && (
                    <div className="text-center py-12">
                        <div className="inline-block w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-4"></div>
                        <p className="text-gray-600 font-medium">Cargando historial...</p>
                    </div>
                )}

                {/* Sessions List */}
                {!loading && sessions.length === 0 && (
                    <div className="bg-white rounded-2xl shadow-sm p-12 text-center">
                        <DollarSign className="mx-auto text-gray-300 mb-4" size={64} />
                        <p className="text-gray-500 font-medium text-lg">No se encontraron sesiones de caja</p>
                        <p className="text-gray-400 text-sm mt-2">Intenta con un rango de fechas diferente</p>
                    </div>
                )}

                {!loading && sessions.length > 0 && (
                    <div className="space-y-4">
                        {sessions.map((session) => {
                            const difference = calculateDifference(session);
                            const isExpanded = expandedId === session.id;
                            const isClosed = session.status === 'CLOSED';

                            return (
                                <div
                                    key={session.id}
                                    className="bg-white rounded-2xl shadow-md hover:shadow-xl transition-all overflow-hidden border-2 border-gray-100"
                                >
                                    {/* Card Header */}
                                    <div
                                        className="p-6 cursor-pointer hover:bg-gray-50 transition-colors"
                                        onClick={() => toggleExpand(session.id)}
                                    >
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-4 flex-1">
                                                {/* Status Badge */}
                                                <div className={`p-3 rounded-xl ${isClosed ? 'bg-green-100' : 'bg-yellow-100'}`}>
                                                    {isClosed ? (
                                                        <CheckCircle className="text-green-600" size={24} />
                                                    ) : (
                                                        <Clock className="text-yellow-600" size={24} />
                                                    )}
                                                </div>

                                                {/* Session Info */}
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-3 mb-2">
                                                        <h3 className="text-lg font-bold text-gray-800">
                                                            Sesión #{session.id}
                                                        </h3>
                                                        <span className={`px-3 py-1 rounded-full text-xs font-bold ${isClosed ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                                                            }`}>
                                                            {isClosed ? 'CERRADA' : 'ABIERTA'}
                                                        </span>
                                                    </div>

                                                    <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                                                        <div className="flex items-center gap-1">
                                                            <User size={14} />
                                                            <span>{session.user?.full_name || session.user?.username || `Usuario #${session.user_id}`}</span>
                                                        </div>
                                                        <div className="flex items-center gap-1">
                                                            <Clock size={14} />
                                                            <span>{formatDate(session.opened_at)}</span>
                                                        </div>
                                                        {isClosed && session.closed_at && (
                                                            <div className="flex items-center gap-1">
                                                                <XCircle size={14} />
                                                                <span>Cerrado: {formatDate(session.closed_at)}</span>
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>

                                                {/* Financial Summary */}
                                                <div className="text-right">
                                                    <p className="text-sm text-gray-500 mb-1">Efectivo Final</p>
                                                    <p className="text-2xl font-black text-gray-800">
                                                        {formatCurrency(session.final_cash || session.initial_cash)}
                                                    </p>
                                                    {isClosed && (
                                                        <div className={`mt-2 px-3 py-1 rounded-lg border-2 inline-flex items-center gap-2 ${getDifferenceColor(difference)}`}>
                                                            {getDifferenceIcon(difference)}
                                                            <span className="text-sm font-bold">
                                                                {Math.abs(difference) < 0.01 ? 'Cuadrado' :
                                                                    difference > 0 ? `+${formatCurrency(difference)}` :
                                                                        formatCurrency(difference)}
                                                            </span>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>

                                            {/* Expand Icon */}
                                            <div className="ml-4">
                                                {isExpanded ? (
                                                    <ChevronUp className="text-gray-400" size={24} />
                                                ) : (
                                                    <ChevronDown className="text-gray-400" size={24} />
                                                )}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Expanded Details */}
                                    {isExpanded && (
                                        <div className="border-t-2 border-gray-100 bg-gray-50 p-6">
                                            {session.currencies && session.currencies.length > 0 ? (
                                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                                    {session.currencies.map((curr) => {
                                                        const diff = curr.difference || 0;
                                                        const hasDiff = Math.abs(diff) >= 0.01;

                                                        return (
                                                            <div key={curr.id} className="bg-white rounded-xl p-4 border-2 border-gray-100 shadow-sm">
                                                                <div className="flex justify-between items-center mb-3 pb-2 border-b border-gray-100">
                                                                    <span className="font-bold text-gray-700">{curr.currency_symbol}</span>
                                                                    {isClosed && hasDiff && (
                                                                        <span className={`text-xs font-bold px-2 py-1 rounded-full ${diff > 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                                                                            {diff > 0 ? 'Sobró' : 'Faltó'}
                                                                        </span>
                                                                    )}
                                                                </div>

                                                                <div className="space-y-3">
                                                                    <div>
                                                                        <p className="text-xs text-gray-500 uppercase">Inicial</p>
                                                                        <p className="font-mono font-bold text-gray-800">{formatCurrency(curr.initial_amount, curr.currency_symbol)}</p>
                                                                    </div>

                                                                    {isClosed && (
                                                                        <>
                                                                            <div>
                                                                                <p className="text-xs text-gray-500 uppercase">Esperado</p>
                                                                                <p className="font-mono font-bold text-blue-600">{formatCurrency(curr.final_expected, curr.currency_symbol)}</p>
                                                                            </div>
                                                                            <div>
                                                                                <p className="text-xs text-gray-500 uppercase">Reportado (Cierre)</p>
                                                                                <p className="font-mono font-bold text-purple-600">{formatCurrency(curr.final_reported, curr.currency_symbol)}</p>
                                                                            </div>
                                                                            {hasDiff && (
                                                                                <div className={`mt-2 p-2 rounded-lg ${diff > 0 ? 'bg-green-50' : 'bg-red-50'}`}>
                                                                                    <p className="text-xs text-gray-500 uppercase">Diferencia</p>
                                                                                    <p className={`font-mono font-bold ${diff > 0 ? 'text-green-700' : 'text-red-700'}`}>
                                                                                        {diff > 0 ? '+' : ''}{formatCurrency(diff, curr.currency_symbol)}
                                                                                    </p>
                                                                                </div>
                                                                            )}
                                                                        </>
                                                                    )}
                                                                </div>
                                                            </div>
                                                        );
                                                    })}
                                                </div>
                                            ) : (
                                                /* Fallback for old sessions without concurrency data */
                                                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                                    {/* Initial Cash */}
                                                    <div className="bg-white rounded-xl p-4 border-2 border-blue-100">
                                                        <p className="text-xs font-bold text-gray-500 uppercase mb-2">Efectivo Inicial</p>
                                                        <p className="text-2xl font-black text-blue-600">
                                                            {formatCurrency(session.initial_cash)}
                                                        </p>
                                                        {session.initial_cash_bs && (
                                                            <p className="text-sm text-gray-600 mt-1">
                                                                {formatCurrency(session.initial_cash_bs, 'BS')}
                                                            </p>
                                                        )}
                                                    </div>

                                                    {/* Expected Cash */}
                                                    {isClosed && (
                                                        <div className="bg-white rounded-xl p-4 border-2 border-purple-100">
                                                            <p className="text-xs font-bold text-gray-500 uppercase mb-2">Efectivo Esperado</p>
                                                            <p className="text-2xl font-black text-purple-600">
                                                                {formatCurrency(session.final_cash_expected ?? session.expected_cash)}
                                                            </p>
                                                        </div>
                                                    )}

                                                    {/* Final Cash */}
                                                    {isClosed && (
                                                        <div className="bg-white rounded-xl p-4 border-2 border-green-100">
                                                            <p className="text-xs font-bold text-gray-500 uppercase mb-2">Efectivo Contado</p>
                                                            <p className="text-2xl font-black text-green-600">
                                                                {formatCurrency(session.final_cash_reported ?? session.final_cash)}
                                                            </p>
                                                        </div>
                                                    )}
                                                </div>
                                            )}

                                            {/* Notes */}
                                            {session.notes && (
                                                <div className="mt-4 bg-yellow-50 border-2 border-yellow-200 rounded-xl p-4">
                                                    <p className="text-xs font-bold text-yellow-800 uppercase mb-2">Notas del Cierre</p>
                                                    <p className="text-sm text-yellow-900">{session.notes}</p>
                                                </div>
                                            )}

                                            {/* Difference Alert */}
                                            {isClosed && Math.abs(difference) >= 0.01 && (
                                                <div className={`mt-4 border-2 rounded-xl p-4 flex items-start gap-3 ${difference > 0 ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
                                                    }`}>
                                                    <AlertTriangle className={difference > 0 ? 'text-green-600' : 'text-red-600'} size={20} />
                                                    <div>
                                                        <p className={`font-bold text-sm ${difference > 0 ? 'text-green-900' : 'text-red-900'}`}>
                                                            {difference > 0 ? 'Sobrante Detectado' : 'Faltante Detectado'}
                                                        </p>
                                                        <p className={`text-xs mt-1 ${difference > 0 ? 'text-green-700' : 'text-red-700'}`}>
                                                            Diferencia de {formatCurrency(Math.abs(difference))}.
                                                            {difference > 0 ? ' Hay más dinero del esperado.' : ' Falta dinero en el conteo.'}
                                                        </p>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
};

export default CashHistory;
