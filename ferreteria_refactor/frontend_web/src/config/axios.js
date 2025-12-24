import axios from 'axios';

// --- CAMBIO PARA SOPORTE HÍBRIDO (LOCAL/SAAS) ---
// Al usar '/api/v1', el navegador resolverá automáticamente:
// - En local: http://localhost:8000/api/v1 (gracias al proxy de Vite)
// - En VPS: https://demo.invensoft.lat/api/v1 (gracias a Nginx/Traefik)
const baseURL = '/api/v1';

const apiClient = axios.create({
    baseURL,
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    },
});

import toast from 'react-hot-toast';

// Request Interceptor (Add Token)
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response Interceptor (Error Handling)
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        const status = error.response ? error.response.status : null;

        if (status === 401) {
            // Avoid redirect loop if already on login page or if error is from login attempt
            const isLoginRequest = error.config.url.includes('/auth/token');
            const isLoginPage = window.location.pathname === '/login';

            if (!isLoginRequest && !isLoginPage) {
                // Unauthorized: Clear token and redirect
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                toast.error('Sesión expirada. Por favor inicie sesión.');
                setTimeout(() => {
                    window.location.href = '/login';
                }, 1500);
            } else if (isLoginRequest) {
                // For login failure, just clear potential stale tokens, but let the component handle the error display
                localStorage.removeItem('token');
                localStorage.removeItem('user');
            }
        } else if (status === 403) {
            // Forbidden
            toast.error('No tienes permisos para realizar esta acción.');
        } else if (!status) {
            // Network Error
            toast.error('Error de conexión con el servidor.');
        }

        return Promise.reject(error);
    }
);

export default apiClient;
