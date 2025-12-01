import uuid
import hashlib
import os
import json
import datetime
from pathlib import Path

class LicenseController:
    def __init__(self):
        self.app_data_dir = os.path.join(os.getenv('APPDATA'), 'InventarioSoft')
        if not os.path.exists(self.app_data_dir):
            os.makedirs(self.app_data_dir)
            
        self.license_file = os.path.join(self.app_data_dir, 'license.dat')
        self.demo_file = os.path.join(self.app_data_dir, 'demo.dat')
        
    def get_hardware_id(self):
        """Get unique hardware ID based on MAC address"""
        mac = uuid.getnode()
        return hashlib.md5(str(mac).encode()).hexdigest().upper()[:16]
    
    def generate_key(self, hardware_id, days=365):
        """Generate a license key for a given hardware ID (Admin only)"""
        # Simple hash: MD5(HardwareID + SecretSalt + Days)
        secret = "INVENTARIO_SOFT_SECRET_KEY_2025"
        raw = f"{hardware_id}{secret}{days}"
        key = hashlib.sha256(raw.encode()).hexdigest().upper()[:20]
        # Format: KEY-DAYS (e.g., ABC123...-365)
        return f"{key}-{days}"
        
    def validate_key(self, key):
        """Validate if a key is valid for this machine"""
        try:
            # Split key and days
            parts = key.split('-')
            if len(parts) != 2:
                return False, 0
            
            key_part = parts[0]
            days = int(parts[1])
            
            # Re-generate expected key
            hw_id = self.get_hardware_id()
            expected_key = self.generate_key(hw_id, days).split('-')[0]
            
            if key_part == expected_key:
                return True, days
            return False, 0
        except:
            return False, 0

    def check_status(self):
        """
        Check license status.
        Returns: (status, message)
        status: 'ACTIVE', 'DEMO', 'EXPIRED', 'INVALID'
        """
        # 1. Check for valid license file
        if os.path.exists(self.license_file):
            try:
                with open(self.license_file, 'r') as f:
                    data = json.load(f)
                    
                key = data.get('key')
                activation_date = datetime.datetime.fromisoformat(data.get('activation_date'))
                days = data.get('days')
                
                # Validate key again (to prevent copying file to another PC)
                is_valid, _ = self.validate_key(key)
                if not is_valid:
                    return 'INVALID', "Licencia inválida para este equipo"
                
                # Check expiration
                expiration_date = activation_date + datetime.timedelta(days=days)
                if datetime.datetime.now() > expiration_date:
                    return 'EXPIRED', f"Licencia vencida el {expiration_date.strftime('%d/%m/%Y')}"
                
                return 'ACTIVE', f"Licencia activa hasta {expiration_date.strftime('%d/%m/%Y')}"
            except Exception as e:
                return 'INVALID', "Error al leer licencia"

        # 2. Check Demo Mode
        if os.path.exists(self.demo_file):
            try:
                with open(self.demo_file, 'r') as f:
                    start_date = datetime.datetime.fromisoformat(f.read().strip())
                
                # Demo duration: 1 day
                expiration_date = start_date + datetime.timedelta(days=1)
                
                if datetime.datetime.now() > expiration_date:
                    return 'EXPIRED', "Periodo de prueba finalizado"
                
                remaining = expiration_date - datetime.datetime.now()
                hours = int(remaining.total_seconds() / 3600)
                return 'DEMO', f"Modo Demo: {hours} horas restantes"
            except:
                # If demo file is corrupted, treat as expired
                return 'EXPIRED', "Error en archivo de demo"
        else:
            # First run: Start Demo
            with open(self.demo_file, 'w') as f:
                f.write(datetime.datetime.now().isoformat())
            return 'DEMO', "Modo Demo iniciado (24 horas)"

    def activate_license(self, key):
        """Activate a license key"""
        is_valid, days = self.validate_key(key)
        if is_valid:
            data = {
                'key': key,
                'activation_date': datetime.datetime.now().isoformat(),
                'days': days,
                'hardware_id': self.get_hardware_id()
            }
            with open(self.license_file, 'w') as f:
                json.dump(data, f)
            return True, "Licencia activada correctamente"
        return False, "Clave de licencia inválida"

    def reset_demo(self):
        """Reset demo for testing purposes"""
        if os.path.exists(self.demo_file):
            os.remove(self.demo_file)
        if os.path.exists(self.license_file):
            os.remove(self.license_file)
        return True
