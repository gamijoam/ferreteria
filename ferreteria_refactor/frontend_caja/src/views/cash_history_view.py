from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QLabel, QDialog, QMessageBox, QFrame,
    QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt
from src.controllers.cash_controller import CashController
from src.views.printer_view import PrinterConfigDialog # To reuse print logic if possible, or just instantiate controller
from src.controllers.printer_controller import PrinterController
import datetime

class CashHistoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Historial de Cierres de Caja")
        self.resize(1000, 600)
        
        self.controller = CashController()
        self.printer_controller = PrinterController()
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.setup_ui()
        self.load_history()
        
    def setup_ui(self):
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Historial de Sesiones de Caja")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)
        
        btn_refresh = QPushButton("🔄 Actualizar")
        btn_refresh.clicked.connect(self.load_history)
        header_layout.addWidget(btn_refresh)
        
        self.layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Apertura", "Cierre", "Inicial ($)", "Esperado ($)", "Diferencia ($)", "Acciones"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)
        
    def load_history(self):
        try:
            history = self.controller.get_history()
            self.table.setRowCount(0)
            
            for i, session in enumerate(history):
                self.table.insertRow(i)
                self.table.setItem(i, 0, QTableWidgetItem(str(session['id'])))
                
                start = datetime.datetime.fromisoformat(session['start_time']).strftime("%d/%m/%Y %H:%M")
                self.table.setItem(i, 1, QTableWidgetItem(start))
                
                end = "Activa"
                if session.get('end_time'):
                    end = datetime.datetime.fromisoformat(session['end_time']).strftime("%d/%m/%Y %H:%M")
                self.table.setItem(i, 2, QTableWidgetItem(end))
                
                self.table.setItem(i, 3, QTableWidgetItem(f"${(session.get('initial_cash') or 0):.2f}"))
                self.table.setItem(i, 4, QTableWidgetItem(f"${(session.get('final_cash_expected') or 0):.2f}"))
                
                diff = (session.get('final_cash_reported') or 0) - (session.get('final_cash_expected') or 0)
                diff_item = QTableWidgetItem(f"${diff:.2f}")
                if abs(diff) > 0.01:
                    diff_item.setForeground(Qt.GlobalColor.red if diff < 0 else Qt.GlobalColor.blue)
                self.table.setItem(i, 5, diff_item)
                
                # Actions
                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(0, 0, 0, 0)
                
                btn_details = QPushButton("📄 Detalles")
                btn_details.clicked.connect(lambda checked, s_id=session['id']: self.show_details(s_id))
                btn_layout.addWidget(btn_details)
                
                btn_print = QPushButton("🖨️ Imprimir")
                btn_print.clicked.connect(lambda checked, s_id=session['id']: self.print_report(s_id))
                btn_layout.addWidget(btn_print)
                
                btn_widget.setLayout(btn_layout)
                self.table.setCellWidget(i, 6, btn_widget)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar historial: {str(e)}")

    def show_details(self, session_id):
        try:
            data = self.controller.get_session_details(session_id)
            if not data:
                raise Exception("No se pudieron cargar los detalles")
            
            dialog = CashDetailDialog(data, self)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def print_report(self, session_id):
        try:
            data = self.controller.get_session_details(session_id)
            if not data:
                raise Exception("No data")
            
            # Reconstruct session object and report dict for printer controller
            # This is a bit hacky because printer controller expects objects, but we have dicts from API
            # Ideally we should adapt printer controller
            
            class DummySession:
                def __init__(self, data_dict):
                    self.id = data_dict['id']
                    self.start_time = datetime.datetime.fromisoformat(data_dict['start_time'])
                    self.end_time = datetime.datetime.fromisoformat(data_dict['end_time']) if data_dict.get('end_time') else None
                    self.initial_cash = data_dict['initial_cash']
                    self.initial_cash_bs = data_dict.get('initial_cash_bs', 0)
            
            session_obj = DummySession(data['session'])
            
            report_data = {
                "expected_usd": data['expected_usd'],
                "reported_usd": data['session'].get('final_cash_reported', 0),
                "diff_usd": data.get('diff_usd', 0),
                "expected_bs": data['expected_bs'],
                "reported_bs": data['session'].get('final_cash_reported_bs', 0),
                "diff_bs": data.get('diff_bs', 0)
            }
            
            self.printer_controller.print_cash_report(session_obj, report_data)
            
            QMessageBox.information(self, "Éxito", "Reporte reenviado a la impresora")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al imprimir: {str(e)}")

class CashDetailDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Detalle de Sesión #{data['session']['id']}")
        self.resize(600, 700)
        self.data = data
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        session = self.data['session']
        details = self.data['details']
        
        # Summary Group
        grp_summary = QFrame()
        grp_summary.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        l_summary = QVBoxLayout()
        grp_summary.setLayout(l_summary)
        
        start = datetime.datetime.fromisoformat(session['start_time']).strftime("%d/%m/%Y %H:%M")
        end = datetime.datetime.fromisoformat(session['end_time']).strftime("%d/%m/%Y %H:%M") if session.get('end_time') else "N/A"
        
        l_summary.addWidget(QLabel(f"<b>Apertura:</b> {start}"))
        l_summary.addWidget(QLabel(f"<b>Cierre:</b> {end}"))
        l_summary.addWidget(QLabel(f"<b>Estado:</b> {session['status']}"))
        
        layout.addWidget(grp_summary)
        
        # Details Grid
        grid = QGridLayout()
        
        # Headers
        grid.addWidget(QLabel("<b>Concepto</b>"), 0, 0)
        grid.addWidget(QLabel("<b>USD ($)</b>"), 0, 1)
        grid.addWidget(QLabel("<b>Bs</b>"), 0, 2)
        
        row = 1
        # Initial
        grid.addWidget(QLabel("Caja Inicial"), row, 0)
        grid.addWidget(QLabel(f"{details['initial_usd']:.2f}"), row, 1)
        grid.addWidget(QLabel(f"{details.get('initial_bs', 0):.2f}"), row, 2)
        row += 1
        
        # Sales (Cash) -> Need to parse from details['sales_by_method']
        # This is a simplification, relying on calculated totals passed in 'sales_total' roughly
        # Better to show total sales
        grid.addWidget(QLabel("Ventas Totales (Eq)"), row, 0)
        grid.addWidget(QLabel(f"{details.get('sales_total', 0):.2f}"), row, 1)
        grid.addWidget(QLabel("-"), row, 2)
        row += 1
        
        # Expenses
        grid.addWidget(QLabel("Gastos/Salidas"), row, 0)
        grid.addWidget(QLabel(f"{details.get('expenses_usd', 0):.2f}"), row, 1)
        grid.addWidget(QLabel(f"{details.get('expenses_bs', 0):.2f}"), row, 2)
        row += 1
        
        # Deposits
        grid.addWidget(QLabel("Ingresos/Depósitos"), row, 0)
        grid.addWidget(QLabel(f"{details.get('deposits_usd', 0):.2f}"), row, 1)
        grid.addWidget(QLabel(f"{details.get('deposits_bs', 0):.2f}"), row, 2)
        row += 1
        
        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        grid.addWidget(line, row, 0, 1, 3)
        row += 1
        
        # Expected
        grid.addWidget(QLabel("<b>Total Esperado</b>"), row, 0)
        grid.addWidget(QLabel(f"<b>{self.data['expected_usd']:.2f}</b>"), row, 1)
        grid.addWidget(QLabel(f"<b>{self.data['expected_bs']:.2f}</b>"), row, 2)
        row += 1
        
        # Reported
        grid.addWidget(QLabel("Total Declarado"), row, 0)
        grid.addWidget(QLabel(f"{(session.get('final_cash_reported') or 0):.2f}"), row, 1)
        grid.addWidget(QLabel(f"{(session.get('final_cash_reported_bs') or 0):.2f}"), row, 2)
        row += 1
        
        # Diff
        grid.addWidget(QLabel("<b>Diferencia</b>"), row, 0)
        diff_usd = self.data['diff_usd']
        diff_bs = self.data['diff_bs']
        
        lbl_diff_usd = QLabel(f"{diff_usd:.2f}")
        if abs(diff_usd) > 0.01:
            lbl_diff_usd.setStyleSheet("color: red;" if diff_usd < 0 else "color: blue;")
        grid.addWidget(lbl_diff_usd, row, 1)
            
        lbl_diff_bs = QLabel(f"{diff_bs:.2f}")
        if abs(diff_bs) > 0.01:
            lbl_diff_bs.setStyleSheet("color: red;" if diff_bs < 0 else "color: blue;")
        grid.addWidget(lbl_diff_bs, row, 2)
        
        layout.addLayout(grid)
        
        # Sales Breakdown
        layout.addWidget(QLabel("Checking breakdown..."))
        if 'sales_by_method' in details and details['sales_by_method']:
            gb = QFrame()
            l_gb = QVBoxLayout()
            gb.setLayout(l_gb)
            l_gb.addWidget(QLabel("<b>Desglose de Ventas:</b>"))
            
            for method, amount in details['sales_by_method'].items():
                l_gb.addWidget(QLabel(f"{method}: {amount:.2f}"))
            
            layout.addWidget(gb)
        
        layout.addStretch()
        
        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
