import { useState, useEffect } from 'react';
import { Calendar, Search, TrendingUp, TrendingDown, AlertTriangle, DollarSign, Clock, User, CheckCircle, XCircle, ChevronDown, ChevronUp, Minus, Plus } from 'lucide-react';
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
        const expected = parseFloat(session.final_cash_expected || session.expected_cash || 0);
        const actual = parseFloat(session.final_cash_reported || session.final_cash || 0);
        return actual - expected;
    };

    // Calculate KPIs for the period
    const calculateKPIs = () => {
        const closedSessions = sessions.filter(s => s.status === 'CLOSED');

        let totalShortages = 0;
        let totalOverages = 0;
        let totalCashSales = 0;

        closedSessions.forEach(session => {
            const diff = calculateDifference(session);
            if (diff < -0.01) {
                totalShortages += Math.abs(diff);
            } else if (diff > 0.01) {
                totalOverages += diff;
            }

            // Calculate cash sales (final_expected - initial)
            const expected = parseFloat(session.final_cash_expected || session.expected_cash || 0);
            const initial = parseFloat(session.initial_cash || 0);
            const sales = expected - initial;
            if (sales > 0) {
                totalCashSales += sales;
            }
        });

        return { totalShortages, totalOverages, totalCashSales };
    };

    const kpis = calculateKPIs();

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
                                Panel de Auditoría de Cajas
                            </h1>
                            <p className="text-gray-600 mt-2">Monitoreo y control de cierres de caja</p>
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

                {/* KPI Cards */}
                {!loading && sessions.length > 0 && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                        {/* Total Shortages */}
                        <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-2xl shadow-xl p-6 text-white">
                            <div className="flex items-center justify-between mb-4">
                                <div className="p-3 bg-white/20 rounded-xl">
                                    <TrendingDown size={28} />
                                </div>
                                <AlertTriangle size={24} className="opacity-70" />
                            </div>
                            <p className="text-sm font-medium opacity-90 mb-1">Total Faltantes del Período</p>
                            <p className="text-3xl font-black">{formatCurrency(kpis.totalShortages)}</p>
                            <p className="text-xs mt-2 opacity-75">Dinero faltante en cierres</p>
                        </div>

                        {/* Total Overages */}
                        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl shadow-xl p-6 text-white">
                            <div className="flex items-center justify-between mb-4">
                                <div className="p-3 bg-white/20 rounded-xl">
                                    <TrendingUp size={28} />
                                </div>
                                <CheckCircle size={24} className="opacity-70" />
                            </div>
                            <p className="text-sm font-medium opacity-90 mb-1">Total Sobrantes del Período</p>
                            <p className="text-3xl font-black">{formatCurrency(kpis.totalOverages)}</p>
                            <p className="text-xs mt-2 opacity-75">Dinero sobrante en cierres</p>
                        </div>

                        {/* Total Cash Sales */}
                        <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl shadow-xl p-6 text-white">
                            <div className="flex items-center justify-between mb-4">
                                <div className="p-3 bg-white/20 rounded-xl">
                                    <DollarSign size={28} />
                                </div>
                                <Plus size={24} className="opacity-70" />
                            </div>
                            <p className="text-sm font-medium opacity-90 mb-1">Total Ventas en Efectivo</p>
                            <p className="text-3xl font-black">{formatCurrency(kpis.totalCashSales)}</p>
                            <p className="text-xs mt-2 opacity-75">Ingresos en efectivo del período</p>
                        </div>
                    </div>
                )}

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

                {/* Empty State */}
                {!loading && sessions.length === 0 && (
                    <div className="bg-white rounded-2xl shadow-sm p-12 text-center">
                        <DollarSign className="mx-auto text-gray-300 mb-4" size={64} />
                        <p className="text-gray-500 font-medium text-lg">No se encontraron sesiones de caja</p>
                        <p className="text-gray-400 text-sm mt-2">Intenta con un rango de fechas diferente</p>
                    </div>
                )}

                {/* Professional Table */}
                {!loading && sessions.length > 0 && (
                    <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead className="bg-gradient-to-r from-gray-800 to-gray-900 text-white">
                                    <tr>
                                        <th className="px-6 py-4 text-left text-xs font-bold uppercase tracking-wider">Fecha/Hora</th>
                                        <th className="px-6 py-4 text-left text-xs font-bold uppercase tracking-wider">Cajero</th>
                                        <th className="px-6 py-4 text-right text-xs font-bold uppercase tracking-wider">Inicial</th>
                                        <th className="px-6 py-4 text-right text-xs font-bold uppercase tracking-wider">Ventas</th>
                                        <th className="px-6 py-4 text-right text-xs font-bold uppercase tracking-wider">Esperado</th>
                                        <th className="px-6 py-4 text-right text-xs font-bold uppercase tracking-wider">Real</th>
                                        <th className="px-6 py-4 text-right text-xs font-bold uppercase tracking-wider">Diferencia</th>
                                        <th className="px-6 py-4 text-center text-xs font-bold uppercase tracking-wider">Estado</th>
                                        <th className="px-6 py-4"></th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200">
                                    {sessions.map((session) => {
                                        const difference = calculateDifference(session);
                                        const isExpanded = expandedId === session.id;
                                        const isClosed = session.status === 'CLOSED';

                                        const initial = parseFloat(session.initial_cash || 0);
                                        const expected = parseFloat(session.final_cash_expected || session.expected_cash || 0);
                                        const sales = expected - initial;

                                        // Determine difference styling
                                        let diffClass = 'bg-green-50 text-green-700 border-l-4 border-green-500';
                                        let diffIcon = <CheckCircle size={18} />;

                                        if (Math.abs(difference) < 0.01) {
                                            diffClass = 'bg-green-50 text-green-700 border-l-4 border-green-500';
                                            diffIcon = <CheckCircle size={18} />;
                                        } else if (difference < 0) {
                                            diffClass = 'bg-red-50 text-red-700 border-l-4 border-red-500';
                                            diffIcon = <AlertTriangle size={18} />;
                                        } else {
                                            diffClass = 'bg-green-50 text-green-700 border-l-4 border-green-500';
                                            diffIcon = <TrendingUp size={18} />;
                                        }

                                        return (
                                            <>
                                                <tr
                                                    key={session.id}
                                                    className="hover:bg-gray-50 transition-colors cursor-pointer"
                                                    onClick={() => toggleExpand(session.id)}
                                                >
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <div className="flex items-center gap-2">
                                                            <Clock size={16} className="text-gray-400" />
                                                            <div>
                                                                <div className="text-sm font-medium text-gray-900">
                                                                    {formatDate(session.opened_at)}
                                                                </div>
                                                                {isClosed && session.closed_at && (
                                                                    <div className="text-xs text-gray-500">
                                                                        Cerrado: {formatDate(session.closed_at)}
                                                                    </div>
                                                                )}
                                                            </div>
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <div className="flex items-center gap-2">
                                                            <User size={16} className="text-gray-400" />
                                                            <span className="text-sm font-medium text-gray-900">
                                                                {session.user?.full_name || session.user?.username || `Usuario #${session.user_id}`}
                                                            </span>
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-right">
                                                        <span className="text-sm font-mono font-semibold text-gray-700">
                                                            {formatCurrency(session.initial_cash)}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-right">
                                                        <span className="text-sm font-mono font-semibold text-blue-600">
                                                            {formatCurrency(sales)}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-right">
                                                        <span className="text-sm font-mono font-semibold text-purple-600">
                                                            {formatCurrency(expected)}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-right">
                                                        <span className="text-sm font-mono font-semibold text-gray-900">
                                                            {formatCurrency(session.final_cash_reported || session.final_cash)}
                                                        </span>
                                                    </td>
                                                    <td className={`px-6 py-4 whitespace-nowrap text-right ${diffClass}`}>
                                                        <div className="flex items-center justify-end gap-2">
                                                            {diffIcon}
                                                            <span className="text-sm font-mono font-bold">
                                                                {Math.abs(difference) < 0.01 ? '$0.00' :
                                                                    difference > 0 ? `+${formatCurrency(difference)}` :
                                                                        formatCurrency(difference)}
                                                            </span>
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-center">
                                                        <span className={`px-3 py-1 rounded-full text-xs font-bold ${isClosed ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                                                            }`}>
                                                            {isClosed ? 'CERRADA' : 'ABIERTA'}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-center">
                                                        {isExpanded ? (
                                                            <ChevronUp className="text-gray-400" size={20} />
                                                        ) : (
                                                            <ChevronDown className="text-gray-400" size={20} />
                                                        )}
                                                    </td>
                                                </tr>

                                                {/* Expanded Details Row */}
                                                {isExpanded && (
                                                    <tr>
                                                        <td colSpan="9" className="px-6 py-6 bg-gray-50 border-t-2 border-gray-200">
                                                            <div className="space-y-4">
                                                                {/* Currency Breakdown */}
                                                                {session.currencies && session.currencies.length > 0 ? (
                                                                    <div>
                                                                        <h4 className="text-sm font-bold text-gray-700 mb-3 uppercase">Desglose por Moneda</h4>
                                                                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                                                            {session.currencies.map((curr) => {
                                                                                const diff = curr.difference || 0;
                                                                                const hasDiff = Math.abs(diff) >= 0.01;

                                                                                return (
                                                                                    <div key={curr.id} className="bg-white rounded-xl p-4 border-2 border-gray-200 shadow-sm">
                                                                                        <div className="flex justify-between items-center mb-3 pb-2 border-b border-gray-100">
                                                                                            <span className="font-bold text-gray-700">{curr.currency_symbol}</span>
                                                                                            {isClosed && hasDiff && (
                                                                                                <span className={`text-xs font-bold px-2 py-1 rounded-full ${diff > 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                                                                                                    }`}>
                                                                                                    {diff > 0 ? 'Sobró' : 'Faltó'}
                                                                                                </span>
                                                                                            )}
                                                                                        </div>

                                                                                        <div className="space-y-2">
                                                                                            <div>
                                                                                                <p className="text-xs text-gray-500 uppercase">Inicial</p>
                                                                                                <p className="font-mono font-bold text-gray-800">
                                                                                                    {formatCurrency(curr.initial_amount, curr.currency_symbol)}
                                                                                                </p>
                                                                                            </div>

                                                                                            {isClosed && (
                                                                                                <>
                                                                                                    <div>
                                                                                                        <p className="text-xs text-gray-500 uppercase">Esperado</p>
                                                                                                        <p className="font-mono font-bold text-blue-600">
                                                                                                            {formatCurrency(curr.final_expected, curr.currency_symbol)}
                                                                                                        </p>
                                                                                                    </div>
                                                                                                    <div>
                                                                                                        <p className="text-xs text-gray-500 uppercase">Reportado</p>
                                                                                                        <p className="font-mono font-bold text-purple-600">
                                                                                                            {formatCurrency(curr.final_reported, curr.currency_symbol)}
                                                                                                        </p>
                                                                                                    </div>
                                                                                                    {hasDiff && (
                                                                                                        <div className={`p-2 rounded-lg ${diff > 0 ? 'bg-green-50' : 'bg-red-50'}`}>
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
                                                                    </div>
                                                                ) : (
                                                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                                                        <div className="bg-white rounded-xl p-4 border-2 border-blue-100">
                                                                            <p className="text-xs font-bold text-gray-500 uppercase mb-2">Efectivo Inicial</p>
                                                                            <p className="text-xl font-black text-blue-600">
                                                                                {formatCurrency(session.initial_cash)}
                                                                            </p>
                                                                        </div>

                                                                        {isClosed && (
                                                                            <>
                                                                                <div className="bg-white rounded-xl p-4 border-2 border-purple-100">
                                                                                    <p className="text-xs font-bold text-gray-500 uppercase mb-2">Efectivo Esperado</p>
                                                                                    <p className="text-xl font-black text-purple-600">
                                                                                        {formatCurrency(expected)}
                                                                                    </p>
                                                                                </div>

                                                                                <div className="bg-white rounded-xl p-4 border-2 border-green-100">
                                                                                    <p className="text-xs font-bold text-gray-500 uppercase mb-2">Efectivo Contado</p>
                                                                                    <p className="text-xl font-black text-green-600">
                                                                                        {formatCurrency(session.final_cash_reported || session.final_cash)}
                                                                                    </p>
                                                                                </div>
                                                                            </>
                                                                        )}
                                                                    </div>
                                                                )}

                                                                {/* Notes */}
                                                                {session.notes && (
                                                                    <div className="bg-yellow-50 border-2 border-yellow-200 rounded-xl p-4">
                                                                        <p className="text-xs font-bold text-yellow-800 uppercase mb-2">Notas del Cierre</p>
                                                                        <p className="text-sm text-yellow-900">{session.notes}</p>
                                                                    </div>
                                                                )}

                                                                {/* Difference Alert */}
                                                                {isClosed && Math.abs(difference) >= 0.01 && (
                                                                    <div className={`border-2 rounded-xl p-4 flex items-start gap-3 ${difference > 0 ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
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
                                                        </td>
                                                    </tr>
                                                )}
                                            </>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default CashHistory;
