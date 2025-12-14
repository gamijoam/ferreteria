from frontend_caja.services.cash_service import CashService
import datetime

class CashController:
    def __init__(self, db=None):
        self.service = CashService()
        self.current_user_id = 1 # Simplification for now
        self.active_session = None

    def check_active_session(self):
        """Check if there is an open session for current user"""
        session = self.service.get_current_session(self.current_user_id)
        if session:
            self.active_session = session
            return True
        return False

    def open_cash_register(self, initial_usd, initial_bs):
        """Open a new cash session"""
        result = self.service.open_session(self.current_user_id, initial_usd, initial_bs)
        if result:
            self.active_session = result
            return True
        return False

    def close_cash_register(self, reported_usd, reported_bs):
        """Close the current session"""
        if not self.active_session:
            raise ValueError("No hay sesión activa")
        
        session_id = self.active_session['id']
        result = self.service.close_session(session_id, reported_usd, reported_bs)
        if result:
            self.active_session = None
            return result # Returns closed session with diffs
        raise Exception("Error al cerrar caja")

    def register_movement(self, amount, type_mov, reason, currency="USD"):
        """Register a cash movement (Ingreso/Retiro)"""
        # Ensure we have active session ID, service handles mapping if missing but better to pass it
        session_id = self.active_session['id'] if self.active_session else None
        
        return self.service.add_movement(amount, type_mov, reason, currency, session_id)
