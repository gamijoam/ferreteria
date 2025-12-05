from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
from src.database.db import SessionLocal
from src.models.models import CashSession, CashMovement

class CashHistoryWindow(QWidget):
    """Window to view cash session history"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Historial de Cierres de Caja")
        self.resize(1400, 700)
        
        self.db = SessionLocal()
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        lbl_title = QLabel("Historial de Sesiones de Caja")
        lbl_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(lbl_title)
        
        # Sessions table
        self.sessions_table = QTableWidget()
        self.sessions_table.setColumnCount(8)
        self.sessions_table.setHorizontalHeaderLabels([
            "ID", "Apertura", "Cierre", "Usuario", 
            "Inicial", "Esperado", "Real", "Diferencia"
        ])
        
        # Set column widths
        self.sessions_table.setColumnWidth(0, 50)
        self.sessions_table.setColumnWidth(1, 150)
        self.sessions_table.setColumnWidth(2, 150)
        self.sessions_table.setColumnWidth(3, 100)
        self.sessions_table.setColumnWidth(4, 150)
        self.sessions_table.setColumnWidth(5, 150)
        self.sessions_table.setColumnWidth(6, 150)
        self.sessions_table.setColumnWidth(7, 150)
        
        self.sessions_table.cellDoubleClicked.connect(self.show_details)
        layout.addWidget(self.sessions_table)
        
        # Info
        lbl_info = QLabel("Doble clic para ver detalles completos")
        lbl_info.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(lbl_info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_refresh = QPushButton("Actualizar")
        btn_refresh.clicked.connect(self.load_sessions)
        btn_refresh.setStyleSheet("background-color: #2196F3; color: white; padding: 8px;")
        btn_layout.addWidget(btn_refresh)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.load_sessions()
    
    def load_sessions(self):
        """Load all closed sessions"""
        self.sessions_table.setRowCount(0)
        
        sessions = self.db.query(CashSession).filter(
            CashSession.status == "CLOSED"
        ).order_by(CashSession.end_time.desc()).all()
        
        for i, s in enumerate(sessions):
            self.sessions_table.insertRow(i)
            
            self.sessions_table.setItem(i, 0, QTableWidgetItem(str(s.id)))
            self.sessions_table.setItem(i, 1, QTableWidgetItem(s.start_time.strftime("%Y-%m-%d %H:%M") if s.start_time else "-"))
            self.sessions_table.setItem(i, 2, QTableWidgetItem(s.end_time.strftime("%Y-%m-%d %H:%M") if s.end_time else "-"))
            
            # Show actual username
            username = s.user.username if s.user else "N/A"
            self.sessions_table.setItem(i, 3, QTableWidgetItem(username))
            
            # Amounts
            self.sessions_table.setItem(i, 4, QTableWidgetItem(f"${s.initial_cash:.2f} / Bs{s.initial_cash_bs:.2f}"))
            self.sessions_table.setItem(i, 5, QTableWidgetItem(f"${s.final_cash_expected or 0:.2f} / Bs{s.final_cash_expected_bs or 0:.2f}"))
            self.sessions_table.setItem(i, 6, QTableWidgetItem(f"${s.final_cash_reported or 0:.2f} / Bs{s.final_cash_reported_bs or 0:.2f}"))
            
            # Difference with color
            diff_usd = s.difference or 0
            diff_bs = s.difference_bs or 0
            diff_item = QTableWidgetItem(f"${diff_usd:.2f} / Bs{diff_bs:.2f}")
            
            if abs(diff_usd) < 0.01 and abs(diff_bs) < 0.01:
                diff_item.setBackground(QColor("#c8e6c9"))
            elif diff_usd < 0 or diff_bs < 0:
                diff_item.setBackground(QColor("#ffcdd2"))
                diff_item.setForeground(Qt.GlobalColor.darkRed)
            else:
                diff_item.setBackground(QColor("#fff9c4"))
                diff_item.setForeground(Qt.GlobalColor.darkGreen)
            
            self.sessions_table.setItem(i, 7, diff_item)
            self.sessions_table.setRowHeight(i, 40)
    
    def show_details(self, row, column):
        """Show session details"""
        session_id = int(self.sessions_table.item(row, 0).text())
        session = self.db.query(CashSession).get(session_id)
        
        if not session:
            QMessageBox.warning(self, "Error", "Sesión no encontrada")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Sesión #{session.id}")
        dialog.resize(900, 600)
        
        layout = QVBoxLayout()
        
        # Info
        info = f"""
<h2>Sesión de Caja #{session.id}</h2>
<p><b>Apertura:</b> {session.start_time.strftime("%Y-%m-%d %H:%M:%S") if session.start_time else "-"}</p>
<p><b>Cierre:</b> {session.end_time.strftime("%Y-%m-%d %H:%M:%S") if session.end_time else "-"}</p>
<hr>
<h3>Resumen</h3>
<table border="1" cellpadding="5">
<tr><th></th><th>USD</th><th>Bs</th></tr>
<tr><td><b>Inicial</b></td><td>${session.initial_cash:.2f}</td><td>Bs {session.initial_cash_bs:.2f}</td></tr>
<tr><td><b>Esperado</b></td><td>${session.final_cash_expected or 0:.2f}</td><td>Bs {session.final_cash_expected_bs or 0:.2f}</td></tr>
<tr><td><b>Real</b></td><td>${session.final_cash_reported or 0:.2f}</td><td>Bs {session.final_cash_reported_bs or 0:.2f}</td></tr>
<tr><td><b>Diferencia</b></td><td>${session.difference or 0:.2f}</td><td>Bs {session.difference_bs or 0:.2f}</td></tr>
</table>
"""
        
        lbl_info = QLabel(info)
        lbl_info.setWordWrap(True)
        lbl_info.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(lbl_info)
        
        # Movements
        layout.addWidget(QLabel("<h3>Movimientos:</h3>"))
        
        mov_table = QTableWidget()
        mov_table.setColumnCount(5)
        mov_table.setHorizontalHeaderLabels(["Fecha", "Tipo", "Monto", "Moneda", "Descripción"])
        
        movements = self.db.query(CashMovement).filter(
            CashMovement.session_id == session.id
        ).order_by(CashMovement.date).all()
        
        for i, m in enumerate(movements):
            mov_table.insertRow(i)
            mov_table.setItem(i, 0, QTableWidgetItem(m.date.strftime("%Y-%m-%d %H:%M")))
            mov_table.setItem(i, 1, QTableWidgetItem(m.type))
            mov_table.setItem(i, 2, QTableWidgetItem(f"${m.amount:.2f}"))
            mov_table.setItem(i, 3, QTableWidgetItem(m.currency or "USD"))
            mov_table.setItem(i, 4, QTableWidgetItem(m.description or ""))
        
        mov_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(mov_table)
        
        # Close button
        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(dialog.accept)
        layout.addWidget(btn_close)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def closeEvent(self, event):
        self.db.close()
        event.accept()
