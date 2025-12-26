import { useState } from 'react';
import apiClient from '../../config/axios';
import { Download, Upload, FileSpreadsheet, FileText, AlertCircle, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';

const BulkProductActions = ({ onImportComplete }) => {
    const [uploading, setUploading] = useState(false);
    const [importResult, setImportResult] = useState(null);

    const downloadTemplate = async () => {
        try {
            const response = await apiClient.get('/products/template', {
                responseType: 'blob'
            });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'plantilla_productos.xlsx');
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);

            toast.success('Plantilla descargada correctamente');
        } catch (error) {
            console.error('Error downloading template:', error);
            toast.error('Error al descargar plantilla');
        }
    };

    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        if (!file.name.endsWith('.xlsx')) {
            toast.error('Solo se permiten archivos .xlsx');
            return;
        }

        setUploading(true);
        setImportResult(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await apiClient.post('/products/import', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            setImportResult(response.data);

            if (response.data.success) {
                toast.success(`✅ ${response.data.created} productos creados exitosamente`);
                if (onImportComplete) {
                    onImportComplete();
                }
            } else {
                toast.error(`❌ Error: ${response.data.errors.length} errores encontrados`);
            }
        } catch (error) {
            console.error('Error importing products:', error);
            toast.error(error.response?.data?.detail || 'Error al importar productos');
            setImportResult({
                success: false,
                created: 0,
                errors: [error.response?.data?.detail || 'Error desconocido']
            });
        } finally {
            setUploading(false);
            // Reset file input
            event.target.value = '';
        }
    };

    const exportToExcel = async () => {
        try {
            toast.loading('Generando archivo Excel...');

            const response = await apiClient.get('/products/export/excel', {
                responseType: 'blob'
            });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            const filename = `inventario_${new Date().toISOString().split('T')[0]}.xlsx`;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);

            toast.dismiss();
            toast.success('Inventario exportado a Excel');
        } catch (error) {
            toast.dismiss();
            console.error('Error exporting to Excel:', error);
            toast.error('Error al exportar a Excel');
        }
    };

    const exportToPDF = async () => {
        try {
            toast.loading('Generando archivo PDF...');

            const response = await apiClient.get('/products/export/pdf', {
                responseType: 'blob'
            });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            const filename = `inventario_${new Date().toISOString().split('T')[0]}.pdf`;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);

            toast.dismiss();
            toast.success('Inventario exportado a PDF');
        } catch (error) {
            toast.dismiss();
            console.error('Error exporting to PDF:', error);
            toast.error('Error al exportar a PDF');
        }
    };

    return (
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                📦 Gestión Masiva de Productos
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Import Section */}
                <div className="border border-gray-200 rounded-lg p-4">
                    <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
                        <Upload size={20} className="text-blue-600" />
                        Importar Productos
                    </h3>

                    <div className="space-y-3">
                        <div className="bg-blue-50 border-l-4 border-blue-400 p-3 text-sm">
                            <p className="font-semibold text-blue-800 mb-1">Pasos:</p>
                            <ol className="list-decimal list-inside text-blue-700 space-y-1">
                                <li>Descargar plantilla Excel</li>
                                <li>Completar con sus datos</li>
                                <li>Subir archivo completado</li>
                            </ol>
                        </div>

                        <button
                            onClick={downloadTemplate}
                            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                        >
                            <Download size={18} />
                            Descargar Plantilla
                        </button>

                        <div className="relative">
                            <input
                                type="file"
                                accept=".xlsx"
                                onChange={handleFileUpload}
                                disabled={uploading}
                                className="hidden"
                                id="file-upload"
                            />
                            <label
                                htmlFor="file-upload"
                                className={`w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg transition-colors cursor-pointer ${uploading
                                        ? 'bg-gray-400 cursor-not-allowed'
                                        : 'bg-blue-600 hover:bg-blue-700 text-white'
                                    }`}
                            >
                                <Upload size={18} />
                                {uploading ? 'Subiendo...' : 'Subir Excel'}
                            </label>
                        </div>
                    </div>

                    {/* Import Result */}
                    {importResult && (
                        <div className={`mt-4 p-3 rounded-lg ${importResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
                            }`}>
                            <div className="flex items-start gap-2">
                                {importResult.success ? (
                                    <CheckCircle size={20} className="text-green-600 flex-shrink-0 mt-0.5" />
                                ) : (
                                    <AlertCircle size={20} className="text-red-600 flex-shrink-0 mt-0.5" />
                                )}
                                <div className="flex-1">
                                    <p className={`font-semibold ${importResult.success ? 'text-green-800' : 'text-red-800'}`}>
                                        {importResult.success
                                            ? `✅ ${importResult.created} productos creados`
                                            : `❌ ${importResult.errors.length} errores encontrados`
                                        }
                                    </p>
                                    {!importResult.success && importResult.errors.length > 0 && (
                                        <div className="mt-2 max-h-40 overflow-y-auto">
                                            <ul className="text-sm text-red-700 space-y-1">
                                                {importResult.errors.slice(0, 10).map((error, idx) => (
                                                    <li key={idx} className="flex items-start gap-1">
                                                        <span className="text-red-500">•</span>
                                                        <span>{error}</span>
                                                    </li>
                                                ))}
                                                {importResult.errors.length > 10 && (
                                                    <li className="text-red-600 font-semibold">
                                                        ... y {importResult.errors.length - 10} errores más
                                                    </li>
                                                )}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Export Section */}
                <div className="border border-gray-200 rounded-lg p-4">
                    <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
                        <Download size={20} className="text-green-600" />
                        Exportar Inventario
                    </h3>

                    <div className="space-y-3">
                        <p className="text-sm text-gray-600 mb-4">
                            Descargue el inventario completo en formato Excel o PDF
                        </p>

                        <button
                            onClick={exportToExcel}
                            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                        >
                            <FileSpreadsheet size={18} />
                            Exportar a Excel
                        </button>

                        <button
                            onClick={exportToPDF}
                            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                        >
                            <FileText size={18} />
                            Exportar a PDF
                        </button>

                        <div className="bg-gray-50 border border-gray-200 rounded p-3 text-sm text-gray-600">
                            <p className="font-semibold mb-1">Incluye:</p>
                            <ul className="list-disc list-inside space-y-1">
                                <li>Todos los productos activos</li>
                                <li>Información completa</li>
                                <li>Formato profesional</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default BulkProductActions;
