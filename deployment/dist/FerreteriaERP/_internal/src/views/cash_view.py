from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QGroupBox, QFormLayout, QInputDialog, QDialog,
    QDoubleSpinBox, QComboBox
)
from PyQt6.QtCore import Qt
from src.database.db import SessionLocal
from src.controllers.cash_controller import CashController

class CashWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Caja y Finanzas - Módulo 4")
        self.resize(1200, 750)
        
        self.db = SessionLocal()
        self.controller = CashController(self.db)
        
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
            
        session = self.controller.get_current_session()
        
        if session:
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
        lbl_status = QLabel(f"🟢 CAJA ABIERTA\nInicio: {session.start_time}\nFondo Inicial: ${session.initial_cash:,.2f}")
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
            self.controller.open_session(initial_usd, initial_bs)
            
            QMessageBox.information(
                self, 
                "Éxito", 
                f"Caja Abierta Correctamente\n\n"
                f"Fondo Inicial USD: ${initial_usd:,.2f}\n"
                f"Fondo Inicial Bs: Bs {initial_bs:,.2f}\n\n"
                f"(Las monedas se manejan por separado)"
            )
            self.refresh_ui()
            
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
                    # Get exchange rate if needed (though controller handles it if passed)
                    # Actually controller just stores it.
                    # We should get current rate to store with movement
                    from src.controllers.config_controller import ConfigController
                    config_ctrl = ConfigController(self.db)
                    rate = config_ctrl.get_exchange_rate()
                    
                    self.controller.add_movement("EXPENSE", amount, desc, currency, rate)
                    QMessageBox.information(self, "Éxito", "Gasto registrado")
                except Exception as e:
                    QMessageBox.warning(self, "Error", str(e))

    def handle_close_session(self):
        # Custom dialog for dual currency cash closing
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QDoubleSpinBox, QPushButton, QLabel
        
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
        from PyQt6.QtWidgets import QHBoxLayout
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
                result = self.controller.close_session(reported_usd, reported_bs)
                
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

                # Calculate Digital Totals
                digital_total = 0.0
                digital_breakdown = ""
                
                for method, amount in result['details']['sales_by_method'].items():
                    # If method is NOT cash, it's digital/bank
                    if "Efectivo" not in method:
                        digital_total += amount
                        digital_breakdown += f"- {method}: ${amount:,.2f}\n"
                
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
                
                for method, amount in result['details']['sales_by_method'].items():
                    # Check if method is Bs to format correctly
                    if "Bs" in method:
                         msg += f"- {method}: ${amount:,.2f} (USD eq)\n"
                    else:
                        msg += f"- {method}: ${amount:,.2f}\n"
                    
                msg += f"\nTOTAL VENTAS (USD eq): ${result['details']['sales_total']:,.2f}\n\n"
                msg += f"--- Movimientos de Caja ---\n"
                msg += f"- Fondo Inicial: ${result['details']['initial_usd']:,.2f} / Bs {result['details']['initial_bs']:,.2f}\n"
                msg += f"- Gastos USD: -${result['details']['expenses_usd']:,.2f}\n"
                msg += f"- Gastos Bs: -Bs {result['details']['expenses_bs']:,.2f}\n"
                msg += f"- Depósitos USD: +${result['details']['deposits_usd']:,.2f}\n"
                msg += f"- Depósitos Bs: +Bs {result['details']['deposits_bs']:,.2f}"
                
                QMessageBox.information(self, "Cierre Finalizado", msg)
                self.refresh_ui()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def closeEvent(self, event):
        self.db.close()
        event.accept()
