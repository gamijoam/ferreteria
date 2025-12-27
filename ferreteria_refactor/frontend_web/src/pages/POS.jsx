import { useState, useRef, useEffect } from 'react';
import { useHotkeys } from 'react-hotkeys-hook';
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
import useBarcodeScanner from '../hooks/useBarcodeScanner';

import apiClient from '../config/axios';

// Helper to format stock: show as integer if whole number, otherwise show decimals
const formatStock = (stock) => {
    const num = Number(stock);
    return num % 1 === 0 ? num.toFixed(0) : num.toFixed(3).replace(/\.?0+$/, '');
}; // Ensure import

// ... imports

const POS = () => {
    const { cart, addToCart, removeFromCart, updateQuantity, clearCart, totalUSD, totalBs, totalsByCurrency, exchangeRates } = useCart();
    const { isSessionOpen, openSession, loading } = useCash();
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
    const [selectedProductIndex, setSelectedProductIndex] = useState(-1); // For keyboard navigation

    // Data State
    const [catalog, setCatalog] = useState([]);
    const [categories, setCategories] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    // Refs
    const searchInputRef = useRef(null);

    // ========================================
    // KEYBOARD SHORTCUTS
    // ========================================

    // F3: Focus search input
    useHotkeys('f3', (e) => {
        e.preventDefault();
        if (searchInputRef.current) {
            searchInputRef.current.focus();
            if (searchTerm) {
                searchInputRef.current.select(); // Select all text for easy rewrite
            }
        }
    }, { enableOnFormTags: true }); // Works even when focused on inputs

    // F5: Open payment modal (Cobrar)
    useHotkeys('f5', (e) => {
        e.preventDefault();
        if (cart.length > 0) {
            setIsPaymentOpen(true);
        }
    }, {
        preventDefault: true,  // Critical: prevent browser refresh
        enableOnFormTags: true
    });

    // ESC: Cancel/Back cascade logic
    useHotkeys('esc', (e) => {
        e.preventDefault();

        // Priority cascade
        if (isPaymentOpen) {
            setIsPaymentOpen(false);
        } else if (isMovementOpen) {
            setIsMovementOpen(false);
        } else if (selectedProductForUnits) {
            setSelectedProductForUnits(null);
        } else if (selectedItemForEdit) {
            setSelectedItemForEdit(null);
        } else if (lastSaleData) {
            handleSuccessClose();
        } else {
            // Nothing open, clear search and focus
            setSearchTerm('');
            if (searchInputRef.current) {
                searchInputRef.current.focus();
            }
        }
    });

    // F2: New sale (clear cart with confirmation)
    useHotkeys('f2', (e) => {
        e.preventDefault();
        if (cart.length > 0) {
            if (window.confirm('¿Desea iniciar una nueva venta? Se perderá el carrito actual.')) {
                clearCart();
                setSearchTerm('');
                if (searchInputRef.current) {
                    searchInputRef.current.focus();
                }
            }
        } else {
            // Cart already empty, just clear search
            setSearchTerm('');
            if (searchInputRef.current) {
                searchInputRef.current.focus();
            }
        }
    });

    // F4: Edit last item in cart
    useHotkeys('f4', (e) => {
        e.preventDefault();
        if (cart.length > 0) {
            const lastItem = cart[cart.length - 1];
            setSelectedItemForEdit(lastItem);
        }
    });

    // Arrow Down: Navigate to next product in search results
    useHotkeys('down', (e) => {
        if (filteredCatalog.length > 0) {
            e.preventDefault();
            setSelectedProductIndex(prev =>
                prev < filteredCatalog.length - 1 ? prev + 1 : prev
            );
        }
    }, { enableOnFormTags: true });

    // Arrow Up: Navigate to previous product in search results
    useHotkeys('up', (e) => {
        if (filteredCatalog.length > 0) {
            e.preventDefault();
            setSelectedProductIndex(prev => prev > 0 ? prev - 1 : 0);
        }
    }, { enableOnFormTags: true });

    // Enter: Add selected product to cart
    useHotkeys('enter', (e) => {
        if (selectedProductIndex >= 0 && selectedProductIndex < filteredCatalog.length) {
            e.preventDefault();
            const selectedProduct = filteredCatalog[selectedProductIndex];
            handleProductClick(selectedProduct);
            setSelectedProductIndex(-1); // Reset selection
        }
    }, { enableOnFormTags: true });

    // ========================================
    // BARCODE SCANNER INTEGRATION
    // ========================================

    /**
     * Handler para cuando se escanea un código de barras
     * Busca el producto en el catálogo y lo agrega al carrito
     */
    const handleGlobalScan = (code) => {
        console.log('🔍 Buscando producto con código:', code);
        console.log('📦 Total productos en catálogo:', catalog.length);

        // Buscar producto por SKU, nombre, ID, o barcode en units
        const foundProduct = catalog.find(p => {
            // Check SKU (handle both string and numeric)
            const matchesSku = p.sku && (
                p.sku.toString().toLowerCase() === code.toLowerCase() ||
                p.sku.toString() === code
            );

            // Check name and ID
            const matchesName = p.name.toLowerCase().includes(code.toLowerCase());
            const matchesId = p.id.toString() === code;

            // Check barcodes in product units
            const matchesUnitBarcode = p.units && p.units.some(unit =>
                unit.barcode && (
                    unit.barcode.toString().toLowerCase() === code.toLowerCase() ||
                    unit.barcode.toString() === code
                )
            );

            const matches = matchesSku || matchesName || matchesId || matchesUnitBarcode;

            // Debug log for each product checked
            if (p.sku && p.sku.toString().includes(code)) {
                console.log('🔎 Producto candidato:', {
                    name: p.name,
                    sku: p.sku,
                    skuType: typeof p.sku,
                    code: code,
                    codeType: typeof code,
                    matchesSku,
                    matches
                });
            }

            return matches;
        });

        if (foundProduct) {
            console.log('✅ Producto encontrado:', foundProduct.name);
            handleProductClick(foundProduct);
        } else {
            console.error('❌ Producto no encontrado para código:', code);
            console.log('📋 Primeros 3 productos del catálogo:', catalog.slice(0, 3).map(p => ({
                name: p.name,
                sku: p.sku,
                skuType: typeof p.sku
            })));
            alert(`Producto no encontrado: ${code}`);
        }
    };

    // Activar el hook de escaneo
    useBarcodeScanner(handleGlobalScan, {
        minLength: 3,           // Códigos de al menos 3 caracteres
        maxTimeBetweenKeys: 50, // Scanners escriben <50ms entre teclas
        ignoreIfFocused: false  // Capturar incluso si hay un input enfocado
    });


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

        const unsubDelete = subscribe('product:deleted', (deletedProduct) => {
            console.log('📦 Real-time Product Deleted:', deletedProduct);
            setCatalog(prev => prev.filter(p => p.id !== deletedProduct.id));
        });

        return () => {
            unsubUpdate();
            unsubCreate();
            unsubDelete();
        };
    }, [subscribe]);

    // Filter by search and category
    const filteredCatalog = catalog.filter(p => {
        // Search by name, SKU, or barcode in units
        const searchLower = searchTerm.toLowerCase();

        // Check product name and SKU
        const matchesName = p.name.toLowerCase().includes(searchLower);

        // SKU comparison - handle both string and numeric
        const matchesSku = p.sku && (
            p.sku.toString().toLowerCase().includes(searchLower) ||
            p.sku.toString() === searchTerm
        );

        const matchesNameOrSku = matchesName || matchesSku;

        // Check barcodes in product units (alternative presentations)
        const matchesUnitBarcode = p.units && p.units.some(unit =>
            unit.barcode && (
                unit.barcode.toString().toLowerCase().includes(searchLower) ||
                unit.barcode.toString() === searchTerm
            )
        );

        const matchesSearch = matchesNameOrSku || matchesUnitBarcode;

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

        // Calculate Discount
        const basePrice = parseFloat(product.price);
        let finalPrice = basePrice;
        let discountPercentage = 0;
        let isDiscountActive = false;

        if (product.is_discount_active && product.discount_percentage > 0) {
            discountPercentage = parseFloat(product.discount_percentage);
            const discountAmount = basePrice * (discountPercentage / 100);
            finalPrice = basePrice - discountAmount;
            isDiscountActive = true;
        }

        const baseUnit = {
            name: product.unit_type || 'Unidad',
            price_usd: finalPrice, // Discounted price for cart totals
            original_price_usd: basePrice, // Original price for backend
            discount_percentage: discountPercentage,
            is_discount_active: isDiscountActive,

            factor: 1,
            is_base: true,
            exchange_rate_id: selectedExchangeRateId,
            exchange_rate_name: selectedExchangeRateName,
            is_special_rate: isSpecialRate
        };

        console.log('🔍 DEBUG addBaseProductToCart:', baseUnit);
        addToCart(product, baseUnit);
    };

    const handleUnitSelect = (unitOption) => {
        if (!selectedProductForUnits) return;
        const product = selectedProductForUnits;

        // ========================================
        // ALGORITMO DE PRECIO (USD) - CASCADA ESTRICTA
        // ========================================
        let calculatedPriceUSD;

        // PASO 1: ¿La ProductUnit tiene precio específico?
        if (unitOption.price_usd && unitOption.price_usd > 0) {
            calculatedPriceUSD = parseFloat(unitOption.price_usd);
        }
        // PASO 2: Calcular desde precio base del producto
        else {
            const basePriceUSD = parseFloat(product.price || 0);
            const conversionFactor = parseFloat(unitOption.conversion_factor || unitOption.factor || 1);
            calculatedPriceUSD = basePriceUSD * conversionFactor;
        }

        // Apply Discount Logic for Units
        let finalPriceUSD = calculatedPriceUSD;
        let discountPercentage = 0;
        let isDiscountActive = false;

        if (unitOption.is_discount_active && unitOption.discount_percentage > 0) {
            discountPercentage = parseFloat(unitOption.discount_percentage);
            const discountAmount = calculatedPriceUSD * (discountPercentage / 100);
            finalPriceUSD = calculatedPriceUSD - discountAmount;
            isDiscountActive = true;
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
            price_usd: finalPriceUSD,  // Precio YA DESCONTADO
            original_price_usd: calculatedPriceUSD, // Precio BASE
            discount_percentage: discountPercentage,
            is_discount_active: isDiscountActive,

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
            paymentData,
            saleId: paymentData.saleId // NEW: Capture sale ID for printing
        });

        // Don't clear cart immediately, wait for user to close success modal
        setIsPaymentOpen(false);
        // Success modal triggers based on !!lastSaleData
    };

    const handleSuccessClose = () => {
        setLastSaleData(null);
        clearCart();
    };

    // Mobile View State
    const [mobileTab, setMobileTab] = useState('catalog'); // 'catalog' | 'ticket'

    return (
        <div className="flex flex-col md:flex-row h-[calc(100vh-64px)] overflow-hidden bg-gray-100 relative">

            {/* LEFT COLUMN: Catalog (Mobile: Show only if tab is catalog. Desktop: Always 70%) */}
            <div className={`
                flex-col p-4 border-r border-gray-300 transition-all min-w-0
                ${mobileTab === 'catalog' ? 'flex w-full' : 'hidden md:flex w-full md:w-[70%]'}
                h-full
            `}>
                {/* Search */}
                <div className="mb-4 relative">
                    <Search className="absolute left-4 top-3.5 text-gray-400" size={24} />
                    <input
                        ref={searchInputRef}
                        type="text"
                        className="w-full text-lg md:text-xl pl-12 pr-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-0 outline-none shadow-sm"
                        placeholder="Buscar producto (F3)..."
                        value={searchTerm}
                        onChange={(e) => {
                            setSearchTerm(e.target.value);
                            setSelectedProductIndex(-1); // Reset selection on search change
                        }}
                        autoFocus
                    />
                    {/* Keyboard hint - Hide on mobile */}
                    <div className="hidden md:flex absolute right-3 top-3 gap-1">
                        <kbd className="px-2 py-1 text-xs font-semibold text-gray-600 bg-gray-100 border border-gray-300 rounded shadow-sm">F3</kbd>
                        <kbd className="px-2 py-1 text-xs font-semibold text-gray-600 bg-gray-100 border border-gray-300 rounded shadow-sm">↑↓</kbd>
                    </div>
                </div>

                {/* Category Filters */}
                <div className="mb-4">
                    {/* Parent Categories */}
                    <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-gray-300 touch-pan-x">
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
                        <div className="flex items-center gap-2 overflow-x-auto mt-2 pb-2 scrollbar-thin scrollbar-thumb-gray-300 touch-pan-x">
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
                {/* Mobile: grid-cols-2, Desktop: grid-cols-3/4. Added pb-24 for mobile fab space */}
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 md:gap-4 overflow-y-auto pr-2 pb-24 md:pb-20">
                    {filteredCatalog.map((product, index) => (
                        <div
                            key={product.id}
                            onClick={() => handleProductClick(product)}
                            className={`bg-white p-3 md:p-4 rounded-xl shadow-sm hover:shadow-md cursor-pointer border transition-all flex flex-col justify-between h-40 ${index === selectedProductIndex
                                ? 'border-blue-500 ring-2 ring-blue-300 bg-blue-50'
                                : 'border-transparent hover:border-blue-400'
                                }`}
                        >
                            <div className="overflow-hidden">
                                <h3 className="font-bold text-gray-800 leading-tight mb-1 text-sm md:text-base line-clamp-2">{product.name}</h3>
                                <span className="text-[10px] md:text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded inline-block">
                                    Stock: {formatStock(product.stock || 0)}
                                </span>
                            </div>
                            <div className="mt-2 self-end w-full">
                                <span className="block text-right text-base md:text-lg font-bold text-blue-600">
                                    ${Number(product.price).toFixed(2)}
                                </span>
                                {product.units?.length > 0 && (
                                    <span className="block text-right text-[10px] md:text-xs text-orange-500 font-medium truncate">
                                        + {product.units.length} Pres.
                                    </span>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* RIGHT COLUMN: Ticket (Mobile: Show only if tab is ticket. Desktop: Always 30% and flex) */}
            <div className={`
                bg-white flex-col shadow-2xl h-full border-l min-w-0
                ${mobileTab === 'ticket' ? 'flex w-full absolute inset-0 z-10' : 'hidden md:flex w-[30%]'}
            `}>
                <div className="bg-slate-800 text-white p-4 shadow-md flex justify-between items-center">
                    <div className="flex items-center">
                        {/* Mobile Back Button */}
                        <button
                            onClick={() => setMobileTab('catalog')}
                            className="mr-3 md:hidden p-1 hover:bg-slate-700 rounded"
                        >
                            <Search size={20} />
                        </button>
                        <h2 className="text-xl font-bold flex items-center">
                            <ShoppingCart className="mr-2" size={20} /> <span className="hidden sm:inline">Ticket</span>
                        </h2>
                    </div>

                    <div className="flex items-center gap-2">
                        <button
                            onClick={clearCart}
                            className="text-xs bg-red-500 hover:bg-red-600 px-3 py-1.5 rounded transition flex items-center gap-1 font-bold"
                            title="Nueva Venta (F2)"
                        >
                            <Trash2 size={14} />
                            <span className="hidden lg:inline">Limpiar</span>
                        </button>
                    </div>
                </div>

                {/* Operations Toolbar */}
                <div className="bg-slate-100 p-2 flex space-x-2 border-b">
                    <button
                        onClick={() => setIsMovementOpen(true)}
                        className="flex-1 text-xs bg-white hover:bg-gray-50 text-slate-700 py-2 rounded text-center border shadow-sm font-medium"
                    >
                        Gasto/Retiro
                    </button>
                    <Link
                        to="/cash-close"
                        className="flex-1 text-xs bg-white hover:bg-gray-50 text-slate-700 py-2 rounded text-center border shadow-sm font-medium block"
                    >
                        Cerrar Caja
                    </Link>
                </div>

                {/* Cart List */}
                <div className="flex-1 overflow-y-auto p-2 space-y-2 pb-32 md:pb-0">
                    {cart.length === 0 && (
                        <div className="flex flex-col items-center justify-center h-full text-gray-400 opacity-50">
                            <ShoppingCart size={48} className="mb-2" />
                            <p>Carrito Vacío</p>
                            <button
                                onClick={() => setMobileTab('catalog')}
                                className="mt-4 text-blue-500 underline md:hidden"
                            >
                                Ir al Catálogo
                            </button>
                        </div>
                    )}
                    {cart.map((item, idx) => (
                        <div
                            key={`${item.id}-${item.unit_id}-${idx}`}
                            onClick={() => setSelectedItemForEdit(item)}
                            className="bg-white p-3 rounded-xl border border-gray-100 shadow-sm hover:shadow-md hover:border-blue-200 cursor-pointer transition-all group relative"
                        >
                            {/* Header: Name & SKU */}
                            <div className="flex justify-between items-start mb-2">
                                <div className="min-w-0 pr-2">
                                    <div className="font-bold text-gray-800 text-sm md:text-base leading-tight line-clamp-2">
                                        {item.name}
                                    </div>
                                    <div className="flex items-center gap-2 mt-1">
                                        {item.sku && (
                                            <span className="text-[10px] font-mono bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded border border-gray-200">
                                                {item.sku}
                                            </span>
                                        )}
                                        {/* Stock Warning Badge */}
                                        {Number(item.stock) <= Number(item.quantity) * Number(item.conversion_factor || 1) && (
                                            <span className="text-[10px] bg-red-50 text-red-600 px-1.5 py-0.5 rounded border border-red-100 font-medium">
                                                Poco Stock
                                            </span>
                                        )}
                                    </div>
                                </div>
                                {/* Quantity Large Display */}
                                <div className="flex flex-col items-end">
                                    <span className="text-xl md:text-2xl font-bold text-blue-600 leading-none">
                                        x{item.quantity}
                                    </span>
                                </div>
                            </div>

                            {/* Divider with Unit Info */}
                            <div className="flex items-center gap-2 mb-2">
                                <span className="bg-blue-50 text-blue-700 text-xs px-2 py-1 rounded-md font-medium border border-blue-100">
                                    {item.unit_name} {item.unit_id ? <span className="text-blue-500 opacity-75 text-[10px]">(x{item.conversion_factor})</span> : null}
                                </span>
                                {item.is_special_rate && (
                                    <span className="bg-purple-50 text-purple-700 text-xs px-2 py-1 rounded-md font-medium flex items-center gap-1 border border-purple-100" title={item.exchange_rate_name}>
                                        <RotateCcw size={10} />
                                        <span className="truncate max-w-[60px] uppercase text-[10px]">{item.exchange_rate_name || 'Tasa'}</span>
                                    </span>
                                )}
                            </div>

                            {/* Footer: Prices */}
                            <div className="flex justify-between items-end border-t border-dashed pt-2">
                                {/* Unit Price Detail */}
                                <div className="text-xs text-gray-400">
                                    <div>Unit: ${Number(item.unit_price_usd).toFixed(2)}</div>
                                    <div className="text-gray-500 font-medium">
                                        Bs. {(Number(item.unit_price_usd) * Number(item.exchange_rate)).toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                    </div>
                                </div>

                                {/* Totals */}
                                <div className="text-right">
                                    <div className="font-bold text-gray-900 text-sm md:text-base">
                                        ${Number(item.subtotal_usd || 0).toFixed(2)}
                                    </div>
                                    <div className="text-xs text-gray-500 font-medium">
                                        Bs. {Number(item.subtotal_bs || 0).toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Footer Totals (Fixed at bottom on desktop, integrated in flow) */}
                <div className="bg-gray-50 p-4 border-t-2 border-slate-200 mt-auto shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.1)] z-20">
                    <div className="space-y-2 mb-4">
                        {/* Base Currency (Anchor) */}
                        <div className="flex justify-between items-end border-b pb-2">
                            <span className="text-gray-500 text-sm font-medium">Total ({anchorCurrency.symbol})</span>
                            <span className="text-3xl font-bold text-gray-800">{anchorCurrency.symbol}{Number(totalUSD).toFixed(2)}</span>
                        </div>
                        {/* Other Currencies Compact View */}
                        <div className="flex flex-wrap gap-4 justify-end">
                            {getActiveCurrencies().map(curr => {
                                const currencyTotal = totalsByCurrency?.[curr.currency_code] || 0;
                                return (
                                    <div key={curr.id} className="text-right">
                                        <span className="text-[10px] text-gray-500 block">{curr.name}</span>
                                        <span className="text-sm font-bold text-blue-600 font-mono">
                                            {curr.symbol} {currencyTotal.toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                        </span>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    <button
                        onClick={() => setIsPaymentOpen(true)}
                        disabled={cart.length === 0}
                        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-bold py-3 md:py-4 rounded-xl shadow-lg transform active:scale-95 transition-all text-lg md:text-xl flex items-center justify-center gap-2"
                    >
                        COBRAR ${Number(totalUSD).toFixed(2)}
                        <kbd className="hidden md:inline px-2 py-1 text-sm font-semibold bg-blue-700 rounded shadow-sm">F5</kbd>
                    </button>
                    {/* Botón para volver al catálogo en móvil (solo visible si estamos en modo ticket) */}
                    <button
                        onClick={() => setMobileTab('catalog')}
                        className="md:hidden w-full mt-2 text-gray-500 py-2 text-sm"
                    >
                        Seguir Comprando
                    </button>
                </div>
            </div>

            {/* MOBILE FLOATING ACTION BUTTON (Summary) - Only visible when in Catalog mode and cart has items */}
            {mobileTab === 'catalog' && cart.length > 0 && (
                <div className="md:hidden fixed bottom-6 left-4 right-4 z-30">
                    <button
                        onClick={() => setMobileTab('ticket')}
                        className="w-full bg-slate-800 text-white p-4 rounded-xl shadow-2xl flex justify-between items-center animate-bounce-slight"
                    >
                        <div className="flex items-center gap-3">
                            <div className="bg-blue-500 text-white w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm">
                                {cart.length}
                            </div>
                            <span className="font-medium">Ver / Pagar</span>
                        </div>
                        <span className="text-xl font-bold">
                            ${Number(totalUSD).toFixed(2)}
                        </span>
                    </button>
                </div>
            )}

            {/* Modals Logic Remains Same */}
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

            {/* Cash Opening Modal - only show after loading and if session is closed */}
            {!loading && !isSessionOpen && (
                <CashOpeningModal onOpen={openSession} />
            )}
        </div>
    );
};

export default POS;
