import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useConfig } from '../context/ConfigContext';
import {
    LayoutDashboard,
    Package,
    ShoppingCart,
    Archive,
    Settings as SettingsIcon,
    LogOut,
    User,
    FolderTree,
    ShoppingBag,
    Wallet,
    Truck
} from 'lucide-react';

const DashboardLayout = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="flex h-screen bg-gray-100">
            {/* Sidebar */}
            <aside className="w-64 bg-slate-800 text-white flex flex-col">
                <div className="p-4 border-b border-slate-700">
                    <h1 className="text-xl font-bold">Ferretería Pro</h1>
                </div>

                <nav className="flex-1 p-4 space-y-2">
                    <Link to="/" className="flex items-center space-x-3 p-3 rounded hover:bg-slate-700 transition-colors">
                        <LayoutDashboard size={20} />
                        <span>Dashboard</span>
                    </Link>
                    <Link to="/products" className="flex items-center space-x-3 p-3 rounded hover:bg-slate-700 transition-colors">
                        <Package size={20} />
                        <span>Productos</span>
                    </Link>
                    <Link to="/categories" className="flex items-center space-x-3 p-3 rounded hover:bg-slate-700 transition-colors">
                        <FolderTree size={20} />
                        <span>Categorías</span>
                    </Link>
                    <Link to="/purchases" className="flex items-center space-x-3 p-3 rounded hover:bg-slate-700 transition-colors">
                        <ShoppingBag size={20} />
                        <span>Compras</span>
                    </Link>
                    <Link to="/suppliers" className="flex items-center space-x-3 p-3 rounded hover:bg-slate-700 transition-colors">
                        <Truck size={20} />
                        <span>Proveedores</span>
                    </Link>
                    <Link to="/accounts-payable" className="flex items-center space-x-3 p-3 rounded hover:bg-slate-700 transition-colors">
                        <Wallet size={20} />
                        <span>Cuentas por Pagar</span>
                    </Link>
                    <Link to="/pos" className="flex items-center space-x-3 p-3 rounded hover:bg-slate-700 transition-colors">
                        <ShoppingCart size={20} />
                        <span>Ventas (POS)</span>
                    </Link>
                    <Link to="/inventory" className="flex items-center px-4 py-3 text-gray-300 hover:bg-slate-700 hover:text-white transition-colors">
                        <Archive className="mr-3" size={20} /> Inventario
                    </Link>
                    <Link to="/settings" className="flex items-center px-4 py-3 text-gray-300 hover:bg-slate-700 hover:text-white transition-colors">
                        <SettingsIcon className="mr-3" size={20} /> Configuración
                    </Link>
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
                            <span>{user?.username || 'Usuario'}</span>
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
