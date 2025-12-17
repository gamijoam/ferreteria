import { createContext, useState, useContext, useEffect } from 'react';
import configService from '../services/configService';
import apiClient from '../config/axios';

const ConfigContext = createContext();

export const ConfigProvider = ({ children }) => {
    const [business, setBusiness] = useState(null);
    const [currencies, setCurrencies] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchConfig = async () => {
        try {
            // Mock data loading if backend routes aren't ready yet or fail
            // In prod, you'd rely on the API success
            try {
                const bizData = await configService.getBusinessInfo();
                setBusiness(bizData);

                // NEW: Use exchange-rates endpoint instead of currencies
                let currData = [];
                try {
                    const ratesRes = await apiClient.get('/config/exchange-rates', {
                        params: { is_active: true }
                    });
                    currData = ratesRes.data || [];
                } catch (e) {
                    console.warn("Exchange rates endpoint failed, trying legacy currencies:", e);
                    // Fallback to old currencies endpoint
                    currData = await configService.getCurrencies();
                }

                // Fallback to debug endpoint if empty (Safety Net)
                if (!Array.isArray(currData) || currData.length === 0) {
                    console.warn("Standard currencies endpoint empty. Trying debug endpoint...");
                    try {
                        const debugRes = await apiClient.get('/config/debug/seed');
                        if (debugRes.data && Array.isArray(debugRes.data.data)) {
                            currData = debugRes.data.data;
                        }
                    } catch (e) {
                        console.error("Debug endpoint failed too", e);
                    }
                }

                setCurrencies(Array.isArray(currData) ? currData : []);
            } catch (apiError) {
                console.warn("Using mock config data due to API error:", apiError);
                // Fallback Mock Data
                setBusiness({
                    name: 'Ferretería El Nuevo Progreso',
                    document_id: 'J-12345678-9',
                    address: 'Av. Principal, Local 1',
                    phone: '0412-1234567'
                });
                setCurrencies([
                    { id: 1, name: 'Dólar', symbol: '$', currency_code: 'USD', currency_symbol: '$', rate: 1.00, is_anchor: true, is_active: true, is_default: true },
                    { id: 2, name: 'Bolívar', symbol: 'Bs', currency_code: 'VES', currency_symbol: 'Bs', rate: 45.00, is_anchor: false, is_active: true, is_default: true }
                ]);
            }
        } catch (err) {
            console.error("Critical Config Error", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const token = localStorage.getItem('token');
        fetchConfig();
    }, [localStorage.getItem('token')]);

    const refreshConfig = () => fetchConfig();

    // Helper to get Exchange Rate by Currency Code (Symbol or ID preferably)
    const getExchangeRate = (symbol) => {
        const curr = currencies.find(c => c.symbol === symbol);
        return curr ? curr.rate : 1;
    };

    const getActiveCurrencies = () => {
        if (!Array.isArray(currencies)) return [];

        // Filter active non-anchor currencies
        const activeCurrencies = currencies.filter(c => c.is_active && !c.is_anchor);

        // Deduplicate by currency_code (group multiple rates for same physical currency)
        const uniqueByCurrencyCode = {};
        activeCurrencies.forEach(curr => {
            const code = curr.currency_code || curr.symbol;
            // If we haven't seen this currency code yet, or if this one is the default rate, use it
            if (!uniqueByCurrencyCode[code] || curr.is_default) {
                uniqueByCurrencyCode[code] = {
                    id: curr.id,
                    name: curr.name || code,
                    symbol: curr.currency_symbol || curr.symbol,
                    currency_code: code,
                    currency_symbol: curr.currency_symbol || curr.symbol,
                    rate: curr.rate,
                    is_active: curr.is_active,
                    is_default: curr.is_default
                };
            }
        });

        // Return array of unique currencies
        return Object.values(uniqueByCurrencyCode);
    };

    const convertPrice = (priceInAnchor, targetSymbol) => {
        const rate = getExchangeRate(targetSymbol);
        return priceInAnchor * rate;
    };

    return (
        <ConfigContext.Provider value={{
            business,
            currencies,
            loading,
            refreshConfig,
            getExchangeRate,
            getActiveCurrencies,
            convertPrice
        }}>
            {children}
        </ConfigContext.Provider>
    );
};

export const useConfig = () => useContext(ConfigContext);
