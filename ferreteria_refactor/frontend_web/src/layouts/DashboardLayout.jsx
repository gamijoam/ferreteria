import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useConfig } from '../context/ConfigContext';
import RoleGuard from '../components/RoleGuard';
import {
    LayoutDashboard,
    Package,
    ShoppingCart,
    Settings as SettingsIcon,
    LogOut,
    FolderTree,
    ShoppingBag,
    DollarSign,
    Truck,
    Wallet,
    RotateCcw,
    Archive,
    User,
    History,
    ChevronDown,
    ChevronRight,
    Users,
    FileText,
    ClipboardList
} from 'lucide-react';

const DashboardLayout = () => {
    const { user, logout } = useAuth();
    const { business } = useConfig(); // Get business info
    const navigate = useNavigate();
    const location = useLocation();

    // Collapsible menu states
    const [openSections, setOpenSections] = useState({
        inventory: true,
        sales: true,
        finance: true,
        operations: false
    });

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const toggleSection = (section) => {
        setOpenSections(prev => ({
            ...prev,
            [section]: !prev[section]
        }));
    };

    const isActive = (path) => location.pathname === path;

    return (
        <div className="flex h-screen bg-gray-100">
            {/* Sidebar */}
            <aside className="w-64 bg-slate-800 text-white flex flex-col overflow-y-auto">
                <div className="p-4 border-b border-slate-700">
                    <h1 className="text-xl font-bold truncate" title={business?.name || 'Ferretería Pro'}>
                        {business?.name || 'Ferretería Pro'}
                    </h1>
                </div>

                <nav className="flex-1 p-4 space-y-1">
                    {/* Dashboard */}
                    <Link
                        to="/"
                        className={`flex items-center space-x-3 p-3 rounded transition-colors ${isActive('/') ? 'bg-blue-600' : 'hover:bg-slate-700'
                            }`}
                    >
                        <LayoutDashboard size={20} />
                        <span>Dashboard</span>
                    </Link>

                    {/* Inventario y Productos - ADMIN or WAREHOUSE */}
                    <RoleGuard allowed={['ADMIN', 'WAREHOUSE']}>
                        <div>
                            <button
                                onClick={() => toggleSection('inventory')}
                                className="flex items-center justify-between w-full p-3 rounded hover:bg-slate-700 transition-colors"
                            >
                                <div className="flex items-center space-x-3">
                                    <Package size={20} />
                                    <span className="font-medium">Inventario</span>
                                </div>
                                {openSections.inventory ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                            </button>
                            {openSections.inventory && (
                                <div className="ml-4 mt-1 space-y-1">
                                    <Link to="/products" className={`flex items-center space-x-3 p-2 pl-4 rounded text-sm transition-colors ${isActive('/products') ? 'bg-blue-600' : 'hover:bg-slate-700'}`}>
                                        <Package size={16} />
                                        <span>Productos</span>
                                    </Link>
                                    <Link to="/categories" className={`flex items-center space-x-3 p-2 pl-4 rounded text-sm transition-colors ${isActive('/categories') ? 'bg-blue-600' : 'hover:bg-slate-700'}`}>
                                        <FolderTree size={16} />
                                        <span>Categorías</span>
                                    </Link>
                                    <Link to="/inventory" className={`flex items-center space-x-3 p-2 pl-4 rounded text-sm transition-colors ${isActive('/inventory') ? 'bg-blue-600' : 'hover:bg-slate-700'}`}>
                                        <Archive size={16} />
                                        <span>Kardex</span>
                                    </Link>
                                </div>
                            )}
                        </div>
                    </RoleGuard>

                    {/* Ventas - ADMIN or CASHIER */}
                    <RoleGuard allowed={['ADMIN', 'CASHIER']}>
                        <div>
                            <button
                                onClick={() => toggleSection('sales')}
                                className="flex items-center justify-between w-full p-3 rounded hover:bg-slate-700 transition-colors"
                            >
                                <div className="flex items-center space-x-3">
                                    <ShoppingCart size={20} />
                                    <span className="font-medium">Ventas</span>
                                </div>
                                {openSections.sales ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                            </button>
                            {openSections.sales && (
                                <div className="ml-4 mt-1 space-y-1">
                                    <Link to="/pos" className={`flex items-center space-x-3 p-2 pl-4 rounded text-sm transition-colors ${isActive('/pos') ? 'bg-blue-600' : 'hover:bg-slate-700'}`}>
                                        <ShoppingCart size={16} />
                                        <span>Punto de Venta</span>
                                    </Link>
                                    <Link to="/sales-history" className={`flex items-center space-x-3 p-2 pl-4 rounded text-sm transition-colors ${isActive('/sales-history') ? 'bg-blue-600' : 'hover:bg-slate-700'}`}>
                                        <History size={16} />
                                        <span>Historial</span>
                                    </Link>
                                    <Link to="/returns" className={`flex items-center space-x-3 p-2 pl-4 rounded text-sm transition-colors ${isActive('/returns') ? 'bg-blue-600' : 'hover:bg-slate-700'}`}>
                                        <RotateCcw size={16} />
                                        <span>Devoluciones</span>
                                    </Link>
                                </div>
                            )}
                        </div>
                    </RoleGuard>

                    {/* Finanzas */}
                    <div>
                        <button
                            onClick={() => toggleSection('finance')}
                            className="flex items-center justify-between w-full p-3 rounded hover:bg-slate-700 transition-colors"
                        >
                            <div className="flex items-center space-x-3">
                                <DollarSign size={20} />
                                <span className="font-medium">Finanzas</span>
                            </div>
                            {openSections.finance ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                        </button>
                        {openSections.finance && (
                            <div className="ml-4 mt-1 space-y-1">
                                <Link to="/customers" className={`flex items-center space-x-3 p-2 pl-4 rounded text-sm transition-colors ${isActive('/customers') ? 'bg-blue-600' : 'hover:bg-slate-700'}`}>
                                    <Users size={16} />
                                    <span>Clientes</span>
                                </Link>
                                <Link to="/accounts-receivable" className={`flex items-center space-x-3 p-2 pl-4 rounded text-sm transition-colors ${isActive('/accounts-receivable') ? 'bg-blue-600' : 'hover:bg-slate-700'}`}>
                                    <FileText size={16} />
                                    <span>Cuentas por Cobrar</span>
                                </Link>
                                <Link to="/suppliers" className={`flex items-center space-x-3 p-2 pl-4 rounded text-sm transition-colors ${isActive('/suppliers') ? 'bg-blue-600' : 'hover:bg-slate-700'}`}>
                                    <Truck size={16} />
                                    <span>Proveedores</span>
                                </Link>
                                <Link to="/accounts-payable" className={`flex items-center space-x-3 p-2 pl-4 rounded text-sm transition-colors ${isActive('/accounts-payable') ? 'bg-blue-600' : 'hover:bg-slate-700'}`}>
                                    <Wallet size={16} />
                                    <span>Cuentas por Pagar</span>
                                </Link>
                            </div>
                        )}
                    </div>

                    {/* Operaciones */}
                    <div>
                        <button
                            onClick={() => toggleSection('operations')}
                            className="flex items-center justify-between w-full p-3 rounded hover:bg-slate-700 transition-colors"
                        >
                            <div className="flex items-center space-x-3">
                                <ShoppingBag size={20} />
                                <span className="font-medium">Operaciones</span>
                            </div>
                            {openSections.operations ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                        </button>
                        {openSections.operations && (
                            <div className="ml-4 mt-1 space-y-1">
                                <Link to="/purchases" className={`flex items-center space-x-3 p-2 pl-4 rounded text-sm transition-colors ${isActive('/purchases') ? 'bg-blue-600' : 'hover:bg-slate-700'}`}>
                                    <ShoppingBag size={16} />
                                    <span>Compras</span>
                                </Link>
                            </div>
                        )}
                    </div>

                    {/* Users - ADMIN ONLY */}
                    <RoleGuard allowed="ADMIN">
                        <Link to="/users" className={`flex items-center space-x-3 p-3 rounded transition-colors ${isActive('/users') ? 'bg-blue-600' : 'hover:bg-slate-700'}`}>
                            <Users size={20} />
                            <span>Usuarios</span>
                        </Link>
                        <Link to="/cash-history" className={`flex items-center space-x-3 p-3 rounded transition-colors ${isActive('/cash-history') ? 'bg-blue-600' : 'hover:bg-slate-700'}`}>
                            <History size={20} />
                            <span>Historial de Caja</span>
                        </Link>
                        <Link to="/audit-logs" className={`flex items-center space-x-3 p-3 rounded transition-colors ${isActive('/audit-logs') ? 'bg-blue-600' : 'hover:bg-slate-700'}`}>
                            <ClipboardList size={20} />
                            <span>Auditoría</span>
                        </Link>
                    </RoleGuard>

                    {/* Settings - ADMIN ONLY */}
                    <RoleGuard allowed="ADMIN">
                        <Link to="/settings" className={`flex items-center space-x-3 p-3 rounded transition-colors ${isActive('/settings') ? 'bg-blue-600' : 'hover:bg-slate-700'}`}>
                            <SettingsIcon size={20} />
                            <span>Configuración</span>
                        </Link>
                    </RoleGuard>
                </nav>

                <div className="p-4 border-t border-slate-700">
                    <button
                        onClick={handleLogout}
                        className="flex items-center space-x-3 p-3 rounded hover:bg-red-600 transition-colors w-full"
                    >
                        <LogOut size={20} />
                        <span>Cerrar Sesión</span>
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {/* Header */}
                <header className="bg-white shadow-sm h-16 flex items-center justify-between px-6">
                    <h2 className="text-xl font-semibold text-gray-800">Panel de Control</h2>
                    <div className="flex items-center space-x-6">
                        {/* Quick Rate Widget */}
                        <div className="flex items-center bg-blue-50 px-3 py-1 rounded-full border border-blue-100">
                            <div className="text-xs font-bold text-blue-800 mr-2">TASA BCV</div>
                            <div className="text-sm font-mono font-bold text-blue-600">
                                {useConfig().getExchangeRate('VES').toFixed(2)} Bs
                            </div>
                        </div>

                        <div className="flex items-center space-x-2 text-gray-700">
                            <User size={20} />
                            <div className="flex flex-col items-end">
                                <span className="font-medium">{user?.username || 'Usuario'}</span>
                                <span className="text-xs text-gray-500">{user?.role || 'CASHIER'}</span>
                            </div>
                        </div>
                    </div>
                </header>

                {/* Page Content */}
                <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

export default DashboardLayout;
