import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';

const DashboardPlaceholder = () => (
  <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
    <div className="bg-white p-6 rounded-lg shadow-md max-w-lg w-full text-center">
      <h1 className="text-3xl font-bold text-blue-600 mb-4">Bienvenido al Sistema Web</h1>
      <p className="text-gray-600">Has iniciado sesión correctamente.</p>
    </div>
  </div>
);

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route path="/" element={<ProtectedRoute />}>
            <Route index element={<DashboardPlaceholder />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
