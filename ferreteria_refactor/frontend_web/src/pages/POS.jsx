
import { useState, useRef, useEffect } from 'react';
import { Search, ShoppingCart, Trash2, Edit, AlertCircle } from 'lucide-react';
import { useCart } from '../context/CartContext';
import { useCash } from '../context/CashContext';
import { Link } from 'react-router-dom';
import UnitSelectionModal from '../components/pos/UnitSelectionModal';
import EditItemModal from '../components/pos/EditItemModal';
import PaymentModal from '../components/pos/PaymentModal';
import CashOpeningModal from '../components/cash/CashOpeningModal';
import CashMovementModal from '../components/cash/CashMovementModal';

const POS = () => {
    const { cart, addToCart, removeFromCart, updateQuantity, clearCart, totalUSD, totalBs } = useCart();
    const { isSessionOpen, openSession } = useCash();

    // UI State
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedProductForAdd, setSelectedProductForAdd] = useState(null);
    const [selectedItemForEdit, setSelectedItemForEdit] = useState(null);
    const [isPaymentOpen, setIsPaymentOpen] = useState(false);
    const [isMovementOpen, setIsMovementOpen] = useState(false);

    // Refs
    const searchInputRef = useRef(null);

    // Mock Catalog Data (Normally fetched)
    const [catalog, setCatalog] = useState([
        {
            id: 1,
            name: 'Cemento Gris Portland',
            price: 5.00, // Base Price 1kg (Example)
            unit: 'KG',
            stock: 500,
            exchange_rate: 45,
            presentations: [
                { name: 'Saco 50kg', price_usd: 50.00, factor: 50 }, // Bulk price
                { name: 'Saco 25kg', price_usd: 26.00, factor: 25 }
            ]
        },
        {
            id: 2,
            name: 'Destornillador Phillips',
            price: 3.50,
            unit: 'UNID',
            stock: 20,
            exchange_rate: 45
        },
        {
            id: 3,
            name: 'Arena Lavada',
            price: 1.00,
            unit: 'M3',
            stock: 100,
            exchange_rate: 45,
            presentations: [
                { name: 'Camión 7m3', price_usd: 120.00, factor: 7 }
            ]
        },
        { id: 4, name: 'Tubería PVC 1/2', price: 4.00, unit: 'Tubo', exchange_rate: 45 },
        { id: 5, name: 'Disco Corte Metal', price: 1.25, unit: 'UNID', exchange_rate: 45 },
        { id: 6, name: 'Guantes Industriales', price: 2.50, unit: 'Par', exchange_rate: 45 },
    ]);

    const filteredCatalog = catalog.filter(p =>
        p.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const handleProductClick = (product) => {
        if (product.presentations && product.presentations.length > 0) {
            setSelectedProductForAdd(product);
        } else {
            // Direct add base unit
            addToCart(product, {
                name: product.unit,
                price_usd: product.price,
                factor: 1,
                is_base: true
            });
        }
    };

    const handleCheckout = (paymentData) => {
        console.log("Processing Sale:", paymentData, cart);
        alert("¡Venta Exitosa!");
        clearCart();
        setIsPaymentOpen(false);
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
                                {product.presentations?.length > 0 && (
                                    <span className="block text-right text-xs text-orange-500 font-medium">
                                        + {product.presentations.length} Presentaciones
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
                            key={item.id}
                            onClick={() => setSelectedItemForEdit(item)}
                            className="flex justify-between items-center p-3 hover:bg-blue-50 cursor-pointer rounded-lg border-b border-gray-100 last:border-0 transition-colors group"
                        >
                            <div className="flex-1">
                                <div className="font-medium text-gray-800 leading-snug">{item.name}</div>
                                <div className="text-xs text-gray-500 flex gap-2">
                                    <span className="bg-blue-100 text-blue-700 px-1.5 rounded">{item.unit_name}</span>
                                    <span>${item.unit_price_usd.toFixed(2)}</span>
                                </div>
                            </div>
                            <div className="flex flex-col items-end">
                                <span className="text-lg font-bold text-gray-800">x{item.quantity}</span>
                                <span className="font-bold text-blue-600">${item.subtotal_usd.toFixed(2)}</span>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Footer Totals */}
                <div className="bg-gray-50 p-4 border-t-2 border-slate-200">
                    <div className="space-y-1 mb-4">
                        <div className="flex justify-between items-end">
                            <span className="text-gray-500 text-sm font-medium">Subtotal USD</span>
                            <span className="text-xl font-bold text-gray-800">${totalUSD.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between items-end">
                            <span className="text-gray-500 text-sm font-medium">Total Bolívares</span>
                            <span className="text-lg font-bold text-blue-600">Bs {totalBs.toFixed(2)}</span>
                        </div>
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
                isOpen={!!selectedProductForAdd}
                product={selectedProductForAdd}
                onClose={() => setSelectedProductForAdd(null)}
                onSelect={(unit) => addToCart(selectedProductForAdd, unit)}
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
                onClose={() => setIsPaymentOpen(false)}
                onConfirm={handleCheckout}
            />

            <CashMovementModal
                isOpen={isMovementOpen}
                onClose={() => setIsMovementOpen(false)}
            />

            {!isSessionOpen && (
                <CashOpeningModal onOpen={openSession} />
            )}
        </div>
    );
};

export default POS;
