import { useState, useRef, useEffect } from 'react';
import { Search, ShoppingCart, Trash2, Plus, Minus, CreditCard, RotateCcw } from 'lucide-react';
import { useCart } from '../context/CartContext';
import { useCash } from '../context/CashContext';
import { useConfig } from '../context/ConfigContext';
import { useWebSocket } from '../context/WebSocketContext';
import { Link } from 'react-router-dom';
import UnitSelectionModal from '../components/pos/UnitSelectionModal';
import EditItemModal from '../components/pos/EditItemModal';
import PaymentModal from '../components/pos/PaymentModal';
import CashOpeningModal from '../components/cash/CashOpeningModal';
import CashMovementModal from '../components/cash/CashMovementModal';
import SaleSuccessModal from '../components/pos/SaleSuccessModal';

import apiClient from '../config/axios'; // Ensure import

// ... imports

const POS = () => {
    const { cart, addToCart, removeFromCart, updateQuantity, clearCart, totalUSD, totalBs, totalsByCurrency, exchangeRates } = useCart();
    const { isSessionOpen, openSession } = useCash();
    const { getActiveCurrencies, convertPrice, currencies } = useConfig();
    const { subscribe } = useWebSocket(); // WebSocket Hook
    const anchorCurrency = currencies.find(c => c.is_anchor) || { symbol: '$' };

    // UI State
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedCategory, setSelectedCategory] = useState(null);
    const [selectedProductForUnits, setSelectedProductForUnits] = useState(null); // For Modal
    const [selectedItemForEdit, setSelectedItemForEdit] = useState(null);
    const [isPaymentOpen, setIsPaymentOpen] = useState(false);
    const [isMovementOpen, setIsMovementOpen] = useState(false);
    const [lastSaleData, setLastSaleData] = useState(null); // { cart, totalUSD, paymentData }

    // Data State
    const [catalog, setCatalog] = useState([]);
    const [categories, setCategories] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    // Refs
    const searchInputRef = useRef(null);

    // Fetch Catalog and Categories on Mount
    useEffect(() => {
        const fetchData = async () => {
            try {
                const [productsRes, categoriesRes] = await Promise.all([
                    apiClient.get('/products/'),
                    apiClient.get('/categories')
                ]);
                console.log('POS Catalog loaded:', productsRes.data);
                setCatalog(productsRes.data);
                setCategories(categoriesRes.data);
            } catch (error) {
                console.error("Error fetching data:", error);
            } finally {
                setIsLoading(false);
            }
        };
        fetchData();
    }, []);

    // WebSocket Subscriptions for Products
    useEffect(() => {
        const unsubUpdate = subscribe('product:updated', (updatedProduct) => {
            console.log('📦 Real-time Product Update:', updatedProduct);
            setCatalog(prev => prev.map(p => p.id === updatedProduct.id ? { ...p, ...updatedProduct } : p));
        });

        const unsubCreate = subscribe('product:created', (newProduct) => {
            console.log('📦 Real-time Product Created:', newProduct);
            setCatalog(prev => [...prev, newProduct]);
        });

        // If we implement specific stock event later, add here
        // const unsubStock = subscribe('product:stock_updated', ...);

        return () => {
            unsubUpdate();
            unsubCreate();
        };
    }, [subscribe]);

    // Filter by search and category
    const filteredCatalog = catalog.filter(p => {
        const matchesSearch = p.name.toLowerCase().includes(searchTerm.toLowerCase());

        if (!selectedCategory) return matchesSearch;

        // Check if product belongs to selected category or its children
        if (p.category_id === selectedCategory) return matchesSearch;

        // Check if product belongs to a subcategory of selected category
        const productCategory = categories.find(c => c.id === p.category_id);
        if (productCategory?.parent_id === selectedCategory) return matchesSearch;

        return false;
    });

    // Get root categories and subcategories
    const rootCategories = categories.filter(cat => !cat.parent_id);
    const getSubcategories = (parentId) => categories.filter(cat => cat.parent_id === parentId);

    const handleProductClick = (product) => {
        // Multi-Unit Logic
        if (product.units && product.units.length > 0) {
            setSelectedProductForUnits(product);
            return;
        }

        // Classic Logic (Base Unit)
        addBaseProductToCart(product);
    };

    const addBaseProductToCart = (product) => {
        // Determine exchange rate for base product
        let selectedExchangeRateId = null;
        let selectedExchangeRateName = 'Sistema Default';
        let isSpecialRate = false;

        if (product.exchange_rate_id) {
            selectedExchangeRateId = product.exchange_rate_id;
            isSpecialRate = true;

            // Get rate name
            if (Array.isArray(exchangeRates)) {
                const rateInfo = exchangeRates.find(r => r.id === product.exchange_rate_id);
                if (rateInfo) {
                    selectedExchangeRateName = rateInfo.name;
                }
            }
        }

        const baseUnit = {
            name: product.unit_type || 'Unidad',
            price_usd: product.price,
            factor: 1,
            is_base: true,
            exchange_rate_id: selectedExchangeRateId,
            exchange_rate_name: selectedExchangeRateName,
            is_special_rate: isSpecialRate
        };

        console.log('🔍 DEBUG addBaseProductToCart:');
        console.log('   Product:', product.name);
        console.log('   Product exchange_rate_id:', product.exchange_rate_id);
        console.log('   baseUnit:', baseUnit);

        addToCart(product, baseUnit);
    };



    const handleUnitSelect = (unitOption) => {
        if (!selectedProductForUnits) return;
        const product = selectedProductForUnits;

        // ========================================
        // ALGORITMO DE PRECIO (USD) - CASCADA ESTRICTA
        // ========================================
        let finalPriceUSD;

        // PASO 1: ¿La ProductUnit tiene precio específico?
        if (unitOption.price_usd && unitOption.price_usd > 0) {
            finalPriceUSD = unitOption.price_usd;
            console.log(`💰 Precio Unit Específico: $${finalPriceUSD}`);
        }
        // PASO 2: Calcular desde precio base del producto
        else {
            const basePriceUSD = product.price || 0;
            const conversionFactor = unitOption.conversion_factor || unitOption.factor || 1;
            finalPriceUSD = basePriceUSD * conversionFactor;
            console.log(`💰 Precio Calculado: $${basePriceUSD} × ${conversionFactor} = $${finalPriceUSD}`);
        }

        // ========================================
        // ALGORITMO DE TASA DE CAMBIO - CASCADA ESTRICTA
        // ========================================
        let selectedExchangeRateId = null;
        let selectedExchangeRateName = 'Sistema Default';
        let isSpecialRate = false;

        // PASO 1: ¿La ProductUnit tiene tasa específica?
        if (unitOption.exchange_rate_id) {
            selectedExchangeRateId = unitOption.exchange_rate_id;
            isSpecialRate = true;
            console.log(`💱 Tasa de Unit: ID ${selectedExchangeRateId}`);
        }
        // PASO 2: ¿El Product padre tiene tasa específica?
        else if (product.exchange_rate_id) {
            selectedExchangeRateId = product.exchange_rate_id;
            isSpecialRate = true;
            console.log(`💱 Tasa del Producto: ID ${selectedExchangeRateId}`);
        }
        // PASO 3: Usar tasa global por defecto (null = sistema decide)
        else {
            selectedExchangeRateId = null;
            isSpecialRate = false;
            console.log(`💱 Usando tasa predeterminada del sistema`);
        }

        // Obtener nombre de la tasa para mostrar en UI
        if (selectedExchangeRateId && Array.isArray(exchangeRates)) {
            const rateInfo = exchangeRates.find(r => r.id === selectedExchangeRateId);
            if (rateInfo) {
                selectedExchangeRateName = rateInfo.name;
            }
        }

        // ========================================
        // CONSTRUIR OBJETO UNIT PARA EL CARRITO
        // ========================================
        const unit = {
            name: unitOption.unit_name || unitOption.name,
            price_usd: finalPriceUSD,  // Precio ya resuelto
            factor: unitOption.conversion_factor || unitOption.factor || 1,
            is_base: unitOption.is_base || false,
            unit_id: unitOption.id || null,

            // NUEVO: Información de tasa de cambio
            exchange_rate_id: selectedExchangeRateId,
            exchange_rate_name: selectedExchangeRateName,
            is_special_rate: isSpecialRate
        };

        console.log('📦 Unit final para carrito:', unit);

        // Agregar al carrito
        addToCart(product, unit);
        setSelectedProductForUnits(null);
    };

    const handleCheckout = (paymentData) => {
        // Save data for receipt printing
        setLastSaleData({
            cart: [...cart], // Copy cart
            totalUSD,
            totalBs,
            paymentData
        });

        // Don't clear cart immediately, wait for user to close success modal
        setIsPaymentOpen(false);
        // Success modal triggers based on !!lastSaleData
    };

    const handleSuccessClose = () => {
        setLastSaleData(null);
        clearCart();
    };

    return (
        <div className="flex h-[calc(100vh-64px)] overflow-hidden bg-gray-100">
            {/* LEFT COLUMN: Catalog (70%) */}
            <div className="w-[70%] flex flex-col p-4 border-r border-gray-300">
                {/* Search */}
                <div className="mb-4 relative">
                    <Search className="absolute left-4 top-3.5 text-gray-400" size={24} />
                    <input
                        ref={searchInputRef}
                        type="text"
                        className="w-full text-xl pl-12 pr-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-0 outline-none shadow-sm"
                        placeholder="Buscar producto (F3)..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        autoFocus
                    />
                </div>

                {/* Category Filters */}
                <div className="mb-4">
                    {/* Parent Categories */}
                    <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-gray-300">
                        <button
                            onClick={() => setSelectedCategory(null)}
                            className={`px-4 py-2 rounded-full font-medium whitespace-nowrap transition-all ${!selectedCategory
                                ? 'bg-blue-600 text-white shadow-md'
                                : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                                }`}
                        >
                            📦 Todos
                        </button>
                        {rootCategories.map(category => (
                            <button
                                key={category.id}
                                onClick={() => setSelectedCategory(category.id)}
                                className={`px-4 py-2 rounded-full font-medium whitespace-nowrap transition-all ${selectedCategory === category.id
                                    ? 'bg-blue-600 text-white shadow-md'
                                    : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                                    }`}
                            >
                                {category.name}
                            </button>
                        ))}
                    </div>

                    {/* Subcategories (if parent selected) */}
                    {selectedCategory && getSubcategories(selectedCategory).length > 0 && (
                        <div className="flex items-center gap-2 overflow-x-auto mt-2 pb-2 scrollbar-thin scrollbar-thumb-gray-300">
                            <span className="text-xs text-gray-500 font-medium whitespace-nowrap">Subcategorías:</span>
                            {getSubcategories(selectedCategory).map(subcategory => (
                                <button
                                    key={subcategory.id}
                                    onClick={() => setSelectedCategory(subcategory.id)}
                                    className={`px-3 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-all ${selectedCategory === subcategory.id
                                        ? 'bg-blue-500 text-white shadow'
                                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200 border border-gray-300'
                                        }`}
                                >
                                    └─ {subcategory.name}
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                {/* Grid */}
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 overflow-y-auto pr-2 pb-20">
                    {filteredCatalog.map(product => (
                        <div
                            key={product.id}
                            onClick={() => handleProductClick(product)}
                            className="bg-white p-4 rounded-xl shadow-sm hover:shadow-md cursor-pointer border border-transparent hover:border-blue-400 transition-all flex flex-col justify-between h-40"
                        >
                            <div>
                                <h3 className="font-bold text-gray-800 leading-tight mb-1">{product.name}</h3>
                                <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
                                    Stock: {product.stock || 0}
                                </span>
                            </div>
                            <div className="mt-2 self-end">
                                <span className="block text-right text-lg font-bold text-blue-600">
                                    ${product.price.toFixed(2)}
                                </span>
                                {product.units?.length > 0 && (
                                    <span className="block text-right text-xs text-orange-500 font-medium">
                                        + {product.units.length} Presentaciones
                                    </span>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* RIGHT COLUMN: Ticket (30%) */}
            <div className="w-[30%] bg-white flex flex-col shadow-2xl h-full border-l">
                <div className="bg-slate-800 text-white p-4 shadow-md">
                    <div className="flex justify-between items-center mb-2">
                        <h2 className="text-xl font-bold flex items-center">
                            <ShoppingCart className="mr-2" /> Ticket
                        </h2>
                        <button onClick={clearCart} className="text-xs bg-red-500 hover:bg-red-600 px-2 py-1 rounded transition">
                            Limpiar
                        </button>
                    </div>
                    <div className="flex space-x-2">
                        <button
                            onClick={() => setIsMovementOpen(true)}
                            className="flex-1 text-xs bg-slate-700 hover:bg-slate-600 py-1 rounded text-center border border-slate-600"
                        >
                            Gasto/Retiro
                        </button>
                        <Link
                            to="/cash-close"
                            className="flex-1 text-xs bg-slate-700 hover:bg-slate-600 py-1 rounded text-center border border-slate-600 block"
                        >
                            Cerrar Caja
                        </Link>
                    </div>
                </div>

                {/* List */}
                <div className="flex-1 overflow-y-auto p-2 space-y-2">
                    {cart.length === 0 && (
                        <div className="flex flex-col items-center justify-center h-full text-gray-400 opacity-50">
                            <ShoppingCart size={48} className="mb-2" />
                            <p>Carrito Vacío</p>
                        </div>
                    )}
                    {cart.map(item => (
                        <div
                            key={item.id + (item.unit_id || '')}
                            onClick={() => setSelectedItemForEdit(item)}
                            className="flex justify-between items-center p-3 hover:bg-blue-50 cursor-pointer rounded-lg border-b border-gray-100 last:border-0 transition-colors group"
                        >
                            <div className="flex-1">
                                <div className="font-medium text-gray-800 leading-snug">{item.name}</div>
                                <div className="text-xs text-gray-500 flex gap-2 items-center flex-wrap">
                                    <span className="bg-blue-100 text-blue-700 px-1.5 rounded">
                                        {item.unit_name} {item.unit_id ? <span>(x{item.conversion_factor})</span> : null}
                                    </span>
                                    <span>${(item.unit_price_usd || 0).toFixed(2)}</span>

                                    {/* NEW: Special Rate Indicator */}
                                    {item.is_special_rate && (
                                        <span className="bg-purple-100 text-purple-700 px-1.5 rounded font-semibold flex items-center gap-1" title={`Usando tasa: ${item.exchange_rate_name}`}>
                                            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                                <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
                                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clipRule="evenodd" />
                                            </svg>
                                            {item.exchange_rate_name}
                                        </span>
                                    )}
                                </div>
                            </div>
                            <div className="flex flex-col items-end">
                                <span className="text-lg font-bold text-gray-800">x{item.quantity}</span>
                                <span className="font-bold text-blue-600">${(item.subtotal_usd || 0).toFixed(2)}</span>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Footer Totals */}
                <div className="bg-gray-50 p-4 border-t-2 border-slate-200">
                    <div className="space-y-2 mb-4">
                        {/* Base Currency (Anchor) */}
                        <div className="flex justify-between items-end border-b pb-2">
                            <span className="text-gray-500 text-sm font-medium">Total ({anchorCurrency.symbol})</span>
                            <span className="text-3xl font-bold text-gray-800">{anchorCurrency.symbol}{totalUSD.toFixed(2)}</span>
                        </div>
                        {/* Other Currencies */}
                        {getActiveCurrencies().map(curr => {
                            // Get total for this currency from cart calculations
                            const currencyTotal = totalsByCurrency?.[curr.currency_code] || 0;

                            return (
                                <div key={curr.id} className="flex justify-between items-end">
                                    <span className="text-gray-500 text-xs font-medium">Total {curr.name}</span>
                                    <span className="text-lg font-bold text-blue-600 font-mono">
                                        {curr.symbol} {currencyTotal.toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                    </span>
                                </div>
                            );
                        })}
                    </div>

                    <button
                        onClick={() => setIsPaymentOpen(true)}
                        disabled={cart.length === 0}
                        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-bold py-4 rounded-xl shadow-lg transform active:scale-95 transition-all text-xl"
                    >
                        COBRAR ${totalUSD.toFixed(2)}
                    </button>
                </div>
            </div>

            {/* Modals */}
            <UnitSelectionModal
                isOpen={!!selectedProductForUnits}
                product={selectedProductForUnits}
                onClose={() => setSelectedProductForUnits(null)}
                onSelect={handleUnitSelect}
            />

            <EditItemModal
                isOpen={!!selectedItemForEdit}
                item={selectedItemForEdit}
                onClose={() => setSelectedItemForEdit(null)}
                onUpdate={updateQuantity}
                onDelete={removeFromCart}
            />

            <PaymentModal
                isOpen={isPaymentOpen}
                totalUSD={totalUSD}
                totalBs={totalBs}
                totalsByCurrency={totalsByCurrency} // Pass calculated totals
                cart={cart}
                onClose={() => setIsPaymentOpen(false)}
                onConfirm={handleCheckout}
            />

            <CashMovementModal
                isOpen={isMovementOpen}
                onClose={() => setIsMovementOpen(false)}
            />

            <SaleSuccessModal
                isOpen={!!lastSaleData}
                saleData={lastSaleData}
                onClose={handleSuccessClose}
            />

            {/* Cash Opening Modal if session closed */}{!isSessionOpen && (
                <CashOpeningModal onOpen={openSession} />
            )}
        </div>
    );
};

export default POS;
