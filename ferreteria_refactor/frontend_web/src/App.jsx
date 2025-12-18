import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Unauthorized from './pages/Unauthorized';
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
import UsersManager from './pages/Users/UsersManager';
import CashHistory from './pages/CashHistory';
import { CartProvider } from './context/CartContext';
import { CashProvider } from './context/CashContext';
import { ConfigProvider } from './context/ConfigContext';
import { WebSocketProvider } from './context/WebSocketContext';

function App() {
  return (
    <AuthProvider>
      <WebSocketProvider>
        <ConfigProvider>
          <CashProvider>
            <CartProvider>
              <Router>
                <Routes>
                  <Route path="/login" element={<Login />} />
                  <Route path="/unauthorized" element={<Unauthorized />} />

                  {/* Protected Routes */}
                  <Route element={<ProtectedRoute />}>
                    <Route element={<DashboardLayout />}>
                      <Route path="/" element={<Dashboard />} />

                      {/* Inventory - ADMIN or WAREHOUSE */}
                      <Route path="/products" element={
                        <ProtectedRoute roles={['ADMIN', 'WAREHOUSE']}>
                          <Products />
                        </ProtectedRoute>
                      } />
                      <Route path="/categories" element={
                        <ProtectedRoute roles={['ADMIN', 'WAREHOUSE']}>
                          <Categories />
                        </ProtectedRoute>
                      } />
                      <Route path="/inventory" element={
                        <ProtectedRoute roles={['ADMIN', 'WAREHOUSE']}>
                          <Inventory />
                        </ProtectedRoute>
                      } />

                      {/* Sales - ADMIN or CASHIER */}
                      <Route path="/pos" element={
                        <ProtectedRoute roles={['ADMIN', 'CASHIER']}>
                          <POS />
                        </ProtectedRoute>
                      } />
                      <Route path="/sales-history" element={
                        <ProtectedRoute roles={['ADMIN', 'CASHIER']}>
                          <SalesHistory />
                        </ProtectedRoute>
                      } />
                      <Route path="/returns" element={
                        <ProtectedRoute roles={['ADMIN', 'CASHIER']}>
                          <ReturnsManager />
                        </ProtectedRoute>
                      } />
                      <Route path="/cash-close" element={
                        <ProtectedRoute roles={['ADMIN', 'CASHIER']}>
                          <CashClose />
                        </ProtectedRoute>
                      } />

                      {/* Finance - All roles can view */}
                      <Route path="/customers" element={<CustomerManager />} />
                      <Route path="/accounts-receivable" element={<AccountsReceivable />} />
                      <Route path="/suppliers" element={<Suppliers />} />
                      <Route path="/accounts-payable" element={<AccountsPayable />} />

                      {/* Operations - All roles can view */}
                      <Route path="/purchases" element={<Purchases />} />
                      <Route path="/purchases/create" element={<CreatePurchase />} />
                      <Route path="/purchases/:id" element={<PurchaseDetail />} />

                      {/* Admin Only */}
                      <Route path="/settings" element={
                        <ProtectedRoute roles="ADMIN">
                          <Settings />
                        </ProtectedRoute>
                      } />
                      <Route path="/users" element={
                        <ProtectedRoute roles="ADMIN">
                          <UsersManager />
                        </ProtectedRoute>
                      } />
                      <Route path="/cash-history" element={
                        <ProtectedRoute roles="ADMIN">
                          <CashHistory />
                        </ProtectedRoute>
                      } />
                    </Route>
                  </Route>
                </Routes>
              </Router>
            </CartProvider>
          </CashProvider>
        </ConfigProvider>
      </WebSocketProvider>
    </AuthProvider>
  );
}

export default App;
