from fastapi import FastAPI, HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from jinja2 import Template
import re
import datetime

import os
import sys
from dotenv import load_dotenv

# FIX: PyInstaller --noconsole sets stdout/stderr to None, causing Uvicorn logging to crash
# FIX: Also force UTF-8 to prevent UnicodeEncodeError when writing emojis to devnull on Windows
# FIX: PyInstaller --noconsole sets stdout/stderr to None.
# Redirect to FILE for debugging instead of devnull.
if sys.stdout is None:
    sys.stdout = open("bridge_debug.log", "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open("bridge_debug.log", "w", encoding="utf-8")

# Cargar variables de entorno desde .env (si existe)
load_dotenv()

# ========================================
# NUCLEAR OPTION: BaseHTTPMiddleware for PNA
# ========================================
class PNACORSMiddleware(BaseHTTPMiddleware):
    """
    Low-level CORS + Private Network Access middleware
    Handles Chrome's strict PNA requirements at Starlette level
    """
    async def dispatch(self, request: Request, call_next):
        # Get origin
        origin = request.headers.get("Origin", "*")
        
        print(f"🔍 [{request.method}] {request.url.path} from {origin}")
        
        # ===== PREFLIGHT (OPTIONS) HANDLING =====
        if request.method == "OPTIONS":
            print("   🔒 PREFLIGHT - Returning immediate response")
            
            # Create empty response with 204 No Content
            response = Response(
                content="",
                status_code=204,
                media_type="text/plain"
            )
            
            # CRITICAL HEADERS (order matters for Chrome)
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["Access-Control-Allow-Private-Network"] = "true"
            response.headers["Access-Control-Max-Age"] = "3600"
            
            print(f"   ✅ Headers: {dict(response.headers)}")
            return response
        
        # ===== NORMAL REQUEST PROCESSING =====
        response = await call_next(request)
        
        # Inject CORS + PNA headers to actual response
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Private-Network"] = "true"
        
        print(f"   ✅ Response sent with PNA")
        return response

# Initialize FastAPI app
app = FastAPI()

# Add PNA middleware (FIRST, before any other middleware)
app.add_middleware(PNACORSMiddleware)

# "VIRTUAL" (archivo/consola), "USB" (impresora real via Zadig), o "WINDOWS" (driver instalado)
PRINTER_MODE = os.getenv("PRINTER_MODE", "WINDOWS").upper()
PRINTER_NAME = os.getenv("PRINTER_NAME", "POS-58") # Nombre exacto en "Dispositivos e Impresoras"

# ========================================
# HELPER: LIST WINDOWS PRINTERS
# ========================================
def get_windows_printers():
    printers = []
    try:
        import win32print
        # Enum PRINTER_ENUM_LOCAL | PRINTER_ENUM_CONNECTIONS
        for p in win32print.EnumPrinters(2 | 4):
            printers.append(p[2]) # p[2] is printer name
    except Exception as e:
        print(f"Error listing printers: {e}")
    return printers


# ========================================
# JINJA2 TEMPLATE SYSTEM
# ========================================

def parse_format_tags(line, printer_output):
    """
    Parse custom formatting tags and apply ESC/POS commands
    
    Supported tags:
    - <center>, <left>, <right>: Alignment
    - <bold>: Bold text
    - <cut>: Paper cut
    
    Args:
        line: Line of text with potential tags
        printer_output: List to append formatted output
    """
    # Track formatting state
    align = 'left'
    bold = False
    
    # Extract alignment
    if '<center>' in line:
        align = 'center'
        line = line.replace('<center>', '').replace('</center>', '')
    elif '<right>' in line:
        align = 'right'
        line = line.replace('<right>', '').replace('</right>', '')
    elif '<left>' in line:
        align = 'left'
        line = line.replace('<left>', '').replace('</left>', '')
    
    # Extract bold
    if '<bold>' in line:
        bold = True
        line = line.replace('<bold>', '').replace('</bold>', '')
    
    # Check for cut command
    if '<cut>' in line:
        printer_output.append({'type': 'cut'})
        return
    
    # Skip empty lines
    if not line.strip():
        return
    
    # Apply formatting and add to output
    printer_output.append({
        'type': 'text',
        'content': line,
        'align': align,
        'bold': bold
    })

def print_from_template(template_str, context_data):
    """
    Render Jinja2 template and parse for ESC/POS formatting
    
    Args:
        template_str: Jinja2 template string
        context_data: Dictionary with template variables
        
    Returns:
        List of formatted print commands
    """
    # Step 1: Render Jinja2 template
    template = Template(template_str)
    rendered = template.render(context_data)
    
    # Step 2: Process line by line for formatting tags
    printer_output = []
    lines = rendered.split('\n')
    
    for line in lines:
        parse_format_tags(line, printer_output)
    
    return printer_output

def format_virtual_ticket(commands):
    """
    Format print commands as virtual ticket text
    
    Args:
        commands: List of print commands from print_from_template
        
    Returns:
        Formatted text string
    """
    width = 48
    lines = []
    
    for cmd in commands:
        if cmd['type'] == 'cut':
            lines.append('\n' + '=' * width + ' [CORTE] ' + '=' * width + '\n')
        elif cmd['type'] == 'text':
            content = cmd['content']
            align = cmd['align']
            bold = cmd['bold']
            
            # Apply bold (uppercase for virtual)
            if bold:
                content = content.upper()
            
            # Apply alignment
            if align == 'center':
                formatted = f"{content:^{width}}"
            elif align == 'right':
                formatted = f"{content:>{width}}"
            else:  # left
                formatted = f"{content:<{width}}"
            
            lines.append(formatted)
    
    return '\n'.join(lines)

# ========================================
# API ENDPOINTS
# ========================================

@app.post("/print")
async def print_ticket(request: Request):
    """
    Print ticket from Jinja2 template
    
    Payload:
    {
        "template": "Jinja2 template string",
        "context": {
            "business": {...},
            "sale": {...}
        }
    }
    """
    try:
        data = await request.json()
        template_str = data.get('template')
        context = data.get('context', {})
        
        print(f"🔍 DEBUG: Received template length: {len(template_str) if template_str else 0}")
        print(f"🔍 DEBUG: Context keys: {list(context.keys())}")
        
        # DEBUG: Print template line 18
        template_lines = template_str.split('\n')
        if len(template_lines) >= 18:
            print(f"🔍 DEBUG: Template line 18: {template_lines[17]}")
        
        # DEBUG: Print sale.items structure
        if 'sale' in context and 'items' in context['sale']:
            print(f"🔍 DEBUG: sale.items type: {type(context['sale']['items'])}")
            print(f"🔍 DEBUG: sale.items is list: {isinstance(context['sale']['items'], list)}")
        
        if not template_str:
            raise HTTPException(status_code=400, detail="Template is required")
        
        # Render template and parse tags
        print("🔍 DEBUG: Starting template rendering...")
        commands = print_from_template(template_str, context)
        print(f"🔍 DEBUG: Generated {len(commands)} commands")
        
        if PRINTER_MODE == "VIRTUAL":
            content = format_virtual_ticket(commands)
            
            # 1. Print to console
            print("=== NUEVA IMPRESION (TEMPLATE) ===")
            print(content)
            print("===================================")
            
            # 2. Save to file
            with open("ticket_output.txt", "w", encoding="utf-8") as f:
                f.write(content)
                
            return {
                "status": "success", 
                "mode": "virtual", 
                "message": "Ticket generado en ticket_output.txt",
                "commands_count": len(commands)
            }
        
        elif PRINTER_MODE == "WINDOWS":
            try:
                print(f"🖨️ WINDOWS MODE: Sending to printer '{PRINTER_NAME}'")
                from escpos.printer import Win32Raw
                
                # Check if printer exists
                available_printers = get_windows_printers()
                print(f"📋 Available Printers: {available_printers}")
                
                if PRINTER_NAME not in available_printers:
                    print(f"❌ ERROR: Printer '{PRINTER_NAME}' not found!")
                    raise HTTPException(status_code=500, detail=f"Printer '{PRINTER_NAME}' not found. Available: {available_printers}")
                
                print("🔌 Initializing Win32Raw...")
                p = Win32Raw(printer_name=PRINTER_NAME)
                
                print("📝 Sending commands...")
                for cmd in commands:
                    if cmd['type'] == 'cut':
                        p.cut()
                    elif cmd['type'] == 'text':
                        # Set alignment
                        align_map = {'left': 'left', 'center': 'center', 'right': 'right'}
                        p.set(align=align_map[cmd['align']], bold=cmd['bold'])
                        
                        # FORCE ENCODING: Win32Raw often needs encoded bytes, not strings
                        # We try to send raw bytes encoded in CP850 (standard for thermal printers)
                        text_to_print = cmd['content'] + '\n'
                        try:
                            # Try printing as string first (python-escpos handles magic)
                            p.text(text_to_print)
                        except Exception as encoding_err:
                            print(f"⚠️ Text encoding error: {encoding_err}. Retrying as raw bytes...")
                            # Fallback: Send raw bytes directly if library fails
                            p._raw(text_to_print.encode('cp850', errors='replace'))

                # End job
                print("✅ Printing complete. Closing job.")
                p.close()
                return {"status": "success", "mode": "windows", "printer": PRINTER_NAME}
                
            except ImportError:
                 print("❌ ERROR: pywin32 not installed")
                 raise HTTPException(status_code=500, detail="pywin32 not installed")
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"❌ WINDOWS PRINT ERROR: {e}")
                print(error_trace)
                raise HTTPException(status_code=500, detail=f"Windows print error: {str(e)}")

        elif PRINTER_MODE == "USB":
            # TODO: Implement using python-escpos
            try:
                from escpos.printer import Usb
                
                # Find printer (adjust vendor_id and product_id)
                p = Usb(0x04b8, 0x0e15)  # Example: Epson TM-T20
                
                for cmd in commands:
                    if cmd['type'] == 'cut':
                        p.cut()
                    elif cmd['type'] == 'text':
                        # Set alignment
                        align_map = {'left': 'left', 'center': 'center', 'right': 'right'}
                        p.set(align=align_map[cmd['align']], bold=cmd['bold'])
                        p.text(cmd['content'] + '\n')
                
                return {"status": "success", "mode": "usb", "message": "Ticket printed"}
            except ImportError:
                raise HTTPException(
                    status_code=500, 
                    detail="python-escpos not installed. Run: pip install python-escpos"
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"USB print error: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"❌ ERROR: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))

