from typing import List, Dict

def get_classic_template() -> str:
    return """=== TICKET DE VENTA ===
{{ business.name }}
{{ business.address }}
RIF: {{ business.document_id }}
Tel: {{ business.phone }}
================================
Fecha: {{ sale.date }}
Factura: #{{ sale.id }}
Cliente: {{ sale.customer.name if sale.customer else "Consumidor Final" }}
{% if sale.is_credit %}
CONDICION: A CREDITO
Vence: {{ sale.due_date }}
{% endif %}
================================
CANT   PRODUCTO         TOTAL
--------------------------------
{% for item in sale.items %}
{{ "%.1f"|format(item.quantity) }} x {{ item.product.name }}
       {{ "$%.2f"|format(item.unit_price) }} = {{ "$%.2f"|format(item.subtotal) }}
{% endfor %}
================================
SUBTOTAL:       {{ "$%.2f"|format(sale.total) }}
{% if sale.discount > 0 %}
DESCUENTO:     -{{ "$%.2f"|format(sale.discount) }}
{% endif %}
TOTAL A PAGAR:  {{ "$%.2f"|format(sale.total) }}
================================
      Gracias por su compra
"""

def get_modern_template() -> str:
    return """
           {{ business.name }}
   {{ business.address }}
----------------------------------
       TICKET DE VENTA #{{ sale.id }}
----------------------------------
{{ sale.date }}

CLIENTE: {{ sale.customer.name if sale.customer else "CLIENTE GENERAL" }}
DOC: {{ sale.customer.id_number if sale.customer else "" }}

ITEMS
----------------------------------
{% for item in sale.items %}
* {{ item.product.name }}
  {{ item.quantity }} x {{ "$%.2f"|format(item.unit_price) }} ...... {{ "$%.2f"|format(item.subtotal) }}
{% endfor %}
----------------------------------
TOTAL ......... {{ "$%.2f"|format(sale.total) }}
----------------------------------
{% if sale.is_credit %}
*** CUENTA POR COBRAR ***
Saldo Pendiente: {{ "$%.2f"|format(sale.balance) }}
{% else %}
*** PAGADO ***
{% endif %}

      ¡VUELVA PRONTO!
"""

def get_detailed_template() -> str:
    return """================================
{{ business.name }}
{{ business.document_id }}
--------------------------------
Venta: #{{ sale.id }}
Fecha: {{ sale.date }}
--------------------------------
{% for item in sale.items %}
[{{ item.product.sku }}] {{ item.product.name }}
Cant: {{ item.quantity }}   Precio: {{ "$%.2f"|format(item.unit_price) }}
Subtotal: {{ "$%.2f"|format(item.subtotal) }}
- - - - - - - - - - - - - - - -
{% endfor %}
================================
TOTAL: {{ "$%.2f"|format(sale.total) }}
================================
"""

def get_minimal_template() -> str:
    return """{{ business.name }}
Ticket #{{ sale.id }}
{{ sale.date }}
--------------------------------
{% for item in sale.items %}
{{ item.quantity }} {{ item.product.name[:20] }} {{ "$%.2f"|format(item.subtotal) }}
{% endfor %}
--------------------------------
TOTAL: {{ "$%.2f"|format(sale.total) }}
"""

def get_all_presets() -> List[Dict[str, str]]:
    return [
        {
            "id": "classic",
            "name": "Clásico",
            "description": "Formato estándar balanceado",
            "template": get_classic_template()
        },
        {
            "id": "modern",
            "name": "Moderno", 
            "description": "Diseño limpio y centrado",
            "template": get_modern_template()
        },
        {
            "id": "detailed",
            "name": "Detallado",
            "description": "Incluye códigos y detalles línea por línea",
            "template": get_detailed_template()
        },
        {
            "id": "minimal",
            "name": "Minimalista",
            "description": "Ahorra papel, solo información esencial",
            "template": get_minimal_template()
        }
    ]

def get_preset_by_id(preset_id: str) -> Dict[str, str]:
    presets = get_all_presets()
    for p in presets:
        if p["id"] == preset_id:
            return p
    return None
