from PySide6.QtCore import QObject, Signal, Slot, Property
from src.controllers.cash_controller import CashController
from src.controllers.config_controller import ConfigController
from src.database.db import SessionLocal
from src.models.models import CashSession

class CashBridge(QObject):
    # Signals
    sessionUpdated = Signal(dict)
    message = Signal(str, str) # type (success/error), text
    historyLoaded = Signal(list)
    
    def __init__(self):
        super().__init__()
        self.db = SessionLocal()
        self.controller = CashController(self.db)
        self.config_controller = ConfigController(self.db)

    @Slot()
    def getCurrentSession(self):
        try:
            session = self.controller.get_current_session()
            if not session:
                self.sessionUpdated.emit({"status": "CLOSED"})
                return

            balance = self.controller.get_session_balance()
            if not balance:
                 # Should not happen if session is open
                 self.sessionUpdated.emit({"status": "CLOSED"})
                 return

            data = {
                "status": "OPEN",
                "id": session.id,
                "start_time": session.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "initial_usd": balance["initial_usd"],
                "initial_bs": balance["initial_bs"],
                "sales_total": balance["sales_total"],
                "expenses_usd": balance["expenses_usd"],
                "expenses_bs": balance["expenses_bs"],
                "deposits_usd": balance["deposits_usd"],
                "deposits_bs": balance["deposits_bs"],
                "expected_usd": balance["expected_usd"],
                "expected_bs": balance["expected_bs"]
            }
            self.sessionUpdated.emit(data)
            
        except Exception as e:
            print(f"Error getting session: {e}")
            self.message.emit("error", str(e))

    @Slot(float, float)
    def openSession(self, usd, bs):
        try:
            self.controller.open_session(usd, bs)
            self.getCurrentSession() # Refresh UI
            self.message.emit("success", "Caja abierta correctamente")
        except Exception as e:
            self.message.emit("error", str(e))

    @Slot(float, float)
    def closeSession(self, reported_usd, reported_bs):
        try:
            result = self.controller.close_session(reported_usd, reported_bs)
            
            # Format the closure message similarly to the PyQt view
            msg = (
                f"=== RESUMEN DE CIERRE ===\n\n"
                f"💵 EFECTIVO USD:\n"
                f"- Esperado: ${result['expected_usd']:,.2f}\n"
                f"- Contado: ${result['reported_usd']:,.2f}\n"
                f"- Diferencia: ${result['diff_usd']:,.2f}\n\n"
                f"💰 EFECTIVO Bs:\n"
                f"- Esperado: Bs {result['expected_bs']:,.2f}\n"
                f"- Contado: Bs {result['reported_bs']:,.2f}\n"
                f"- Diferencia: Bs {result['diff_bs']:,.2f}\n\n"
                f"TOTAL VENTAS: ${result['details']['sales_total']:,.2f}"
            )
            
            self.getCurrentSession() # Should emit CLOSED
            self.message.emit("success", msg)
            self.loadHistory() # Refresh history if visible
            
        except Exception as e:
            self.message.emit("error", str(e))

    @Slot(str, float, str, str)
    def addMovement(self, type, amount, currency, description):
        try:
            # Get current rate just for record, though controller might not ask for it explicit in args if it fetches internally?
            # Controller `add_movement` signature: (type, amount, description, currency='USD', exchange_rate=1.0)
            rate = self.config_controller.get_exchange_rate()
            
            self.controller.add_movement(type, amount, description, currency, rate)
            self.getCurrentSession() # Refresh totals
            self.message.emit("success", "Movimiento registrado")
        except Exception as e:
            self.message.emit("error", str(e))

    @Slot()
    def loadHistory(self):
        try:
            sessions = self.db.query(CashSession).filter(
                CashSession.status == "CLOSED"
            ).order_by(CashSession.end_time.desc()).limit(50).all()
            
            history_data = []
            for s in sessions:
                history_data.append({
                    "id": s.id,
                    "start_time": s.start_time.strftime("%Y-%m-%d %H:%M") if s.start_time else "-",
                    "end_time": s.end_time.strftime("%Y-%m-%d %H:%M") if s.end_time else "-",
                    "user": s.user.username if s.user else "N/A",
                    "initial": f"${s.initial_cash:.2f} / Bs{s.initial_cash_bs:.2f}",
                    "expected": f"${s.final_cash_expected or 0:.2f} / Bs{s.final_cash_expected_bs or 0:.2f}",
                    "reported": f"${s.final_cash_reported or 0:.2f} / Bs{s.final_cash_reported_bs or 0:.2f}",
                    "diff_usd": s.difference or 0,
                    "diff_bs": s.difference_bs or 0
                })
            
            self.historyLoaded.emit(history_data)
        except Exception as e:
            print(f"Error loading history: {e}")
