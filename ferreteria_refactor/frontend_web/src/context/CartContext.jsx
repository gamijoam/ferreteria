import { createContext, useState, useContext, useMemo } from 'react';

const CartContext = createContext();

export const CartProvider = ({ children }) => {
    const [cart, setCart] = useState([]);

    // Add Item Logic logic with multi-unit support
    const addToCart = (product, unit) => {
        // unit: { name, price_usd, factor, is_base }
        const itemId = `${product.id}_${unit.name.replace(/\s+/g, '_')}`;

        setCart(prevCart => {
            const existingItem = prevCart.find(item => item.id === itemId);

            if (existingItem) {
                // Update quantity if exists
                return updateItemQuantityInList(prevCart, itemId, existingItem.quantity + 1);
            } else {
                // Add new item
                const exchangeRate = product.exchange_rate || 45.00; // Fallback or global
                const subtotalUsd = unit.price_usd * 1;

                const newItem = {
                    id: itemId,
                    product_id: product.id,
                    name: product.name,
                    unit_name: unit.name,
                    quantity: 1,
                    unit_price_usd: unit.price_usd,
                    conversion_factor: unit.factor,
                    exchange_rate: exchangeRate,
                    subtotal_usd: subtotalUsd,
                    subtotal_bs: subtotalUsd * exchangeRate
                };
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

    // Totals Calculation (Sum of subtotals)
    const totals = useMemo(() => {
        return cart.reduce((acc, item) => ({
            usd: acc.usd + item.subtotal_usd,
            bs: acc.bs + item.subtotal_bs
        }), { usd: 0, bs: 0 });
    }, [cart]);

    return (
        <CartContext.Provider value={{
            cart,
            addToCart,
            removeFromCart,
            updateQuantity,
            clearCart,
            totalUSD: totals.usd,
            totalBs: totals.bs
        }}>
            {children}
        </CartContext.Provider>
    );
};

export const useCart = () => useContext(CartContext);
