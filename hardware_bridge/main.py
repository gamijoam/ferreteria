from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Template
import re
import datetime

app = FastAPI()

# Configura CORS para permitir peticiones desde el frontend web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En produccion, limita esto al dominio de tu app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PRINTER_MODE = "VIRTUAL"  # "VIRTUAL" (archivo) o "USB" (impresora real)

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
        "version": "2.0",
        "mode": PRINTER_MODE,
        "features": ["jinja2_templates", "custom_tags", "virtual_printer"]
    }

if __name__ == "__main__":
    import uvicorn
    print("🖨️  Iniciando Hardware Bridge v2.0 en Puerto 5001...")
    print(f"📋 Modo: {PRINTER_MODE}")
    print("✅ Jinja2 Template System Enabled")
    uvicorn.run(app, host="0.0.0.0", port=5001)
