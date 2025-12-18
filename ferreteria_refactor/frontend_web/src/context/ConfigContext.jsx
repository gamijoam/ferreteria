import { createContext, useState, useContext, useEffect } from 'react';
import configService from '../services/configService';
import apiClient from '../config/axios';
import { useWebSocket } from './WebSocketContext';

const ConfigContext = createContext();

export const ConfigProvider = ({ children }) => {
    const [business, setBusiness] = useState(null);
    const [currencies, setCurrencies] = useState([]);
    const [loading, setLoading] = useState(true);
    const { subscribe } = useWebSocket();

    // WebSocket Subscriptions for Real-Time Updates
    useEffect(() => {
        // Subscribe to Exchange Rate Updates
        const unsubUpdate = subscribe('exchange_rate:updated', (updatedRate) => {
            console.log('📡 Real-time Rate Update:', updatedRate);
            setCurrencies(prev => {
                // If it's default, we need to update others too (set them to false)
                // But simplified: just update the one or potentially reload all if complex
                // For now, let's just update the matching one

                // If updatedRate became default, others must be unset
                if (updatedRate.is_default) {
                    return prev.map(c => ({
                        ...c,
                        // Update the rate and default status
                        rate: c.id === updatedRate.id ? updatedRate.rate : c.rate,
                        is_default: c.id === updatedRate.id
                    }));
                }

                return prev.map(c =>
                    c.id === updatedRate.id ? { ...c, ...updatedRate } : c
                );
            });
        });

        // Subscribe to New Rates
        const unsubCreate = subscribe('exchange_rate:created', (newRate) => {
            console.log('📡 Real-time Rate Created:', newRate);
            setCurrencies(prev => {
                if (newRate.is_default) {
                    // Unset other defaults
                    const updated = prev.map(c => ({ ...c, is_default: false }));
                    return [...updated, newRate];
                }
                return [...prev, newRate];
            });
        });

        return () => {
            unsubUpdate();
            unsubCreate();
        };
    }, [subscribe]);

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

                setCurrencies(Array.isArray(currData) ? currData.map(c => ({ ...c, rate: parseFloat(c.rate) })) : []);
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
        if (!symbol) return 1;
        const normalize = s => String(s).trim().toUpperCase();
        const target = normalize(symbol);

        const curr = currencies.find(c =>
            normalize(c.symbol) === target ||
            normalize(c.currency_symbol) === target ||
            normalize(c.currency_code) === target
        );
        return curr ? parseFloat(curr.rate) : 1;
    };

    const getActiveCurrencies = () => {
        if (!Array.isArray(currencies)) return [];

        // Filter active non-anchor currencies
        const activeCurrencies = currencies.filter(c => c.is_active && !c.is_anchor);

        // Deduplicate by currency_code (group multiple rates for same physical currency)
        const uniqueByCurrencyCode = {};
        activeCurrencies.forEach(curr => {
            // Normalize Code/Symbol to handle "VES" vs "VES " mismatches
            const code = (curr.currency_code || curr.symbol || '').trim().toUpperCase();

            // PRIORITY LOGIC:
            // 1. Current iteration IS default -> Overwrite everything.
            // 2. We don't have this code yet -> Add it.
            // 3. We have it (non-default), and current (non-default) has HIGHER rate -> Upgrade to higher rate (heuristic).

            const existing = uniqueByCurrencyCode[code];

            if (curr.is_default) {
                // Priority 1: Default always wins
                uniqueByCurrencyCode[code] = { ...formatCurrency(curr, code) };
            } else if (!existing) {
                // Priority 2: New entry
                uniqueByCurrencyCode[code] = { ...formatCurrency(curr, code) };
            } else if (!existing.is_default && curr.rate > existing.rate) {
                // Priority 3: Higher rate wins among non-defaults
                uniqueByCurrencyCode[code] = { ...formatCurrency(curr, code) };
            }
        });

        function formatCurrency(c, code) {
            return {
                id: c.id,
                name: c.name || code,
                symbol: (c.currency_symbol || c.symbol || '').trim(),
                currency_code: code,
                currency_symbol: (c.currency_symbol || c.symbol || '').trim(),
                rate: c.rate,
                is_active: c.is_active,
                is_default: c.is_default
            };
        }

        // Return array of unique currencies
        return Object.values(uniqueByCurrencyCode);
    };

    const convertPrice = (priceInAnchor, targetSymbol) => {
        const rate = getExchangeRate(targetSymbol);
        return priceInAnchor * rate;
    };

    const getProductExchangeRate = (product) => {
        // If product has specific exchange_rate_id, use that rate
        if (product?.exchange_rate_id && Array.isArray(currencies)) {
            const productRate = currencies.find(r => r.id === product.exchange_rate_id);
            if (productRate) {
                return productRate;
            }
        }
        // Otherwise, return default rate for the currency
        return currencies.find(c => c.is_default) || currencies[0];
    };

    const convertProductPrice = (product, targetCurrencyCode) => {
        // Get the rate assigned to this product (or default)
        const rate = getProductExchangeRate(product);

        // If target currency matches product's rate currency, use product's rate
        if (rate && rate.currency_code === targetCurrencyCode) {
            return product.price * rate.rate;
        }

        // Otherwise find the rate for target currency
        const targetRate = currencies.find(c => c.currency_code === targetCurrencyCode);
        return product.price * (targetRate?.rate || 1);
    };

    return (
        <ConfigContext.Provider value={{
            business,
            currencies,
            loading,
            refreshConfig,
            getExchangeRate,
            getActiveCurrencies,
            convertPrice,
            getProductExchangeRate,
            convertProductPrice
        }}>
            {children}
        </ConfigContext.Provider>
    );
};

export const useConfig = () => useContext(ConfigContext);
