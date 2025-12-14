from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QTabWidget,
    QFormLayout, QGroupBox, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit,
    QDateEdit
)
from PyQt6.QtCore import QDate, QLocale
from src.database.db import SessionLocal
from src.controllers.purchase_controller import PurchaseController
from src.controllers.supplier_controller import SupplierController
from src.models.models import Product
import datetime

class PurchaseOrderWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.setWindowTitle("Órdenes de Compra - Módulo 15")
        self.resize(1200, 750)
        
        self.db = SessionLocal()
        self.controller = PurchaseController(self.db)
        self.supplier_controller = SupplierController(self.db)
        self.user = user
        self.cart = []  # Temporary cart for creating order
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        self.setup_list_tab()
        self.setup_create_tab()
        self.setup_receive_tab()

    def setup_list_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        layout.addWidget(QLabel("Lista de Órdenes de Compra"))
        
        # Filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Estado:"))
        self.status_filter = QComboBox()
        self.status_filter.addItem("Todas", None)
        self.status_filter.addItem("Pendientes", "PENDING")
        self.status_filter.addItem("Recibidas", "RECEIVED")
        self.status_filter.addItem("Canceladas", "CANCELLED")
        filter_layout.addWidget(self.status_filter)
        
        btn_filter = QPushButton("Filtrar")
        btn_filter.clicked.connect(self.load_orders)
        filter_layout.addWidget(btn_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Table
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(7)
        self.orders_table.setHorizontalHeaderLabels([
            "ID", "Proveedor", "Fecha", "Total", "Estado", "Entrega Esperada", "Acciones"
        ])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.orders_table)
        
        self.tabs.addTab(tab, "Órdenes")
        self.load_orders()

    def setup_create_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Supplier selection
        supplier_group = QGroupBox("Información de la Orden")
        supplier_layout = QFormLayout()
        
        self.supplier_combo = QComboBox()
        self.load_suppliers()
        supplier_layout.addRow("Proveedor*:", self.supplier_combo)
        
        self.delivery_date = QDateEdit()
        self.delivery_date.setDate(QDate.currentDate().addDays(7))
        self.delivery_date.setCalendarPopup(True)
        supplier_layout.addRow("Entrega Esperada:", self.delivery_date)
        
        self.order_notes = QTextEdit()
        self.order_notes.setMaximumHeight(60)
        supplier_layout.addRow("Notas:", self.order_notes)
        
        supplier_group.setLayout(supplier_layout)
        layout.addWidget(supplier_group)
        
        # Product selection
        product_group = QGroupBox("Agregar Productos")
        product_layout = QHBoxLayout()
        
        self.product_combo = QComboBox()
        self.load_products()
        product_layout.addWidget(QLabel("Producto:"))
        product_layout.addWidget(self.product_combo)
        
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(10000)
        product_layout.addWidget(QLabel("Cantidad:"))
        product_layout.addWidget(self.quantity_spin)
        
        self.cost_spin = QDoubleSpinBox()
        self.cost_spin.setMinimum(0.01)
        self.cost_spin.setMaximum(1000000)
        self.cost_spin.setDecimals(2)
        self.cost_spin.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        product_layout.addWidget(QLabel("Costo Unit.:"))
        product_layout.addWidget(self.cost_spin)
        
        btn_add = QPushButton("Agregar")
        btn_add.clicked.connect(self.add_to_cart)
        btn_add.setStyleSheet("background-color: #4CAF50; color: white;")
        product_layout.addWidget(btn_add)
        
        product_group.setLayout(product_layout)
        layout.addWidget(product_group)
        
        # Cart table
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels([
            "Producto", "Cantidad", "Costo Unit.", "Subtotal", "Eliminar"
        ])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.cart_table)
        
        # Total and submit
        bottom_layout = QHBoxLayout()
        self.lbl_total = QLabel("Total: $0")
        self.lbl_total.setStyleSheet("font-size: 18pt; font-weight: bold; color: green;")
        bottom_layout.addWidget(self.lbl_total)
        bottom_layout.addStretch()
        
        btn_create = QPushButton("Crear Orden de Compra")
        btn_create.clicked.connect(self.create_order)
        btn_create.setStyleSheet("background-color: #2196F3; color: white; padding: 10px;")
        bottom_layout.addWidget(btn_create)
        
        layout.addLayout(bottom_layout)
        
        self.tabs.addTab(tab, "Crear Orden")

    def setup_receive_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        layout.addWidget(QLabel("Recibir Órdenes Pendientes"))
        
        # Pending orders table
        self.pending_table = QTableWidget()
        self.pending_table.setColumnCount(5)
        self.pending_table.setHorizontalHeaderLabels([
            "ID", "Proveedor", "Fecha", "Total", "Recibir"
        ])
        self.pending_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.pending_table)
        
        btn_refresh = QPushButton("Actualizar")
        btn_refresh.clicked.connect(self.load_pending_orders)
        layout.addWidget(btn_refresh)
        
        self.tabs.addTab(tab, "Recibir Orden")
        self.load_pending_orders()

    def load_suppliers(self):
        self.supplier_combo.clear()
        self.supplier_combo.addItem("Seleccione proveedor...", None)
        suppliers = self.supplier_controller.get_all_suppliers()
        for s in suppliers:
            self.supplier_combo.addItem(s.name, s.id)

    def load_products(self):
        self.product_combo.clear()
        self.product_combo.addItem("Seleccione producto...", None)
        products = self.db.query(Product).filter(Product.is_active == True).all()
        for p in products:
            self.product_combo.addItem(f"{p.name} (Stock: {p.stock})", p.id)

    def add_to_cart(self):
        product_id = self.product_combo.currentData()
        if not product_id:
            QMessageBox.warning(self, "Error", "Seleccione un producto")
            return
        
        product = self.db.query(Product).get(product_id)
        quantity = self.quantity_spin.value()
        cost = self.cost_spin.value()
        
        self.cart.append({
            'product_id': product_id,
            'product_name': product.name,
            'quantity': quantity,
            'unit_cost': cost,
            'subtotal': quantity * cost
        })
        
        self.refresh_cart()

    def refresh_cart(self):
        self.cart_table.setRowCount(0)
        total = 0
        
        for i, item in enumerate(self.cart):
            self.cart_table.insertRow(i)
            self.cart_table.setRowHeight(i, 50)
            
            self.cart_table.setItem(i, 0, QTableWidgetItem(item['product_name']))
            self.cart_table.setItem(i, 1, QTableWidgetItem(str(item['quantity'])))
            self.cart_table.setItem(i, 2, QTableWidgetItem(f"${item['unit_cost']:,.2f}"))
            self.cart_table.setItem(i, 3, QTableWidgetItem(f"${item['subtotal']:,.2f}"))
            
            btn_del = QPushButton("Eliminar")
            btn_del.setFixedWidth(70)
            btn_del.setStyleSheet("""
                QPushButton {
                    background-color: #F44336;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px;
                    font-size: 9pt;
                }
                QPushButton:hover {
                    background-color: #D32F2F;
                }
            """)
            btn_del.clicked.connect(lambda checked, idx=i: self.remove_from_cart(idx))
            self.cart_table.setCellWidget(i, 4, btn_del)
            
            total += item['subtotal']
        
        self.lbl_total.setText(f"Total: ${total:,.2f}")

    def remove_from_cart(self, index):
        del self.cart[index]
        self.refresh_cart()

    def create_order(self):
        if not self.cart:
            QMessageBox.warning(self, "Error", "Agregue productos a la orden")
            return
        
        supplier_id = self.supplier_combo.currentData()
        if not supplier_id:
            QMessageBox.warning(self, "Error", "Seleccione un proveedor")
            return
        
        delivery = self.delivery_date.date().toPyDate()
        delivery_dt = datetime.datetime.combine(delivery, datetime.time())
        notes = self.order_notes.toPlainText().strip()
        
        order, msg = self.controller.create_purchase_order(
            supplier_id, self.cart, delivery_dt, notes
        )
        
        if order:
            QMessageBox.information(self, "Éxito", f"Orden de compra #{order.id} creada correctamente")
            self.cart.clear()
            self.refresh_cart()
            self.order_notes.clear()
            self.load_orders()
            self.tabs.setCurrentIndex(0)
        else:
            QMessageBox.critical(self, "Error", msg)

    def load_orders(self):
        status = self.status_filter.currentData()
        orders = self.controller.get_all_purchase_orders(status)
        
        self.orders_table.setRowCount(0)
        for i, order in enumerate(orders):
            self.orders_table.insertRow(i)
            self.orders_table.setRowHeight(i, 50)
            
            self.orders_table.setItem(i, 0, QTableWidgetItem(str(order.id)))
            self.orders_table.setItem(i, 1, QTableWidgetItem(order.supplier.name))
            self.orders_table.setItem(i, 2, QTableWidgetItem(order.order_date.strftime('%Y-%m-%d')))
            self.orders_table.setItem(i, 3, QTableWidgetItem(f"${order.total_amount:,.2f}"))
            self.orders_table.setItem(i, 4, QTableWidgetItem(order.status))
            self.orders_table.setItem(i, 5, QTableWidgetItem(
                order.expected_delivery.strftime('%Y-%m-%d') if order.expected_delivery else "N/A"
            ))
            
            # Action button
            if order.status == "PENDING":
                btn_cancel = QPushButton("Cancelar")
                btn_cancel.setFixedWidth(70)
                btn_cancel.setStyleSheet("""
                    QPushButton {
                        background-color: #F44336;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 6px;
                        font-size: 9pt;
                    }
                    QPushButton:hover {
                        background-color: #D32F2F;
                    }
                """)
                btn_cancel.clicked.connect(lambda checked, o=order: self.cancel_order(o))
                self.orders_table.setCellWidget(i, 6, btn_cancel)

    def load_pending_orders(self):
        orders = self.controller.get_all_purchase_orders("PENDING")
        
        self.pending_table.setRowCount(0)
        for i, order in enumerate(orders):
            self.pending_table.insertRow(i)
            self.pending_table.setRowHeight(i, 50)
            
            self.pending_table.setItem(i, 0, QTableWidgetItem(str(order.id)))
            self.pending_table.setItem(i, 1, QTableWidgetItem(order.supplier.name))
            self.pending_table.setItem(i, 2, QTableWidgetItem(order.order_date.strftime('%Y-%m-%d')))
            self.pending_table.setItem(i, 3, QTableWidgetItem(f"${order.total_amount:,.2f}"))
            
            btn_receive = QPushButton("Recibir")
            btn_receive.setFixedWidth(70)
            btn_receive.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px;
                    font-size: 9pt;
                }
                QPushButton:hover {
                    background-color: #388E3C;
                }
            """)
            btn_receive.clicked.connect(lambda checked, o=order: self.receive_order(o))
            self.pending_table.setCellWidget(i, 4, btn_receive)

    def receive_order(self, order):
        reply = QMessageBox.question(
            self, "Confirmar",
            f"¿Recibir orden #{order.id} de {order.supplier.name}?\n\nEsto actualizará el inventario.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, msg = self.controller.receive_purchase_order(order.id, self.user.id)
            if success:
                QMessageBox.information(self, "Éxito", msg)
                self.load_pending_orders()
                self.load_orders()
            else:
                QMessageBox.critical(self, "Error", msg)

    def cancel_order(self, order):
        reply = QMessageBox.question(
            self, "Confirmar",
            f"¿Cancelar orden #{order.id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, msg = self.controller.cancel_purchase_order(order.id)
            if success:
                QMessageBox.information(self, "Éxito", msg)
                self.load_orders()
            else:
                QMessageBox.critical(self, "Error", msg)

    def closeEvent(self, event):
        self.db.close()
        event.accept()
