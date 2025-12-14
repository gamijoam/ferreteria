# from src.models.models import Sale, CashSession, Quote, BusinessConfig # Don't import models to avoid DB dependency issues if possible, or keep as type hints only
from src.controllers.config_controller import ConfigController
import datetime
import json

try:
    from escpos.printer import Usb, Network, Win32Raw, Dummy
    from escpos import printer
    ESCPOS_AVAILABLE = True
except ImportError:
    ESCPOS_AVAILABLE = False
    print("Warning: python-escpos not installed. Printer functionality limited.")

from PIL import Image
import os

# PDF Generation for preview
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Warning: reportlab not installed. PDF preview not available.")

class PrinterController:
    def __init__(self, db=None):
        self.db = None # Ignored
        self.config_ctrl = ConfigController()
        self.printer = None
        self.template = self.load_template()
        
    def load_template(self):
        """Load ticket template from config or use default"""
        template_str = self.config_ctrl.get_config("ticket_template", "")
        
        if template_str:
            try:
                return json.loads(template_str)
            except:
                pass
        
        # Default template
        return {
            "show_logo": True,
            "show_business_name": True,
            "show_rif": True,
            "show_address": True,
            "show_phone": True,
            "show_barcode": True,
            "header_text": "TICKET DE VENTA",
            "footer_text": "¡GRACIAS POR SU COMPRA!",
            "show_exchange_rate": True,
            "font_size": "normal"  # small, normal, large
        }
    
    def save_template(self, template):
        """Save custom ticket template"""
        self.config_ctrl.set_config("ticket_template", json.dumps(template))
        self.template = template
        
    def get_printer_config(self):
        """Get printer configuration from database"""
        printer_type = self.config_ctrl.get_config("printer_type", "Windows")
        printer_connection = self.config_ctrl.get_config("printer_connection", "USB")
        printer_params_str = self.config_ctrl.get_config("printer_params", "{}")
        
        try:
            printer_params = json.loads(printer_params_str)
        except:
            printer_params = {}
            
        return {
            "type": printer_type,
            "connection": printer_connection,
            "params": printer_params
        }
    
    def save_printer_config(self, printer_type, connection, params):
        """Save printer configuration to database"""
        self.config_ctrl.set_config("printer_type", printer_type)
        self.config_ctrl.set_config("printer_connection", connection)
        self.config_ctrl.set_config("printer_params", json.dumps(params))
        
    def detect_usb_printers(self):
        """Detect USB ESC/POS printers"""
        if not ESCPOS_AVAILABLE:
            return []
        
        detected = []
        try:
            # Try common vendor IDs for thermal printers
            common_vendors = [
                (0x04b8, "Epson"),      # Epson
                (0x0519, "Star"),       # Star Micronics
                (0x154f, "Bixolon"),    # Bixolon
                (0x0fe6, "Custom"),     # Custom
            ]
            
            import usb.core
            for vid, name in common_vendors:
                devices = usb.core.find(find_all=True, idVendor=vid)
                for dev in devices:
                    detected.append({
                        "name": f"{name} Printer",
                        "vendor_id": hex(vid),
                        "product_id": hex(dev.idProduct),
                        "connection": "USB"
                    })
        except Exception as e:
            print(f"USB detection error: {e}")
            
        return detected
    
    def connect_printer(self):
        """Connect to configured printer"""
        if not ESCPOS_AVAILABLE:
            return None
            
        config = self.get_printer_config()
        
        try:
            if config["type"] == "ESC/POS":
                if config["connection"] == "USB":
                    params = config["params"]
                    vid = int(params.get("vendor_id", "0x04b8"), 16)
                    pid = int(params.get("product_id", "0x0e15"), 16)
                    self.printer = Usb(vid, pid)
                    
                elif config["connection"] == "Network":
                    params = config["params"]
                    host = params.get("host", "192.168.1.100")
                    port = int(params.get("port", 9100))
                    self.printer = Network(host, port)
                    
            elif config["type"] == "Windows":
                printer_name = config["params"].get("printer_name", "")
                if printer_name:
                    self.printer = Win32Raw(printer_name)
                else:
                    # Use default Windows printer
                    self.printer = Win32Raw()
                    
            return self.printer
            
        except Exception as e:
            print(f"Printer connection error: {e}")
            return None
    
    def test_print(self):
        """Print a test page"""
        if not self.connect_printer():
            raise Exception("No se pudo conectar a la impresora")
        
        try:
            self.printer.text("========================================\n")
            self.printer.set(align='center', text_type='B', width=2, height=2)
            self.printer.text("PRUEBA DE IMPRESORA\n")
            self.printer.set()
            self.printer.text("========================================\n\n")
            
            business_name = self.config_ctrl.get_config("BUSINESS_NAME", "InventarioSoft")
            self.printer.set(align='center')
            self.printer.text(f"{business_name}\n\n")
            
            self.printer.set(align='left')
            self.printer.text(f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.printer.text(f"Impresora configurada correctamente\n\n")
            
            self.printer.text("========================================\n")
            self.printer.set(align='center')
            self.printer.text("Prueba exitosa\n")
            self.printer.text("========================================\n\n")
            
            self.printer.cut()
            self.printer.close()
            
            return True
            
        except Exception as e:
            raise Exception(f"Error al imprimir: {str(e)}")
    
    def print_ticket(self, sale):
        """Print sale ticket"""
        if not self.connect_printer():
            raise Exception("No se pudo conectar a la impresora")
        
        try:
            # Print logo if configured
            logo_path = self.config_ctrl.get_config("business_logo_path", "")
            print_logo = self.config_ctrl.get_config("print_logo_on_ticket", "false") == "true"
            
            if logo_path and print_logo and os.path.exists(logo_path) and self.template.get("show_logo", True):
                try:
                    img = Image.open(logo_path)
                    # Resize to fit thermal printer (max 512px width)
                    img.thumbnail((512, 200))
                    self.printer.image(img, center=True)
                except Exception as e:
                    print(f"Logo print error: {e}")
            
            # Header
            self.printer.text("========================================\n")
            self.printer.set(align='center', text_type='B')
            
            business_name = self.config_ctrl.get_config("BUSINESS_NAME", "InventarioSoft")
            business_rif = self.config_ctrl.get_config("BUSINESS_RIF", "")
            business_address = self.config_ctrl.get_config("BUSINESS_ADDRESS", "")
            business_phone = self.config_ctrl.get_config("BUSINESS_PHONE", "")
            
            if self.template.get("show_business_name", True):
                self.printer.text(f"{business_name}\n")
            self.printer.set()
            if business_rif and self.template.get("show_rif", True):
                self.printer.text(f"RIF: {business_rif}\n")
            if business_address and self.template.get("show_address", True):
                self.printer.text(f"{business_address}\n")
            if business_phone and self.template.get("show_phone", True):
                self.printer.text(f"Tel: {business_phone}\n")
            
            self.printer.text("========================================\n")
            
            # Sale info
            self.printer.set(align='left')
            self.printer.text(f"Fecha: {sale.date.strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.printer.text(f"Ticket #: {sale.id}\n")
            self.printer.text("----------------------------------------\n")
            
            # Items
            self.printer.text("PRODUCTO          CANT  PRECIO   TOTAL\n")
            self.printer.text("----------------------------------------\n")
            
            for detail in sale.details:
                product_name = detail.product.name[:17].ljust(17)
                qty = str(int(detail.quantity)).rjust(4)
                price = f"${detail.unit_price:.2f}".rjust(8)
                total = f"${detail.subtotal:.2f}".rjust(8)
                self.printer.text(f"{product_name} {qty} {price} {total}\n")
            
            self.printer.text("----------------------------------------\n")
            
            # Totals
            self.printer.set(align='right')
            self.printer.text(f"TOTAL: ${sale.total_amount:.2f}\n\n")
            
            # Payment info
            self.printer.set(align='left')
            self.printer.text(f"Método de Pago: {sale.payment_method}\n")
            
            if sale.exchange_rate_used and sale.exchange_rate_used > 1 and self.template.get("show_exchange_rate", True):
                self.printer.text(f"Tasa: 1 USD = {sale.exchange_rate_used:.2f} Bs\n")
                if sale.total_amount_bs:
                    self.printer.text(f"Total Bs: Bs {sale.total_amount_bs:.2f}\n")
            
            # Footer
            self.printer.text("\n========================================\n")
            self.printer.set(align='center')
            footer_text = self.template.get("footer_text", "¡GRACIAS POR SU COMPRA!")
            self.printer.text(f"{footer_text}\n")
            self.printer.text("========================================\n\n")
            
            # Barcode
            if self.template.get("show_barcode", True):
                try:
                    self.printer.barcode(str(sale.id), 'CODE39', width=2, height=50, pos='BELOW')
                except:
                    pass
            
            self.printer.text("\n\n")
            self.printer.cut()
            self.printer.close()
            
            return True
            
        except Exception as e:
            raise Exception(f"Error al imprimir ticket: {str(e)}")
    
    def generate_pdf_preview(self, sale, output_path: str):
        """Generate PDF preview of ticket for testing without printer"""
        if not REPORTLAB_AVAILABLE:
            raise Exception("reportlab no está instalado. No se puede generar PDF.")
        
        try:
            c = canvas.Canvas(output_path, pagesize=(80*mm, 200*mm))
            
            y = 190*mm  # Start from top
            
            # Logo
            logo_path = self.config_ctrl.get_config("business_logo_path", "")
            if logo_path and os.path.exists(logo_path) and self.template.get("show_logo", True):
                try:
                    c.drawImage(logo_path, 10*mm, y-20*mm, width=60*mm, height=15*mm, preserveAspectRatio=True)
                    y -= 22*mm
                except:
                    pass
            
            # Business info
            c.setFont("Helvetica-Bold", 12)
            business_name = self.config_ctrl.get_config("BUSINESS_NAME", "InventarioSoft")
            if self.template.get("show_business_name", True):
                c.drawCentredString(40*mm, y, business_name)
                y -= 5*mm
            
            c.setFont("Helvetica", 8)
            business_rif = self.config_ctrl.get_config("BUSINESS_RIF", "")
            business_address = self.config_ctrl.get_config("BUSINESS_ADDRESS", "")
            business_phone = self.config_ctrl.get_config("BUSINESS_PHONE", "")
            
            if business_rif and self.template.get("show_rif", True):
                c.drawCentredString(40*mm, y, f"RIF: {business_rif}")
                y -= 4*mm
            if business_address and self.template.get("show_address", True):
                c.drawCentredString(40*mm, y, business_address)
                y -= 4*mm
            if business_phone and self.template.get("show_phone", True):
                c.drawCentredString(40*mm, y, f"Tel: {business_phone}")
                y -= 4*mm
            
            # Line
            c.line(5*mm, y, 75*mm, y)
            y -= 5*mm
            
            # Sale info
            c.setFont("Helvetica", 8)
            c.drawString(5*mm, y, f"Fecha: {sale.date.strftime('%Y-%m-%d %H:%M')}")
            y -= 4*mm
            c.drawString(5*mm, y, f"Ticket #: {sale.id}")
            y -= 5*mm
            
            # Items header
            c.setFont("Helvetica-Bold", 7)
            c.drawString(5*mm, y, "PRODUCTO")
            c.drawString(40*mm, y, "CANT")
            c.drawString(50*mm, y, "PRECIO")
            c.drawString(62*mm, y, "TOTAL")
            y -= 4*mm
            
            # Items
            c.setFont("Helvetica", 7)
            for detail in sale.details:
                product_name = detail.product.name[:15]
                c.drawString(5*mm, y, product_name)
                c.drawString(40*mm, y, str(int(detail.quantity)))
                c.drawString(50*mm, y, f"${detail.unit_price:.2f}")
                c.drawString(62*mm, y, f"${detail.subtotal:.2f}")
                y -= 4*mm
            
            # Line
            c.line(5*mm, y, 75*mm, y)
            y -= 5*mm
            
            # Total
            c.setFont("Helvetica-Bold", 10)
            c.drawString(40*mm, y, f"TOTAL: ${sale.total_amount:.2f}")
            y -= 6*mm
            
            # Payment info
            c.setFont("Helvetica", 8)
            c.drawString(5*mm, y, f"Pago: {sale.payment_method}")
            y -= 4*mm
            
            if sale.exchange_rate_used and sale.exchange_rate_used > 1 and self.template.get("show_exchange_rate", True):
                c.drawString(5*mm, y, f"Tasa: 1 USD = {sale.exchange_rate_used:.2f} Bs")
                y -= 4*mm
                if sale.total_amount_bs:
                    c.drawString(5*mm, y, f"Total Bs: Bs {sale.total_amount_bs:.2f}")
                    y -= 4*mm
            
            # Footer
            y -= 5*mm
            c.setFont("Helvetica-Bold", 9)
            footer_text = self.template.get("footer_text", "¡GRACIAS POR SU COMPRA!")
            c.drawCentredString(40*mm, y, footer_text)
            
            c.save()
            return output_path
            
        except Exception as e:
            raise Exception(f"Error al generar PDF: {str(e)}")
    
    def print_cash_report(self, session, report_data: dict):
        """Print cash closing report"""
        if not self.connect_printer():
            raise Exception("No se pudo conectar a la impresora")
        
        try:
            # Header
            self.printer.text("========================================\n")
            self.printer.set(align='center', text_type='B', width=2, height=2)
            self.printer.text("CIERRE DE CAJA\n")
            self.printer.set()
            self.printer.text("========================================\n\n")
            
            business_name = self.config_ctrl.get_config("BUSINESS_NAME", "InventarioSoft")
            self.printer.set(align='center')
            self.printer.text(f"{business_name}\n\n")
            
            # Session info
            self.printer.set(align='left')
            self.printer.text(f"Apertura: {session.start_time.strftime('%Y-%m-%d %H:%M')}\n")
            self.printer.text(f"Cierre: {session.end_time.strftime('%Y-%m-%d %H:%M') if session.end_time else 'N/A'}\n")
            self.printer.text("========================================\n\n")
            
            # USD Section
            self.printer.set(text_type='B')
            self.printer.text("EFECTIVO USD:\n")
            self.printer.set()
            self.printer.text(f"Esperado: ${report_data['expected_usd']:.2f}\n")
            self.printer.text(f"Contado:  ${report_data['reported_usd']:.2f}\n")
            diff_usd = report_data['diff_usd']
            status_usd = "OK" if abs(diff_usd) < 0.01 else ("+" if diff_usd > 0 else "-")
            self.printer.text(f"Diferencia: {status_usd}${abs(diff_usd):.2f}\n\n")
            
            # Bs Section
            self.printer.set(text_type='B')
            self.printer.text("EFECTIVO Bs:\n")
            self.printer.set()
            self.printer.text(f"Esperado: Bs {report_data['expected_bs']:.2f}\n")
            self.printer.text(f"Contado:  Bs {report_data['reported_bs']:.2f}\n")
            diff_bs = report_data['diff_bs']
            status_bs = "OK" if abs(diff_bs) < 0.01 else ("+" if diff_bs > 0 else "-")
            self.printer.text(f"Diferencia: {status_bs}Bs {abs(diff_bs):.2f}\n\n")
            
            self.printer.text("========================================\n")
            self.printer.set(align='center')
            self.printer.text("FIN DEL REPORTE\n")
            self.printer.text("========================================\n\n")
            
            self.printer.cut()
            self.printer.close()
            
            return True
            
        except Exception as e:
            raise Exception(f"Error al imprimir reporte: {str(e)}")
