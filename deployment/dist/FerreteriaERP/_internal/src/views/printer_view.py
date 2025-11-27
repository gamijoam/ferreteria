from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QGroupBox, QFormLayout, QMessageBox, QCheckBox
)
from PyQt6.QtGui import QFont
from src.database.db import SessionLocal
from src.controllers.printer_controller import PrinterController

class PrinterConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración de Impresora")
        self.resize(600, 500)
        
        self.db = SessionLocal()
        self.controller = PrinterController(self.db)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.setup_ui()
        self.load_current_config()
        
    def setup_ui(self):
        # Title
        title = QLabel("Configurar Impresora Térmica")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.layout.addWidget(title)
        
        # Printer Type
        type_group = QGroupBox("Tipo de Impresora")
        type_layout = QFormLayout()
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["ESC/POS", "Windows"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        type_layout.addRow("Tipo:", self.type_combo)
        
        type_group.setLayout(type_layout)
        self.layout.addWidget(type_group)
        
        # Connection Type (for ESC/POS)
        self.connection_group = QGroupBox("Conexión")
        connection_layout = QFormLayout()
        
        self.connection_combo = QComboBox()
        self.connection_combo.addItems(["USB", "Network"])
        self.connection_combo.currentTextChanged.connect(self.on_connection_changed)
        connection_layout.addRow("Tipo de Conexión:", self.connection_combo)
        
        self.connection_group.setLayout(connection_layout)
        self.layout.addWidget(self.connection_group)
        
        # USB Parameters
        self.usb_group = QGroupBox("Parámetros USB")
        usb_layout = QFormLayout()
        
        self.vendor_id_input = QLineEdit()
        self.vendor_id_input.setPlaceholderText("0x04b8 (Epson)")
        usb_layout.addRow("Vendor ID:", self.vendor_id_input)
        
        self.product_id_input = QLineEdit()
        self.product_id_input.setPlaceholderText("0x0e15")
        usb_layout.addRow("Product ID:", self.product_id_input)
        
        btn_detect = QPushButton("Detectar Impresoras USB")
        btn_detect.clicked.connect(self.detect_usb)
        usb_layout.addRow("", btn_detect)
        
        self.usb_group.setLayout(usb_layout)
        self.layout.addWidget(self.usb_group)
        
        # Network Parameters
        self.network_group = QGroupBox("Parámetros de Red")
        network_layout = QFormLayout()
        
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("192.168.1.100")
        network_layout.addRow("IP Address:", self.host_input)
        
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("9100")
        self.port_input.setText("9100")
        network_layout.addRow("Puerto:", self.port_input)
        
        self.network_group.setLayout(network_layout)
        self.layout.addWidget(self.network_group)
        
        # Windows Printer
        self.windows_group = QGroupBox("Impresora Windows")
        windows_layout = QFormLayout()
        
        self.windows_printer_input = QLineEdit()
        self.windows_printer_input.setPlaceholderText("Dejar vacío para usar predeterminada")
        windows_layout.addRow("Nombre:", self.windows_printer_input)
        
        self.windows_group.setLayout(windows_layout)
        self.layout.addWidget(self.windows_group)
        
        # Auto-print option
        self.auto_print_check = QCheckBox("Imprimir tickets automáticamente después de cada venta")
        self.auto_print_check.setChecked(True)
        self.layout.addWidget(self.auto_print_check)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        btn_template = QPushButton("✏️ Editar Plantilla")
        btn_template.setStyleSheet("background-color: #9c27b0; color: white; padding: 10px; font-weight: bold;")
        btn_template.clicked.connect(self.edit_template)
        btn_layout.addWidget(btn_template)
        
        btn_pdf = QPushButton("📄 Vista Previa PDF")
        btn_pdf.setStyleSheet("background-color: #2196f3; color: white; padding: 10px; font-weight: bold;")
        btn_pdf.clicked.connect(self.preview_pdf)
        btn_layout.addWidget(btn_pdf)
        
        btn_test = QPushButton("Prueba de Impresión")
        btn_test.setStyleSheet("background-color: #17a2b8; color: white; padding: 10px; font-weight: bold;")
        btn_test.clicked.connect(self.test_printer)
        btn_layout.addWidget(btn_test)
        
        btn_save = QPushButton("Guardar Configuración")
        btn_save.setStyleSheet("background-color: #28a745; color: white; padding: 10px; font-weight: bold;")
        btn_save.clicked.connect(self.save_config)
        btn_layout.addWidget(btn_save)
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet("background-color: #6c757d; color: white; padding: 10px;")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        self.layout.addLayout(btn_layout)
        
        # Initial visibility
        self.on_type_changed(self.type_combo.currentText())
        
    def on_type_changed(self, printer_type):
        """Show/hide relevant groups based on printer type"""
        is_escpos = (printer_type == "ESC/POS")
        
        self.connection_group.setVisible(is_escpos)
        self.usb_group.setVisible(is_escpos and self.connection_combo.currentText() == "USB")
        self.network_group.setVisible(is_escpos and self.connection_combo.currentText() == "Network")
        self.windows_group.setVisible(not is_escpos)
        
    def on_connection_changed(self, connection_type):
        """Show/hide USB or Network parameters"""
        self.usb_group.setVisible(connection_type == "USB")
        self.network_group.setVisible(connection_type == "Network")
        
    def detect_usb(self):
        """Detect USB printers"""
        try:
            printers = self.controller.detect_usb_printers()
            
            if not printers:
                QMessageBox.information(
                    self,
                    "Detección USB",
                    "No se detectaron impresoras USB ESC/POS.\n\n"
                    "Asegúrese de que:\n"
                    "1. La impresora esté conectada y encendida\n"
                    "2. Los drivers estén instalados\n"
                    "3. La impresora sea compatible con ESC/POS"
                )
                return
            
            # Show detected printers
            msg = "Impresoras detectadas:\n\n"
            for i, p in enumerate(printers, 1):
                msg += f"{i}. {p['name']}\n"
                msg += f"   Vendor ID: {p['vendor_id']}\n"
                msg += f"   Product ID: {p['product_id']}\n\n"
            
            msg += "¿Usar la primera impresora detectada?"
            
            reply = QMessageBox.question(
                self,
                "Impresoras Detectadas",
                msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes and printers:
                self.vendor_id_input.setText(printers[0]['vendor_id'])
                self.product_id_input.setText(printers[0]['product_id'])
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al detectar impresoras: {str(e)}")
            
    def load_current_config(self):
        """Load current printer configuration"""
        config = self.controller.get_printer_config()
        
        # Set printer type
        index = self.type_combo.findText(config['type'])
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
        
        # Set connection type
        index = self.connection_combo.findText(config['connection'])
        if index >= 0:
            self.connection_combo.setCurrentIndex(index)
        
        # Set parameters
        params = config['params']
        if 'vendor_id' in params:
            self.vendor_id_input.setText(params['vendor_id'])
        if 'product_id' in params:
            self.product_id_input.setText(params['product_id'])
        if 'host' in params:
            self.host_input.setText(params['host'])
        if 'port' in params:
            self.port_input.setText(str(params['port']))
        if 'printer_name' in params:
            self.windows_printer_input.setText(params['printer_name'])
            
        # Auto-print
        auto_print = self.controller.config_ctrl.get_config("auto_print_tickets", "true")
        self.auto_print_check.setChecked(auto_print == "true")
        
    def save_config(self):
        """Save printer configuration"""
        try:
            printer_type = self.type_combo.currentText()
            connection = self.connection_combo.currentText()
            
            params = {}
            
            if printer_type == "ESC/POS":
                if connection == "USB":
                    params['vendor_id'] = self.vendor_id_input.text() or "0x04b8"
                    params['product_id'] = self.product_id_input.text() or "0x0e15"
                elif connection == "Network":
                    params['host'] = self.host_input.text() or "192.168.1.100"
                    params['port'] = int(self.port_input.text() or "9100")
            else:  # Windows
                params['printer_name'] = self.windows_printer_input.text()
            
            self.controller.save_printer_config(printer_type, connection, params)
            
            # Save auto-print preference
            self.controller.config_ctrl.set_config(
                "auto_print_tickets",
                "true" if self.auto_print_check.isChecked() else "false"
            )
            
            QMessageBox.information(
                self,
                "Éxito",
                "Configuración de impresora guardada correctamente"
            )
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar configuración: {str(e)}")
            
    def test_printer(self):
        """Test printer connection"""
        # Save current config first
        self.save_config()
        
        try:
            self.controller.test_print()
            QMessageBox.information(
                self,
                "Éxito",
                "Prueba de impresión exitosa.\nVerifique que el ticket se haya impreso correctamente."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error en la prueba de impresión:\n\n{str(e)}\n\n"
                "Verifique que:\n"
                "1. La impresora esté encendida\n"
                "2. Los parámetros sean correctos\n"
                "3. Los drivers estén instalados"
            )
    
    def preview_pdf(self):
        """Generate PDF preview of a sample ticket"""
        try:
            # Create a sample sale for preview
            from src.models.models import Sale
            import datetime
            import os
            
            # Get the most recent sale or create dummy data
            sale = self.db.query(Sale).order_by(Sale.id.desc()).first()
            
            if not sale:
                QMessageBox.warning(
                    self,
                    "Sin Ventas",
                    "No hay ventas registradas para generar vista previa.\n\n"
                    "Realice una venta primero para ver cómo se vería el ticket."
                )
                return
            
            # Generate PDF
            output_path = os.path.join(os.path.expanduser("~"), "Desktop", f"ticket_preview_{sale.id}.pdf")
            self.controller.generate_pdf_preview(sale, output_path)
            
            # Open PDF
            import subprocess
            subprocess.Popen([output_path], shell=True)
            
            QMessageBox.information(
                self,
                "Vista Previa Generada",
                f"PDF generado exitosamente:\n\n{output_path}\n\n"
                "El archivo se abrirá automáticamente."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al generar vista previa:\n\n{str(e)}"
            )
    
    def edit_template(self):
        """Open template editor dialog"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QCheckBox, QLineEdit, QPushButton, QLabel
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Editor de Plantilla de Ticket")
        dialog.resize(500, 400)
        
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        title = QLabel("Personalizar Formato del Ticket")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        form = QFormLayout()
        
        # Load current template
        template = self.controller.template
        
        # Checkboxes for visibility
        show_logo = QCheckBox()
        show_logo.setChecked(template.get("show_logo", True))
        form.addRow("Mostrar Logo:", show_logo)
        
        show_business_name = QCheckBox()
        show_business_name.setChecked(template.get("show_business_name", True))
        form.addRow("Mostrar Nombre del Negocio:", show_business_name)
        
        show_rif = QCheckBox()
        show_rif.setChecked(template.get("show_rif", True))
        form.addRow("Mostrar RIF:", show_rif)
        
        show_address = QCheckBox()
        show_address.setChecked(template.get("show_address", True))
        form.addRow("Mostrar Dirección:", show_address)
        
        show_phone = QCheckBox()
        show_phone.setChecked(template.get("show_phone", True))
        form.addRow("Mostrar Teléfono:", show_phone)
        
        show_barcode = QCheckBox()
        show_barcode.setChecked(template.get("show_barcode", True))
        form.addRow("Mostrar Código de Barras:", show_barcode)
        
        show_exchange_rate = QCheckBox()
        show_exchange_rate.setChecked(template.get("show_exchange_rate", True))
        form.addRow("Mostrar Tasa de Cambio:", show_exchange_rate)
        
        # Text fields
        header_text = QLineEdit()
        header_text.setText(template.get("header_text", "TICKET DE VENTA"))
        form.addRow("Texto del Encabezado:", header_text)
        
        footer_text = QLineEdit()
        footer_text.setText(template.get("footer_text", "¡GRACIAS POR SU COMPRA!"))
        form.addRow("Texto del Pie:", footer_text)
        
        layout.addLayout(form)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        btn_save = QPushButton("Guardar Plantilla")
        btn_save.setStyleSheet("background-color: #28a745; color: white; padding: 10px;")
        btn_save.clicked.connect(lambda: self.save_template(
            dialog,
            {
                "show_logo": show_logo.isChecked(),
                "show_business_name": show_business_name.isChecked(),
                "show_rif": show_rif.isChecked(),
                "show_address": show_address.isChecked(),
                "show_phone": show_phone.isChecked(),
                "show_barcode": show_barcode.isChecked(),
                "show_exchange_rate": show_exchange_rate.isChecked(),
                "header_text": header_text.text(),
                "footer_text": footer_text.text(),
                "font_size": "normal"
            }
        ))
        btn_layout.addWidget(btn_save)
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet("background-color: #6c757d; color: white; padding: 10px;")
        btn_cancel.clicked.connect(dialog.reject)
        btn_layout.addWidget(btn_cancel)
        
        layout.addLayout(btn_layout)
        
        dialog.exec()
    
    def save_template(self, dialog, template):
        """Save custom template"""
        try:
            self.controller.save_template(template)
            QMessageBox.information(
                dialog,
                "Éxito",
                "Plantilla guardada correctamente.\n\n"
                "Los cambios se aplicarán en las próximas impresiones."
            )
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(dialog, "Error", f"Error al guardar plantilla: {str(e)}")
            
    def closeEvent(self, event):
        self.db.close()
        event.accept()
