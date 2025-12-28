import { useState, useEffect } from 'react';
import { Plus, Search, Package, Filter, X, Trash2, Pencil } from 'lucide-react';
import ProductForm from '../components/products/ProductForm';
import BulkProductActions from '../components/products/BulkProductActions';
import InventoryValuationCard from '../components/products/InventoryValuationCard';
import ProductThumbnail from '../components/products/ProductThumbnail';
import { useConfig } from '../context/ConfigContext';
import { useWebSocket } from '../context/WebSocketContext';

import apiClient from '../config/axios';

// Helper to format stock: show as integer if whole number, otherwise show decimals
const formatStock = (stock) => {
    const num = Number(stock);
    return num % 1 === 0 ? num.toFixed(0) : num.toFixed(3).replace(/\.?0+$/, '');
};

const Products = () => {
    const { getActiveCurrencies, convertPrice, convertProductPrice } = useConfig();
    const { subscribe } = useWebSocket();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedProduct, setSelectedProduct] = useState(null); // For editing

    const [searchTerm, setSearchTerm] = useState('');
    const [products, setProducts] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    // Filters State
    const [categories, setCategories] = useState([]);
    const [exchangeRates, setExchangeRates] = useState([]);
    const [filterCategory, setFilterCategory] = useState('');
    const [filterExchangeRate, setFilterExchangeRate] = useState('');

    const fetchProducts = async () => {
        try {
            const response = await apiClient.get('/products/');
            setProducts(response.data);
        } catch (error) {
            console.error("Error fetching products:", error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDelete = async (product) => {
        if (window.confirm(`¿Estás seguro de que deseas eliminar el producto "${product.name}"?`)) {
            try {
                await apiClient.delete(`/products/${product.id}`);
                // State update is handled by WebSocket subscription
                alert("Producto eliminado correctamente");
            } catch (error) {
                console.error("Error deleting product:", error);
                alert("Error al eliminar el producto");
            }
        }
    };

    const fetchFilters = async () => {
        try {
            const [catRes, rateRes] = await Promise.all([
                apiClient.get('/categories'),
                apiClient.get('/config/exchange-rates', { params: { is_active: true } })
            ]);
            setCategories(catRes.data);
            setExchangeRates(rateRes.data);
        } catch (error) {
            console.error("Error fetching filters:", error);
        }
    };

    useEffect(() => {
        fetchProducts();
        fetchFilters();

        // WebSocket Subscriptions
        const unsubCreate = subscribe('product:created', (newProduct) => {
            setProducts(prev => [newProduct, ...prev]);
        });

        const unsubUpdate = subscribe('product:updated', (updatedProduct) => {
            setProducts(prev => prev.map(p => p.id === updatedProduct.id ? { ...p, ...updatedProduct } : p));
        });

        const unsubDelete = subscribe('product:deleted', (deletedProduct) => {
            setProducts(prev => prev.filter(p => p.id !== deletedProduct.id));
        });

        return () => {
            unsubCreate();
            unsubUpdate();
            unsubDelete();
        };
    }, [subscribe]);

    return (
        <div className="container mx-auto">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-gray-800 flex items-center">
                        <Package className="mr-2" /> Inventario de Productos
                    </h1>
                    <p className="text-gray-500">Gestiona tu catálogo y existencias</p>
                </div>
                <div className="flex items-center gap-3">
                    {/* Bulk Import/Export Actions */}
                    <BulkProductActions onImportComplete={fetchProducts} />

                    {/* Nuevo Producto Button */}
                    <button
                        onClick={() => setIsModalOpen(true)}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded flex items-center shadow-sm transition-all"
                    >
                        <Plus size={20} className="mr-2" />
                        Nuevo Producto
                    </button>
                </div>
            </div>

            {/* Valuation Dashboard (Admin Only) */}
            <InventoryValuationCard />

            {/* Filters Bar */}
            <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 mb-6 flex flex-col md:flex-row gap-4 items-center">
                <div className="relative flex-1 w-full">
                    <Search className="absolute left-3 top-2.5 text-gray-400" size={20} />
                    <input
                        type="text"
                        placeholder="Buscar por nombre, SKU..."
                        className="w-full pl-10 pr-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>

                <div className="flex gap-2 w-full md:w-auto overflow-x-auto pb-1 md:pb-0">
                    <div className="relative min-w-[150px]">
                        <select
                            value={filterCategory}
                            onChange={(e) => setFilterCategory(e.target.value)}
                            className="w-full appearance-none pl-3 pr-8 py-2 border rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                        >
                            <option value="">Todas las Categorías</option>
                            {categories.filter(cat => !cat.parent_id).map(parent => (
                                <optgroup key={parent.id} label={parent.name}>
                                    <option value={parent.id}>{parent.name}</option>
                                    {categories.filter(child => child.parent_id === parent.id).map(child => (
                                        <option key={child.id} value={child.id}>
                                            └─ {child.name}
                                        </option>
                                    ))}
                                </optgroup>
                            ))}
                            {categories.filter(cat => !cat.parent_id && !categories.some(c => c.parent_id === cat.id)).length === 0 && categories.filter(cat => !cat.parent_id).map(cat => (
                                <option key={cat.id} value={cat.id}>{cat.name}</option>
                            ))}
                        </select>
                        <Filter className="absolute right-2 top-2.5 text-gray-400 pointer-events-none" size={16} />
                    </div>

                    <div className="relative min-w-[150px]">
                        <select
                            value={filterExchangeRate}
                            onChange={(e) => setFilterExchangeRate(e.target.value)}
                            className="w-full appearance-none pl-3 pr-8 py-2 border rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                        >
                            <option value="">Todas las Tasas</option>
                            {exchangeRates.map(rate => (
                                <option key={rate.id} value={rate.id}>
                                    {rate.name}
                                </option>
                            ))}
                        </select>
                        <Filter className="absolute right-2 top-2.5 text-gray-400 pointer-events-none" size={16} />
                    </div>

                    {(filterCategory || filterExchangeRate) && (
                        <button
                            onClick={() => {
                                setFilterCategory('');
                                setFilterExchangeRate('');
                            }}
                            className="p-2 text-red-500 hover:bg-red-50 rounded-md transition-colors"
                            title="Limpiar Filtros"
                        >
                            <X size={20} />
                        </button>
                    )}
                </div>
            </div>

            {/* Desktop Table View */}
            <div className="hidden md:block bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Imagen</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Producto</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">SKU</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Precio Publico</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stock</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {products
                            .filter(product => {
                                // 1. Search Logic
                                const matchesSearch = !searchTerm || (() => {
                                    const search = searchTerm.toLowerCase();
                                    return (
                                        product.name.toLowerCase().includes(search) ||
                                        (product.sku && product.sku.toLowerCase().includes(search))
                                    );
                                })();

                                // 2. Category Filter
                                const matchesCategory = !filterCategory || product.category_id === parseInt(filterCategory);

                                // 3. Exchange Rate Filter
                                const matchesRate = !filterExchangeRate || product.exchange_rate_id === parseInt(filterExchangeRate);

                                return matchesSearch && matchesCategory && matchesRate;
                            })
                            .map(product => (
                                <tr key={product.id} className="hover:bg-gray-50 transition-colors">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <ProductThumbnail
                                            imageUrl={product.image_url}
                                            productName={product.name}
                                            updatedAt={product.updated_at}
                                            size="md"
                                        />
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center">
                                            <div className="ml-4">
                                                <div className="text-sm font-medium text-gray-900 flex items-center">
                                                    {product.name}
                                                    {product.units && product.units.length > 0 && (
                                                        <span className="ml-2 px-2 py-0.5 text-[10px] bg-purple-100 text-purple-700 rounded-full border border-purple-200">
                                                            Multi-formato
                                                        </span>
                                                    )}
                                                </div>
                                                <div className="text-sm text-gray-500">{product.unit}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{product.sku}</td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm font-semibold text-gray-900">${Number(product.price).toFixed(2)}</div>
                                        <div className="text-xs text-gray-500 flex flex-col">
                                            {getActiveCurrencies().map(currency => (
                                                <span key={currency.id}>
                                                    {convertProductPrice(product, currency.currency_code).toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} {currency.symbol}
                                                </span>
                                            ))}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${product.stock > 10 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                            {formatStock(product.stock)}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        <div className="flex items-center gap-3">
                                            <button
                                                onClick={() => {
                                                    setSelectedProduct(product);
                                                    setIsModalOpen(true);
                                                }}
                                                className="text-blue-600 hover:text-blue-800 transition-colors"
                                                title="Editar"
                                            >
                                                <Pencil size={18} />
                                            </button>
                                            <button
                                                onClick={() => handleDelete(product)}
                                                className="text-red-600 hover:text-red-900 transition-colors"
                                                title="Eliminar"
                                            >
                                                <Trash2 size={18} />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                    </tbody>
                </table>
            </div>

            {/* Mobile Card View */}
            <div className="md:hidden grid grid-cols-1 gap-4 pb-20">
                {products
                    .filter(product => {
                        const matchesSearch = !searchTerm || (() => {
                            const search = searchTerm.toLowerCase();
                            return (
                                product.name.toLowerCase().includes(search) ||
                                (product.sku && product.sku.toLowerCase().includes(search))
                            );
                        })();
                        const matchesCategory = !filterCategory || product.category_id === parseInt(filterCategory);
                        const matchesRate = !filterExchangeRate || product.exchange_rate_id === parseInt(filterExchangeRate);
                        return matchesSearch && matchesCategory && matchesRate;
                    })
                    .map(product => (
                        <div key={product.id} className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 flex flex-col gap-3">
                            <div className="flex justify-between items-start">
                                <div className="flex items-center gap-3">
                                    <ProductThumbnail
                                        imageUrl={product.image_url}
                                        productName={product.name}
                                        updatedAt={product.updated_at}
                                        size="md"
                                    />
                                    <div>
                                        <div className="font-bold text-gray-800">{product.name}</div>
                                        <div className="text-xs text-gray-500 flex gap-2">
                                            <span>{product.sku || 'Sin SKU'}</span>
                                            <span>•</span>
                                            <span>{product.unit}</span>
                                        </div>
                                    </div>
                                </div>
                                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${product.stock > 10 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                    Example: {formatStock(product.stock)}
                                </span>
                            </div>

                            <div className="flex justify-between items-end border-t pt-3 mt-1">
                                <div>
                                    <div className="text-lg font-bold text-blue-600">${Number(product.price).toFixed(2)}</div>
                                    <div className="text-xs text-gray-500 flex flex-col">
                                        {getActiveCurrencies().map(currency => (
                                            <span key={currency.id}>
                                                {convertProductPrice(product, currency.currency_code).toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} {currency.symbol}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => {
                                            setSelectedProduct(product);
                                            setIsModalOpen(true);
                                        }}
                                        className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                                    >
                                        Editar
                                    </button>
                                    <button
                                        onClick={() => handleDelete(product)}
                                        className="bg-red-50 hover:bg-red-100 text-red-600 p-2 rounded-lg transition-colors"
                                        title="Eliminar"
                                    >
                                        <Trash2 size={20} />
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                {/* Empty State Helper for Mobile */}
                {products.length === 0 && (
                    <div className="text-center py-10 text-gray-500">
                        No se encontraron productos.
                    </div>
                )}
            </div>

            <ProductForm
                isOpen={isModalOpen}
                onClose={() => {
                    setIsModalOpen(false);
                    setSelectedProduct(null); // Clear selection on close
                }}
                initialData={selectedProduct} // Pass data for editing
                onSubmit={async (productData) => {
                    try {
                        if (selectedProduct) {
                            // Edit Mode
                            await apiClient.put(`/products/${selectedProduct.id}`, productData);
                            alert("Producto actualizado exitosamente");
                        } else {
                            // Create Mode
                            await apiClient.post('/products/', productData);
                            alert("Producto creado exitosamente");
                        }
                        await fetchProducts(); // Refresh list
                        setIsModalOpen(false);
                        setSelectedProduct(null);
                    } catch (error) {
                        console.error("Error saving product:", error);
                        const errorMessage = error.response?.data?.detail || "Error al guardar producto";
                        alert(errorMessage);
                    }
                }}
            />
        </div >
    );
};

export default Products;