# Legacy endpoint (keep for backward compatibility)
class TicketItem(BaseModel):
    name: str
    quantity: float
    price: float
    total: float
    unit: str

class TicketData(BaseModel):
    header: Optional[List[str]] = []
    items: List[TicketItem]
    totals: dict
    footer: Optional[List[str]] = []

@app.post("/print-ticket")
async def print_ticket_legacy(data: TicketData):
    """Legacy endpoint - kept for backward compatibility"""
    try:
        # Convert to template format
        template_str = """<center><bold>{{ header[0] }}</bold></center>
{% for line in header[1:] %}
<center>{{ line }}</center>
{% endfor %}
================================
{% for item in items %}
{{ item.name }}
  {{ item.quantity }} {{ item.unit }} x ${{ item.price }} = ${{ item.total }}
{% endfor %}
================================
{% for key, value in totals.items() %}
<right>{{ key }}: ${{ value }}</right>
{% endfor %}
================================
{% for line in footer %}
<center>{{ line }}</center>
{% endfor %}
<cut>"""
        
        context = {
            'header': data.header,
            'items': [item.dict() for item in data.items],
            'totals': data.totals,
            'footer': data.footer
        }
        
        commands = print_from_template(template_str, context)
        content = format_virtual_ticket(commands)
        
        print("=== NUEVA IMPRESION (LEGACY) ===")
        print(content)
        print("=================================")
        
        with open("ticket_output.txt", "w", encoding="utf-8") as f:
            f.write(content)
            
        return {
            "status": "success", 
            "mode": "virtual", 
            "message": "Ticket generado en ticket_output.txt"
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {
        "service": "Hardware Bridge",
        "version": "2.1",
        "mode": PRINTER_MODE,
        "target_printer": PRINTER_NAME if PRINTER_MODE == "WINDOWS" else None,
        "features": ["jinja2_templates", "custom_tags", "windows_spooler"],
        "available_printers": get_windows_printers()
    }

@app.get("/printers")
def list_printers():
    return {"printers": get_windows_printers()}

if __name__ == "__main__":
    import uvicorn
    # Removed emojis to prevent cp1252 encoding errors on some Windows systems
    print("Iniciando Hardware Bridge v2.0 en Puerto 5001...")
    print(f"Modo: {PRINTER_MODE}")
    print("Jinja2 Template System Enabled")
    uvicorn.run(app, host="0.0.0.0", port=5001)
