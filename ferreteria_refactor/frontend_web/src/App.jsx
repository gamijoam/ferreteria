import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import DashboardLayout from './layouts/DashboardLayout';
import Dashboard from './pages/Dashboard';
import Products from './pages/Products';
import Categories from './pages/Categories';
import Inventory from './pages/Inventory';
import POS from './pages/POS';
import CashClose from './pages/CashClose';
import Settings from './pages/Settings';
import Purchases from './pages/Purchases';
import CreatePurchase from './pages/Purchases/CreatePurchase';
import PurchaseDetail from './pages/Purchases/PurchaseDetail';
import AccountsPayable from './pages/Suppliers/AccountsPayable';
import Suppliers from './pages/Suppliers';
import ReturnsManager from './pages/Returns/ReturnsManager';
import SalesHistory from './pages/SalesHistory';
import CustomerManager from './pages/Customers/CustomerManager';
import AccountsReceivable from './pages/Credit/AccountsReceivable';
import { CartProvider } from './context/CartContext';
import { CashProvider } from './context/CashContext';
import { ConfigProvider } from './context/ConfigContext';

function App() {
  return (
    <AuthProvider>
      <ConfigProvider>
        <CashProvider>
          <CartProvider>
            <Router>
              <Routes>
                <Route path="/login" element={<Login />} />

                <Route element={<ProtectedRoute />}>
                  <Route element={<DashboardLayout />}>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/products" element={<Products />} />
                    <Route path="/categories" element={<Categories />} />
                    <Route path="/inventory" element={<Inventory />} />
                    <Route path="/purchases" element={<Purchases />} />
                    <Route path="/purchases/create" element={<CreatePurchase />} />
                    <Route path="/purchases/:id" element={<PurchaseDetail />} />
                    <Route path="/suppliers" element={<Suppliers />} />
                    <Route path="/accounts-payable" element={<AccountsPayable />} />
                    <Route path="/customers" element={<CustomerManager />} />
                    <Route path="/accounts-receivable" element={<AccountsReceivable />} />
                    <Route path="/returns" element={<ReturnsManager />} />
                    <Route path="/sales-history" element={<SalesHistory />} />
                    <Route path="/pos" element={<POS />} />
                    <Route path="/cash-close" element={<CashClose />} />
                    <Route path="/settings" element={<Settings />} />
                  </Route>
                </Route>
              </Routes>
            </Router>
          </CartProvider>
        </CashProvider>
      </ConfigProvider>
    </AuthProvider>
  );
}

export default App;
