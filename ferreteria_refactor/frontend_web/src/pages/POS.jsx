import { useState, useRef, useEffect } from 'react';
import { Search, ShoppingCart, Trash2, Plus, Minus, CreditCard, RotateCcw } from 'lucide-react';
import { useCart } from '../context/CartContext';
import { useCash } from '../context/CashContext';
import { useConfig } from '../context/ConfigContext';
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
    const { cart, addToCart, removeFromCart, updateQuantity, clearCart, totalUSD, totalBs } = useCart();
    const { isSessionOpen, openSession } = useCash();
    const { getActiveCurrencies, convertPrice, currencies } = useConfig();
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

    // Fetch Catalog and Categories
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
        const baseUnit = {
            name: product.unit_type || 'Unidad',
            price_usd: product.price,
            factor: 1,
            is_base: true
        };
        addToCart(product, baseUnit);
    };



    const handleUnitSelect = (unitOption) => {
        if (!selectedProductForUnits) return;
        const product = selectedProductForUnits;

        const unit = {
            name: unitOption.name,
            price_usd: unitOption.price, // Use the price calculated by UnitSelectionModal
            factor: unitOption.factor,
            is_base: unitOption.is_base || false
        };

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
                                <div className="text-xs text-gray-500 flex gap-2">
                                    <span className="bg-blue-100 text-blue-700 px-1.5 rounded">
                                        {item.unit_name} {item.unit_id ? <span>(x{item.conversion_factor})</span> : null}
                                    </span>
                                    <span>${(item.price_unit_usd || 0).toFixed(2)}</span>
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
                        {getActiveCurrencies().map(curr => (
                            <div key={curr.id} className="flex justify-between items-end">
                                <span className="text-gray-500 text-xs font-medium">Total {curr.name}</span>
                                <span className="text-lg font-bold text-blue-600 font-mono">
                                    {curr.symbol} {convertPrice(totalUSD, curr.symbol).toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                </span>
                            </div>
                        ))}
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
