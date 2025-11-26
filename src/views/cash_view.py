from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QGroupBox, QFormLayout, QInputDialog, QDialog
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
        layout = QFormLayout()
        
        self.initial_input = QLineEdit()
        self.initial_input.setPlaceholderText("Monto inicial (ej: 10000)")
        
        btn_open = QPushButton("Abrir Caja")
        btn_open.clicked.connect(self.handle_open_session)
        
        layout.addRow("Fondo de Caja:", self.initial_input)
        layout.addRow(btn_open)
        
        group.setLayout(layout)
        self.layout.addWidget(group)
        self.layout.addStretch()

    def show_open_session_ui(self, session):
        lbl_status = QLabel(f"🟢 CAJA ABIERTA\nInicio: {session.start_time}\nFondo Inicial: ${session.initial_cash:,.0f}")
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
            amount_text = self.initial_input.text()
            if not amount_text.isdigit():
                raise ValueError("Ingrese un monto válido")
            
            amount = float(amount_text)
            self.controller.open_session(amount)
            QMessageBox.information(self, "Éxito", "Caja Abierta Correctamente")
            self.refresh_ui()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def handle_expense(self):
        amount, ok = QInputDialog.getDouble(self, "Registrar Gasto", "Monto del Gasto:")
        if ok and amount > 0:
            desc, ok2 = QInputDialog.getText(self, "Descripción", "Motivo del Gasto:")
            if ok2 and desc:
                try:
                    self.controller.add_movement("EXPENSE", amount, desc)
                    QMessageBox.information(self, "Éxito", "Gasto registrado")
                except Exception as e:
                    QMessageBox.warning(self, "Error", str(e))

    def handle_close_session(self):
        # Blind Close: Ask user to count money
        reported, ok = QInputDialog.getDouble(self, "Cierre de Caja", "Ingrese el TOTAL de efectivo que hay en caja:")
        if ok:
            try:
                result = self.controller.close_session(reported)
                
                diff = result["difference"]
                status = "CORRECTO"
                color = "green"
                if diff > 0:
                    status = f"SOBRANTE (+${diff:,.0f})"
                    color = "blue"
                elif diff < 0:
                    status = f"FALTANTE (-${abs(diff):,.0f})"
                    color = "red"
                
                msg = (
                    f"=== RESUMEN DE CIERRE ===\n\n"
                    f"Esperado (Sistema): ${result['expected']:,.0f}\n"
                    f"Reportado (Cajero): ${result['reported']:,.0f}\n"
                    f"Diferencia: {status}\n\n"
                    f"Detalles:\n"
                    f"- Inicial: ${result['details']['initial']:,.0f}\n"
                    f"- Ventas: ${result['details']['sales']:,.0f}\n"
                    f"- Gastos: -${result['details']['expenses']:,.0f}"
                )
                
                QMessageBox.information(self, "Cierre Finalizado", msg)
                self.refresh_ui()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def closeEvent(self, event):
        self.db.close()
        event.accept()
