from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
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

def format_virtual_ticket(data: TicketData):
    """
    Formatea el ticket como una cadena de texto simulando un ancho de 48 carácteres.
    """
    width = 48
    separator = "-" * width
    lines = []
    
    # Header
    lines.append(separator)
    lines.append(f"{'TICKET DE VENTA':^{width}}")
    lines.append(separator)
    for line in data.header:
        lines.append(f"{line:^{width}}")
    lines.append(separator + "\n")
    
    # Items
    lines.append(f"{'CANT':<6} {'DESCRIPCION':<25} {'TOTAL':>15}")
    lines.append(separator)
    
    for item in data.items:
        # Line 1: Name
        lines.append(f"{item.name:<width}")
        # Line 2: Details
        q_str = f"{item.quantity} {item.unit}"
        lines.append(f"{q_str:<10} x {item.price:<10.2f} {item.total:>24.2f}")
    
    lines.append(separator + "\n")
    
    # Totals
    for key, value in data.totals.items():
        if isinstance(value, float) or isinstance(value, int):
             lines.append(f"{key:<30} {value:>16.2f}")
        else:
             lines.append(f"{key:<30} {value:>16}")
             
    lines.append(separator + "\n")
    
    # Footer
    for line in data.footer:
        lines.append(f"{line:^{width}}")
        
    lines.append("\n\n")
    
    return "\n".join(lines)

@app.post("/print-ticket")
async def print_ticket(data: TicketData):
    try:
        if PRINTER_MODE == "VIRTUAL":
            content = format_virtual_ticket(data)
            
            # 1. Imprimir en consola del servidor
            print("=== NUEVA IMPRESION RECIBIDA ===")
            print(content)
            print("================================")
            
            # 2. Guardar en archivo
            with open("ticket_output.txt", "w", encoding="utf-8") as f:
                f.write(content)
                
            return {
                "status": "success", 
                "mode": "virtual", 
                "message": "Ticket generado en ticket_output.txt"
            }
            
        elif PRINTER_MODE == "USB":
            # TODO: Implementar usando python-escpos o win32print
            return {"status": "error", "message": "Modo USB no implementado aun"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("Iniciando Hardware Bridge en Puerto 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
