import { createContext, useState, useEffect, useContext } from 'react';
import apiClient from '../config/axios';
import authService from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (token) {
            // Configure initial interceptor or validate token
            localStorage.setItem('token', token);
            // Optional: Fetch user profile here if the token doesn't contain all info
            // user info is usually decoded from token or fetched
            // For now we will assume authenticated if token exists
            setUser({ username: 'User' }); // Placeholder, usually you decode JWT
        } else {
            localStorage.removeItem('token');
            setUser(null);
        }
        setLoading(false);
    }, [token]);

    // Axios Interceptor
    useEffect(() => {
        const interceptor = apiClient.interceptors.request.use(
            (config) => {
                if (token) {
                    config.headers.Authorization = `Bearer ${token}`;
                }
                return config;
            },
            (error) => Promise.reject(error)
        );

        return () => {
            apiClient.interceptors.request.eject(interceptor);
        };
    }, [token]);

    const login = async (username, password) => {
        try {
            const data = await authService.login(username, password);
            // FastAPI returns { access_token, token_type }
            setToken(data.access_token);
            localStorage.setItem('token', data.access_token);
            return true;
        } catch (error) {
            console.error("Login failed", error);
            throw error;
        }
    };

    const logout = () => {
        setToken(null);
        setUser(null);
        localStorage.removeItem('token');
        // We don't need to manually redirect here if we use ProtectedRoute correctly and trigger a re-render
        // But typically you might redirect to /login
    };

    return (
        <AuthContext.Provider value={{ user, token, login, logout, loading }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
