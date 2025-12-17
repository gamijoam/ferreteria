import { useState, useEffect, useRef } from 'react';
import { Search, Plus, Trash2, Save, X, AlertCircle, Package, DollarSign, Calendar, FileText } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../../config/axios';

const CreatePurchase = () => {
    const navigate = useNavigate();
    const searchInputRef = useRef(null);
    const productSearchRef = useRef(null);

    // State
    const [suppliers, setSuppliers] = useState([]);
    const [products, setProducts] = useState([]);
    const [selectedSupplier, setSelectedSupplier] = useState(null);
    const [supplierSearch, setSupplierSearch] = useState('');
    const [showSupplierDropdown, setShowSupplierDropdown] = useState(false);

    const [invoiceData, setInvoiceData] = useState({
        invoice_number: '',
        purchase_date: new Date().toISOString().split('T')[0],
        due_date: '',
        notes: ''
    });

    const [purchaseItems, setPurchaseItems] = useState([]);
    const [productSearch, setProductSearch] = useState('');
    const [filteredProducts, setFilteredProducts] = useState([]);
    const [paymentType, setPaymentType] = useState('CREDIT'); // CASH or CREDIT
    const [showCostUpdateModal, setShowCostUpdateModal] = useState(null);

    // Load suppliers and products
    useEffect(() => {
        fetchSuppliers();
        fetchProducts();
    }, []);

    const fetchSuppliers = async () => {
        try {
            const response = await apiClient.get('/suppliers');
            setSuppliers(response.data);
        } catch (error) {
            console.error('Error fetching suppliers:', error);
        }
    };

    const fetchProducts = async () => {
        try {
            const response = await apiClient.get('/products');
            setProducts(response.data);
        } catch (error) {
            console.error('Error fetching products:', error);
        }
    };

    // Filter suppliers
    const filteredSuppliers = suppliers.filter(s =>
        s.name.toLowerCase().includes(supplierSearch.toLowerCase())
    );

    // Handle supplier selection
    const handleSupplierSelect = (supplier) => {
        setSelectedSupplier(supplier);
        setSupplierSearch(supplier.name);
        setShowSupplierDropdown(false);

        // Calculate due date based on payment terms
        if (supplier.payment_terms) {
            const dueDate = new Date();
            dueDate.setDate(dueDate.getDate() + supplier.payment_terms);
            setInvoiceData(prev => ({
                ...prev,
                due_date: dueDate.toISOString().split('T')[0]
            }));
        }
    };

    // Filter products for search
    useEffect(() => {
        if (productSearch) {
            const filtered = products.filter(p =>
                p.name.toLowerCase().includes(productSearch.toLowerCase()) ||
                (p.sku && p.sku.toLowerCase().includes(productSearch.toLowerCase()))
            );
            setFilteredProducts(filtered);
        } else {
            setFilteredProducts([]);
        }
    }, [productSearch, products]);

    // Add product to purchase
    const handleAddProduct = (product) => {
        const existingItem = purchaseItems.find(item => item.product_id === product.id);

        if (existingItem) {
            setPurchaseItems(prev => prev.map(item =>
                item.product_id === product.id
                    ? { ...item, quantity: item.quantity + 1 }
                    : item
            ));
        } else {
            setPurchaseItems(prev => [...prev, {
                product_id: product.id,
                product_name: product.name,
                quantity: 1,
                unit_cost: product.cost_price || 0,
                original_cost: product.cost_price || 0,
                subtotal: product.cost_price || 0
            }]);
        }

        setProductSearch('');
        setFilteredProducts([]);
        productSearchRef.current?.focus();
    };

    // Update item quantity
    const handleQuantityChange = (productId, quantity) => {
        setPurchaseItems(prev => prev.map(item =>
            item.product_id === productId
                ? { ...item, quantity: parseFloat(quantity) || 0, subtotal: (parseFloat(quantity) || 0) * item.unit_cost }
                : item
        ));
    };

    // Update item cost
    const handleCostChange = (productId, cost) => {
        const item = purchaseItems.find(i => i.product_id === productId);
        const newCost = parseFloat(cost) || 0;

        setPurchaseItems(prev => prev.map(i =>
            i.product_id === productId
                ? { ...i, unit_cost: newCost, subtotal: i.quantity * newCost }
                : i
        ));

        // Show modal if cost changed
        if (item && newCost !== item.original_cost && newCost > 0) {
            setShowCostUpdateModal({ productId, newCost });
        }
    };

    // Remove item
    const handleRemoveItem = (productId) => {
        setPurchaseItems(prev => prev.filter(item => item.product_id !== productId));
    };

    // Calculate total
    const total = purchaseItems.reduce((sum, item) => sum + item.subtotal, 0);

    // Submit purchase
    const handleSubmit = async () => {
        if (!selectedSupplier) {
            alert('Selecciona un proveedor');
            return;
        }

        if (purchaseItems.length === 0) {
            alert('Agrega al menos un producto');
            return;
        }

        try {
            const purchaseData = {
                supplier_id: selectedSupplier.id,
                invoice_number: invoiceData.invoice_number,
                notes: invoiceData.notes,
                total_amount: total,
                items: purchaseItems.map(item => ({
                    product_id: item.product_id,
                    quantity: item.quantity,
                    unit_cost: item.unit_cost,
                    update_cost: item.unit_cost !== item.original_cost
                })),
                payment_type: paymentType
            };

            await apiClient.post('/purchases', purchaseData);
            alert('Compra registrada exitosamente');
            navigate('/purchases');
        } catch (error) {
            console.error('Error creating purchase:', error);
            alert(error.response?.data?.detail || 'Error al registrar compra');
        }
    };

    return (
        <div className="flex h-[calc(100vh-64px)] bg-gray-100">
            {/* LEFT: Product Selection (70%) */}
            <div className="w-[70%] flex flex-col p-4 border-r border-gray-300">
                {/* Supplier Selection */}
                <div className="bg-white rounded-lg shadow p-4 mb-4">
                    <h3 className="text-sm font-bold text-gray-700 mb-2">Proveedor</h3>
                    <div className="relative">
                        <input
                            ref={searchInputRef}
                            type="text"
                            value={supplierSearch}
                            onChange={(e) => {
                                setSupplierSearch(e.target.value);
                                setShowSupplierDropdown(true);
                            }}
                            onFocus={() => setShowSupplierDropdown(true)}
                            className="w-full p-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 outline-none"
                            placeholder="Buscar proveedor..."
                        />

                        {showSupplierDropdown && filteredSuppliers.length > 0 && (
                            <div className="absolute z-10 w-full mt-1 bg-white border-2 border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                                {filteredSuppliers.map(supplier => (
                                    <div
                                        key={supplier.id}
                                        onClick={() => handleSupplierSelect(supplier)}
                                        className="p-3 hover:bg-blue-50 cursor-pointer border-b last:border-b-0"
                                    >
                                        <div className="font-medium">{supplier.name}</div>
                                        <div className="text-xs text-gray-500">
                                            Crédito: {supplier.payment_terms || 0} días
                                            {supplier.credit_limit && ` | Límite: $${supplier.credit_limit}`}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {selectedSupplier && (
                        <div className="mt-2 p-2 bg-blue-50 rounded text-sm">
                            <strong>{selectedSupplier.name}</strong>
                            {selectedSupplier.current_balance > 0 && (
                                <span className="ml-2 text-red-600">
                                    Deuda actual: ${selectedSupplier.current_balance.toFixed(2)}
                                </span>
                            )}
                        </div>
                    )}
                </div>

                {/* Invoice Details */}
                <div className="bg-white rounded-lg shadow p-4 mb-4">
                    <h3 className="text-sm font-bold text-gray-700 mb-2">Datos de Factura</h3>
                    <div className="grid grid-cols-3 gap-3">
                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Nro. Control</label>
                            <input
                                type="text"
                                value={invoiceData.invoice_number}
                                onChange={(e) => setInvoiceData(prev => ({ ...prev, invoice_number: e.target.value }))}
                                className="w-full p-2 border border-gray-300 rounded focus:border-blue-500 outline-none"
                                placeholder="INV-001"
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Fecha Emisión</label>
                            <input
                                type="date"
                                value={invoiceData.purchase_date}
                                onChange={(e) => setInvoiceData(prev => ({ ...prev, purchase_date: e.target.value }))}
                                className="w-full p-2 border border-gray-300 rounded focus:border-blue-500 outline-none"
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Fecha Vencimiento</label>
                            <input
                                type="date"
                                value={invoiceData.due_date}
                                onChange={(e) => setInvoiceData(prev => ({ ...prev, due_date: e.target.value }))}
                                className="w-full p-2 border border-gray-300 rounded focus:border-blue-500 outline-none"
                            />
                        </div>
                    </div>
                </div>

                {/* Product Search */}
                <div className="mb-4 relative">
                    <Search className="absolute left-4 top-3.5 text-gray-400" size={24} />
                    <input
                        ref={productSearchRef}
                        type="text"
                        value={productSearch}
                        onChange={(e) => setProductSearch(e.target.value)}
                        className="w-full text-xl pl-12 pr-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 outline-none shadow-sm"
                        placeholder="Buscar producto para agregar..."
                    />

                    {filteredProducts.length > 0 && (
                        <div className="absolute z-10 w-full mt-1 bg-white border-2 border-gray-300 rounded-lg shadow-lg max-h-96 overflow-y-auto">
                            {filteredProducts.map(product => (
                                <div
                                    key={product.id}
                                    onClick={() => handleAddProduct(product)}
                                    className="p-4 hover:bg-blue-50 cursor-pointer border-b last:border-b-0 flex justify-between items-center"
                                >
                                    <div>
                                        <div className="font-medium">{product.name}</div>
                                        <div className="text-xs text-gray-500">
                                            Stock: {product.stock} | Costo: ${product.cost_price?.toFixed(2) || '0.00'}
                                        </div>
                                    </div>
                                    <Plus size={20} className="text-blue-600" />
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Items Table */}
                <div className="flex-1 bg-white rounded-lg shadow overflow-hidden">
                    <div className="overflow-y-auto h-full">
                        <table className="w-full">
                            <thead className="bg-gray-50 sticky top-0">
                                <tr>
                                    <th className="text-left p-3 font-semibold text-gray-700">Producto</th>
                                    <th className="text-center p-3 font-semibold text-gray-700 w-32">Cantidad</th>
                                    <th className="text-center p-3 font-semibold text-gray-700 w-40">Costo Unit.</th>
                                    <th className="text-right p-3 font-semibold text-gray-700 w-32">Subtotal</th>
                                    <th className="w-16"></th>
                                </tr>
                            </thead>
                            <tbody>
                                {purchaseItems.length === 0 ? (
                                    <tr>
                                        <td colSpan="5" className="text-center p-8 text-gray-400">
                                            <Package size={48} className="mx-auto mb-2 opacity-50" />
                                            <p>No hay productos agregados</p>
                                        </td>
                                    </tr>
                                ) : (
                                    purchaseItems.map(item => (
                                        <tr key={item.product_id} className="border-b hover:bg-gray-50">
                                            <td className="p-3">
                                                <div className="font-medium">{item.product_name}</div>
                                                {item.unit_cost !== item.original_cost && (
                                                    <div className="text-xs text-orange-600">
                                                        <AlertCircle size={12} className="inline mr-1" />
                                                        Costo modificado
                                                    </div>
                                                )}
                                            </td>
                                            <td className="p-3">
                                                <input
                                                    type="number"
                                                    value={item.quantity}
                                                    onChange={(e) => handleQuantityChange(item.product_id, e.target.value)}
                                                    className="w-full p-2 border border-gray-300 rounded text-center font-bold"
                                                    min="0"
                                                    step="0.01"
                                                />
                                            </td>
                                            <td className="p-3">
                                                <input
                                                    type="number"
                                                    value={item.unit_cost}
                                                    onChange={(e) => handleCostChange(item.product_id, e.target.value)}
                                                    className="w-full p-2 border border-gray-300 rounded text-center font-bold text-green-700"
                                                    min="0"
                                                    step="0.01"
                                                />
                                            </td>
                                            <td className="p-3 text-right font-bold text-lg">
                                                ${item.subtotal.toFixed(2)}
                                            </td>
                                            <td className="p-3">
                                                <button
                                                    onClick={() => handleRemoveItem(item.product_id)}
                                                    className="p-2 text-red-600 hover:bg-red-50 rounded"
                                                >
                                                    <Trash2 size={18} />
                                                </button>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {/* RIGHT: Summary (30%) */}
            <div className="w-[30%] bg-white flex flex-col shadow-2xl">
                <div className="bg-slate-800 text-white p-4">
                    <h2 className="text-xl font-bold flex items-center">
                        <FileText className="mr-2" /> Resumen de Compra
                    </h2>
                </div>

                <div className="flex-1 p-4 space-y-4">
                    {/* Payment Type */}
                    <div>
                        <label className="block text-sm font-bold text-gray-700 mb-2">Condición de Pago</label>
                        <div className="grid grid-cols-2 gap-2">
                            <button
                                onClick={() => setPaymentType('CASH')}
                                className={`p-3 rounded-lg font-medium transition-all ${paymentType === 'CASH'
                                        ? 'bg-green-600 text-white shadow-md'
                                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                    }`}
                            >
                                💵 Contado
                            </button>
                            <button
                                onClick={() => setPaymentType('CREDIT')}
                                className={`p-3 rounded-lg font-medium transition-all ${paymentType === 'CREDIT'
                                        ? 'bg-blue-600 text-white shadow-md'
                                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                    }`}
                            >
                                📋 Crédito
                            </button>
                        </div>
                    </div>

                    {/* Total */}
                    <div className="bg-blue-50 p-4 rounded-lg border-2 border-blue-200">
                        <div className="text-sm text-gray-600 mb-1">Total a Pagar</div>
                        <div className="text-3xl font-bold text-blue-700">
                            ${total.toFixed(2)}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                            {purchaseItems.length} producto(s)
                        </div>
                    </div>

                    {/* Notes */}
                    <div>
                        <label className="block text-sm font-bold text-gray-700 mb-2">Notas</label>
                        <textarea
                            value={invoiceData.notes}
                            onChange={(e) => setInvoiceData(prev => ({ ...prev, notes: e.target.value }))}
                            className="w-full p-2 border border-gray-300 rounded resize-none"
                            rows="3"
                            placeholder="Observaciones..."
                        />
                    </div>
                </div>

                {/* Actions */}
                <div className="p-4 border-t space-y-2">
                    <button
                        onClick={handleSubmit}
                        disabled={!selectedSupplier || purchaseItems.length === 0}
                        className="w-full bg-green-600 hover:bg-green-700 text-white py-3 rounded-lg font-bold flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        <Save className="mr-2" size={20} />
                        Procesar Ingreso
                    </button>
                    <button
                        onClick={() => navigate('/purchases')}
                        className="w-full bg-gray-200 hover:bg-gray-300 text-gray-700 py-3 rounded-lg font-bold flex items-center justify-center transition-colors"
                    >
                        <X className="mr-2" size={20} />
                        Cancelar
                    </button>
                </div>
            </div>

            {/* Cost Update Modal */}
            {showCostUpdateModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg shadow-xl p-6 max-w-md">
                        <div className="flex items-center text-orange-600 mb-4">
                            <AlertCircle size={24} className="mr-2" />
                            <h3 className="text-lg font-bold">Actualizar Costo Base</h3>
                        </div>
                        <p className="text-gray-700 mb-4">
                            El costo unitario ha cambiado. ¿Deseas actualizar el costo base del producto en el inventario?
                        </p>
                        <div className="flex gap-3">
                            <button
                                onClick={() => {
                                    // Update cost in backend
                                    setShowCostUpdateModal(null);
                                }}
                                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg font-medium"
                            >
                                Sí, Actualizar
                            </button>
                            <button
                                onClick={() => setShowCostUpdateModal(null)}
                                className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 py-2 rounded-lg font-medium"
                            >
                                No, Mantener
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CreatePurchase;
