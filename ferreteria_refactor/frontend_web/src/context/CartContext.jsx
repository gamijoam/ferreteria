import { createContext, useState, useContext, useMemo, useEffect } from 'react';
import apiClient from '../config/axios';

const CartContext = createContext();

export const CartProvider = ({ children }) => {
    const [cart, setCart] = useState([]);
    const [exchangeRates, setExchangeRates] = useState([]);

    // Fetch exchange rates on mount
    useEffect(() => {
        const fetchExchangeRates = async () => {
            try {
                const response = await apiClient.get('/config/exchange-rates', {
                    params: { is_active: true }
                });
                setExchangeRates(response.data);
            } catch (error) {
                console.error('Error fetching exchange rates:', error);
            }
        };
        fetchExchangeRates();
    }, []);

    /**
     * Get effective exchange rate for a product/unit combination
     * Hierarchy: Unit.exchange_rate_id → Product.exchange_rate_id → Default rate for currency
     */
    const getEffectiveExchangeRate = (product, unit, targetCurrencyCode = 'VES') => {
        // 1. Check if unit has specific rate
        if (unit.exchange_rate_id) {
            const rate = exchangeRates.find(r => r.id === unit.exchange_rate_id);
            if (rate && rate.is_active) {
                return {
                    rate: rate.rate,
                    rateName: rate.name,
                    rateId: rate.id,
                    source: 'unit',
                    isSpecial: !rate.is_default
                };
            }
        }

        // 2. Check if product has specific rate
        if (product.exchange_rate_id) {
            const rate = exchangeRates.find(r => r.id === product.exchange_rate_id);
            if (rate && rate.is_active) {
                return {
                    rate: rate.rate,
                    rateName: rate.name,
                    rateId: rate.id,
                    source: 'product',
                    isSpecial: !rate.is_default
                };
            }
        }

        // 3. Fallback to default rate for target currency
        const defaultRate = exchangeRates.find(r =>
            r.currency_code === targetCurrencyCode &&
            r.is_default &&
            r.is_active
        );

        if (defaultRate) {
            return {
                rate: defaultRate.rate,
                rateName: defaultRate.name,
                rateId: defaultRate.id,
                source: 'default',
                isSpecial: false
            };
        }

        // Ultimate fallback (should not happen if DB is seeded properly)
        console.warn('No exchange rate found, using hardcoded fallback');
        return {
            rate: 45.00,
            rateName: 'Fallback',
            rateId: null,
            source: 'fallback',
            isSpecial: false
        };
    };

    // Add Item Logic with multi-unit support and exchange rate hierarchy
    const addToCart = (product, unit) => {
        // unit: { name, price_usd, factor, is_base, exchange_rate_id?, exchange_rate_name?, is_special_rate? }
        const itemId = `${product.id}_${unit.name.replace(/\s+/g, '_')}`;

        setCart(prevCart => {
            const existingItem = prevCart.find(item => item.id === itemId);

            if (existingItem) {
                // Update quantity if exists
                return updateItemQuantityInList(prevCart, itemId, existingItem.quantity + 1);
            } else {
                // Get effective exchange rate using hierarchy (as fallback if not provided by caller)
                const rateInfo = unit.exchange_rate_id
                    ? {
                        rate: exchangeRates.find(r => r.id === unit.exchange_rate_id)?.rate || 1,
                        rateName: unit.exchange_rate_name || 'Personalizada',
                        source: 'pre-resolved',
                        isSpecial: unit.is_special_rate ?? true
                    }
                    : getEffectiveExchangeRate(product, unit);

                const subtotalUsd = unit.price_usd * 1;

                console.log('🛒 DEBUG CartContext addToCart:');
                console.log('   Product:', product.name);
                console.log('   Unit received:', unit);
                console.log('   rateInfo:', rateInfo);

                const newItem = {
                    id: itemId,
                    product_id: product.id,
                    name: product.name,
                    unit_name: unit.name,
                    quantity: 1,
                    unit_price_usd: unit.price_usd,
                    conversion_factor: unit.factor,
                    exchange_rate: rateInfo.rate,
                    exchange_rate_name: rateInfo.rateName,
                    exchange_rate_source: rateInfo.source,
                    is_special_rate: rateInfo.isSpecial,
                    subtotal_usd: subtotalUsd,
                    subtotal_bs: subtotalUsd * rateInfo.rate
                };

                console.log('   newItem created:', newItem);

                return [...prevCart, newItem];
            }
        });
    };

    const removeFromCart = (itemId) => {
        setCart(prev => prev.filter(item => item.id !== itemId));
    };

    const updateQuantity = (itemId, newQuantity) => {
        if (newQuantity <= 0) {
            removeFromCart(itemId);
            return;
        }
        setCart(prev => updateItemQuantityInList(prev, itemId, newQuantity));
    };

    const clearCart = () => setCart([]);

    // Helper to purely update the list and recalculate subtotals
    const updateItemQuantityInList = (list, itemId, qty) => {
        return list.map(item => {
            if (item.id === itemId) {
                const subUsd = item.unit_price_usd * qty;
                return {
                    ...item,
                    quantity: qty,
                    subtotal_usd: subUsd,
                    subtotal_bs: subUsd * item.exchange_rate
                };
            }
            return item;
        });
    };

    // Totals Calculation (Sum of subtotals per currency)
    const totals = useMemo(() => {
        const totalsPerCurrency = {};

        cart.forEach(item => {
            // Get currency code from exchange rate
            const currencyCode = item.exchange_rate_source === 'pre-resolved'
                ? (exchangeRates.find(r => r.id === item.exchange_rate_id)?.currency_code || 'VES')
                : 'VES'; // Default to VES for now

            if (!totalsPerCurrency[currencyCode]) {
                totalsPerCurrency[currencyCode] = 0;
            }

            totalsPerCurrency[currencyCode] += item.subtotal_bs || (item.subtotal_usd * item.exchange_rate);
        });

        return {
            usd: cart.reduce((acc, item) => acc + item.subtotal_usd, 0),
            bs: cart.reduce((acc, item) => acc + (item.subtotal_bs || 0), 0),
            byCurrency: totalsPerCurrency
        };
    }, [cart, exchangeRates]);

    return (
        <CartContext.Provider value={{
            cart,
            addToCart,
            removeFromCart,
            updateQuantity,
            clearCart,
            totalUSD: totals.usd,
            totalBs: totals.bs,
            totalsByCurrency: totals.byCurrency,
            exchangeRates  // Expose for other components if needed
        }}>
            {children}
        </CartContext.Provider>
    );
};

export const useCart = () => useContext(CartContext);
