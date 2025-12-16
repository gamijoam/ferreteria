import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import DashboardLayout from './layouts/DashboardLayout';
import Products from './pages/Products';
import Inventory from './pages/Inventory';
import POS from './pages/POS';
import CashClose from './pages/CashClose';
import { CartProvider } from './context/CartContext';
import { CashProvider } from './context/CashContext';

const DashboardPlaceholder = () => (
  <div className="text-center p-10">
    <h1 className="text-3xl font-bold text-gray-800 mb-4">Bienvenido al Sistema Web</h1>
    <p className="text-gray-600">Selecciona una opción del menú lateral para comenzar.</p>
  </div>
);

function App() {
  return (
    <AuthProvider>
      <CashProvider>
        <CartProvider>
          <Router>
            <Routes>
              <Route path="/login" element={<Login />} />

              <Route element={<ProtectedRoute />}>
                <Route element={<DashboardLayout />}>
                  <Route path="/" element={<DashboardPlaceholder />} />
                  <Route path="/products" element={<Products />} />
                  <Route path="/inventory" element={<Inventory />} />
                  <Route path="/pos" element={<POS />} />
                  <Route path="/cash-close" element={<CashClose />} />
                </Route>
              </Route>
            </Routes>
          </Router>
        </CartProvider>
      </CashProvider>
    </AuthProvider>
  );
}

export default App;
