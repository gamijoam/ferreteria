from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QGroupBox, QFormLayout, QInputDialog, QDialog,
    QDoubleSpinBox, QComboBox
)
from PyQt6.QtCore import Qt
# from src.database.db import SessionLocal # REMOVED
from src.controllers.cash_controller import CashController
from src.controllers.config_controller import ConfigController

class CashWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Caja y Finanzas - Módulo 4")
        self.resize(1200, 750)
        
        # self.db = SessionLocal() # REMOVED
        self.controller = CashController(db=None) 
        self.config_controller = ConfigController(db=None)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.refresh_ui()

    def refresh_ui(self):
        # Clear layout safely
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            
        # Check active session via API
        active = self.controller.check_active_session()
        
        if active:
            session = self.controller.active_session
            # Mapping API response to object-like access if needed, or using dict
            # CashController.active_session comes from API so it's a dict (from requests .json())
            self.show_open_session_ui(session)
        else:
            self.show_closed_session_ui()

    def show_closed_session_ui(self):
        group = QGroupBox("Apertura de Caja")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Instructions
        instructions = QLabel("Ingrese el fondo inicial en cada moneda:")
        instructions.setStyleSheet("font-size: 12px; padding: 5px;")
        layout.addWidget(instructions)
        
        # Form
        from PyQt6.QtWidgets import QFormLayout, QDoubleSpinBox
        form_layout = QFormLayout()
        
        self.initial_usd_input = QDoubleSpinBox()
        self.initial_usd_input.setRange(0, 999999.99)
        self.initial_usd_input.setDecimals(2)
        self.initial_usd_input.setPrefix("$ ")
        self.initial_usd_input.setStyleSheet("font-size: 14px; padding: 5px;")
        
        self.initial_bs_input = QDoubleSpinBox()
        self.initial_bs_input.setRange(0, 999999999.99)
        self.initial_bs_input.setDecimals(2)
        self.initial_bs_input.setPrefix("Bs ")
        self.initial_bs_input.setStyleSheet("font-size: 14px; padding: 5px;")
        
        form_layout.addRow("Fondo USD:", self.initial_usd_input)
        form_layout.addRow("Fondo Bs:", self.initial_bs_input)
        layout.addLayout(form_layout)
        
        btn_open = QPushButton("Abrir Caja")
        btn_open.setStyleSheet("background-color: #28a745; color: white; padding: 10px; font-weight: bold;")
        btn_open.clicked.connect(self.handle_open_session)
        layout.addWidget(btn_open)
        
        group.setLayout(layout)
        self.layout.addWidget(group)
        self.layout.addStretch()

    def show_open_session_ui(self, session):
        # Session is a dict now
        start_time = session.get('start_time')
        initial_cash = session.get('initial_cash', 0.0)
        
        lbl_status = QLabel(f"🟢 CAJA ABIERTA\nInicio: {start_time}\nFondo Inicial: ${initial_cash:,.2f}")
        lbl_status.setStyleSheet("font-size: 16px; font-weight: bold; color: green;")
        lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(lbl_status)
        
        # Movements
        btn_expense = QPushButton("Registrar Gasto / Retiro")
        btn_expense.clicked.connect(self.handle_expense)
        self.layout.addWidget(btn_expense)
        
        # Close
        btn_close = QPushButton("CERRAR CAJA (Cierre Ciego)")
        btn_close.setStyleSheet("background-color: red; color: white; font-weight: bold; padding: 10px;")
        btn_close.clicked.connect(self.handle_close_session)
        self.layout.addWidget(btn_close)
        
        self.layout.addStretch()

    def handle_open_session(self):
        try:
            initial_usd = self.initial_usd_input.value()
            initial_bs = self.initial_bs_input.value()
            
            # Pass both USD and Bs to controller
            if self.controller.open_cash_register(initial_usd, initial_bs):
                QMessageBox.information(
                    self, 
                    "Éxito", 
                    f"Caja Abierta Correctamente\n\n"
                    f"Fondo Inicial USD: ${initial_usd:,.2f}\n"
                    f"Fondo Inicial Bs: Bs {initial_bs:,.2f}\n\n"
                    f"(Las monedas se manejan por separado)"
                )
                self.refresh_ui()
            else:
                 # If it failed, it might be because it's already open (400 Bad Request).
                 # Let's try to refresh UI to see if we are actually open.
                 active = self.controller.check_active_session()
                 if active:
                     QMessageBox.warning(self, "Aviso", "La caja ya estaba abierta. Se ha actualizado la vista.")
                     self.refresh_ui()
                 else:
                     QMessageBox.warning(self, "Error", "No se pudo abrir la caja. \nSi el error persiste, cierre sesión o contacte soporte.")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def handle_expense(self):
        # Custom dialog for expense
        dialog = QDialog(self)
        dialog.setWindowTitle("Registrar Gasto / Retiro")
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        form = QFormLayout()
        
        amount_spin = QDoubleSpinBox()
        amount_spin.setRange(0.01, 999999.99)
        amount_spin.setDecimals(2)
        form.addRow("Monto:", amount_spin)
        
        currency_combo = QComboBox()
        currency_combo.addItems(["USD", "Bs"])
        form.addRow("Moneda:", currency_combo)
        
        desc_input = QLineEdit()
        form.addRow("Descripción:", desc_input)
        
        layout.addLayout(form)
        
        btn_ok = QPushButton("Registrar")
        btn_ok.clicked.connect(dialog.accept)
        layout.addWidget(btn_ok)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            amount = amount_spin.value()
            currency = currency_combo.currentText()
            desc = desc_input.text()
            
            if amount > 0 and desc:
                try:
                    # Get rate via config service (API)
                    # Note: Controller API calls for movement usually don't need rate stored in movement directly 
                    # if backend handles it, but currently logic is mixed. 
                    # For layout consistency we assume backend handles Logic.
                    
                    self.controller.register_movement(amount, "OUT", desc, currency)
                    QMessageBox.information(self, "Éxito", "Gasto registrado")
                except Exception as e:
                    QMessageBox.warning(self, "Error", str(e))

    def handle_close_session(self):
        # Custom dialog for dual currency cash closing
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QDoubleSpinBox, QPushButton, QLabel, QHBoxLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Cierre de Caja")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        # Title
        title = QLabel("Contar Efectivo en Caja")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Form
        form_layout = QFormLayout()
        
        # USD input
        usd_spin = QDoubleSpinBox()
        usd_spin.setRange(0, 999999.99)
        usd_spin.setDecimals(2)
        usd_spin.setPrefix("$ ")
        usd_spin.setStyleSheet("font-size: 14px; padding: 5px;")
        
        # Bs input
        bs_spin = QDoubleSpinBox()
        bs_spin.setRange(0, 999999999.99)
        bs_spin.setDecimals(2)
        bs_spin.setPrefix("Bs ")
        bs_spin.setStyleSheet("font-size: 14px; padding: 5px;")
        
        form_layout.addRow("Efectivo USD:", usd_spin)
        form_layout.addRow("Efectivo Bs:", bs_spin)
        layout.addLayout(form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        btn_ok = QPushButton("Cerrar Caja")
        btn_ok.setStyleSheet("background-color: #dc3545; color: white; padding: 10px; font-weight: bold;")
        btn_ok.clicked.connect(dialog.accept)
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet("background-color: gray; color: white; padding: 10px;")
        btn_cancel.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        layout.addLayout(btn_layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                reported_usd = usd_spin.value()
                reported_bs = bs_spin.value()
                
                # Get expected cash from controller (dual currency)
                # RESULT IS NOW A DICT FROM API: { "session": {...}, "details": {...}, ... }
                result = self.controller.close_cash_register(reported_usd, reported_bs)
                
                # USD Status
                diff_usd = result["diff_usd"]
                status_usd = "CORRECTO"
                if diff_usd > 0.01:
                    status_usd = f"SOBRANTE (+${diff_usd:,.2f})"
                elif diff_usd < -0.01:
                    status_usd = f"FALTANTE (-${abs(diff_usd):,.2f})"
                    
                # Bs Status
                diff_bs = result["diff_bs"]
                status_bs = "CORRECTO"
                if diff_bs > 0.01:
                    status_bs = f"SOBRANTE (+Bs {diff_bs:,.2f})"
                elif diff_bs < -0.01:
                    status_bs = f"FALTANTE (-Bs {abs(diff_bs):,.2f})"

                # Calculate Digital Totals from details
                details = result['details']
                sales_by_method = details.get('sales_by_method', {})
                
                digital_total = 0.0
                digital_breakdown = ""
                
                for key, amount in sales_by_method.items():
                    # method key format: "Method (Currency)"
                    # If method is NOT cash, it's digital/bank
                    # Check method name
                    if "Efectivo" not in key:
                        digital_total += amount
                        digital_breakdown += f"- {key}: ${amount:,.2f}\n"
                
                if digital_total == 0:
                    digital_breakdown = "(Sin movimientos digitales)\n"

                msg = (
                    f"=== RESUMEN DE CIERRE ===\n\n"
                    f"💵 EFECTIVO USD:\n"
                    f"- Esperado (Sistema): ${result['expected_usd']:,.2f}\n"
                    f"- Contado (Físico): ${reported_usd:,.2f}\n"
                    f"- Diferencia: {status_usd}\n\n"
                    f"💰 EFECTIVO Bs:\n"
                    f"- Esperado (Sistema): Bs {result['expected_bs']:,.2f}\n"
                    f"- Contado (Físico): Bs {reported_bs:,.2f}\n"
                    f"- Diferencia: {status_bs}\n\n"
                    f"💳 DINERO DIGITAL / BANCO:\n"
                    f"{digital_breakdown}"
                    f"TOTAL DIGITAL: ${digital_total:,.2f}\n"
                    f"(Verificar en cuenta bancaria)\n\n"
                    f"--- Desglose de Ventas ---\n"
                )
                
                for key, amount in sales_by_method.items():
                     msg += f"- {key}: ${amount:,.2f}\n"
                    
                msg += f"\nTOTAL VENTAS (USD eq): ${details.get('sales_total', 0):,.2f}\n\n"
                msg += f"--- Movimientos de Caja ---\n"
                msg += f"- Fondo Inicial: ${details.get('initial_usd', 0):,.2f} / Bs {details.get('initial_bs', 0):,.2f}\n"
                msg += f"- Gastos USD: -${details.get('expenses_usd', 0):,.2f}\n"
                msg += f"- Gastos Bs: -Bs {details.get('expenses_bs', 0):,.2f}\n"
                msg += f"- Depósitos USD: +${details.get('deposits_usd', 0):,.2f}\n"
                msg += f"- Depósitos Bs: +Bs {details.get('deposits_bs', 0):,.2f}"
                
                QMessageBox.information(self, "Cierre Finalizado", msg)
                self.refresh_ui()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def closeEvent(self, event):
        # self.db.close() # REMOVED
        event.accept()
