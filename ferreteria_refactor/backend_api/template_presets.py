"""
Template Presets for Ticket Printing
Provides 5 predefined templates for easy selection
"""

# Using sale['items'] notation to avoid Jinja2 dict.items() conflict

TEMPLATE_PRESETS = {
    "classic": {
        "name": "Clásico",
        "description": "Diseño tradicional simple y limpio",
        "preview_image": "classic_preview.png",
        "template": """<center><bold>{{ business.name }}</bold></center>
<center>{{ business.address }}</center>
<center>RIF: {{ business.document_id }}</center>
<center>Tel: {{ business.phone }}</center>
<center>================================</center>
Fecha: {{ sale.date }}
Factura: #{{ sale.id }}
{% if sale.customer %}
Cliente: {{ sale.customer.name }}
{% endif %}
{% if sale.is_credit %}
<center><bold>*** A CREDITO ***</bold></center>
<center>Saldo: ${{ sale.balance }}</center>
{% endif %}
<center>================================</center>
{% for item in sale['items'] %}
{{ item.product.name }}
  {{ item.quantity }} x ${{ item.unit_price }} = ${{ item.subtotal }}
{% endfor %}
<center>================================</center>
<right><bold>TOTAL: ${{ sale.total }}</bold></right>
<center>================================</center>
<center>Gracias por su compra</center>
<center>{{ business.name }}</center>
<cut>"""
    },
    
    "modern": {
        "name": "Moderno",
        "description": "Diseño minimalista y elegante",
        "preview_image": "modern_preview.png",
        "template": """<center><bold>{{ business.name }}</bold></center>
<center>{{ business.address }} | {{ business.phone }}</center>
<center>--------------------------------</center>
#{{ sale.id }} | {{ sale.date }}{% if sale.customer %} | {{ sale.customer.name }}{% endif %}
<center>--------------------------------</center>
{% for item in sale['items'] %}
{{ item.product.name }}
<right>{{ item.quantity }} x ${{ item.unit_price }} = ${{ item.subtotal }}</right>
{% endfor %}
<center>--------------------------------</center>
<right><bold>TOTAL: ${{ sale.total }}</bold></right>
{% if sale.is_credit %}
<right>Saldo: ${{ sale.balance }}</right>
{% endif %}
<center>--------------------------------</center>
<center>Gracias por preferirnos</center>
<cut>"""
    },
    
    "detailed": {
        "name": "Detallado",
        "description": "Con toda la información completa",
        "preview_image": "detailed_preview.png",
        "template": """<center>================================</center>
<center><bold>{{ business.name }}</bold></center>
<center>================================</center>
{{ business.address }}
RIF: {{ business.document_id }}
Tel: {{ business.phone }}
{% if business.email %}Email: {{ business.email }}{% endif %}
<center>================================</center>
<bold>FACTURA: #{{ sale.id }}</bold>
FECHA: {{ sale.date }}
{% if sale.customer %}
CLIENTE: {{ sale.customer.name }}
{% if sale.customer.id_number %}CI/RIF: {{ sale.customer.id_number }}{% endif %}
{% endif %}
<center>================================</center>
CANT  DESCRIPCION           TOTAL
<center>--------------------------------</center>
{% for item in sale['items'] %}
{{ item.quantity }}     {{ item.product.name }}
      @${{ item.unit_price }}/u      ${{ item.subtotal }}
{% endfor %}
<center>================================</center>
<right>SUBTOTAL: ${{ sale.total }}</right>
{% if sale.is_credit %}
<right><bold>CREDITO</bold></right>
<right>Saldo: ${{ sale.balance }}</right>
{% endif %}
<center>================================</center>
<right><bold>TOTAL: ${{ sale.total }}</bold></right>
<center>================================</center>
<center>Gracias por su compra</center>
<center>{{ business.name }}</center>
<cut>"""
    },
    
    "minimal": {
        "name": "Minimalista",
        "description": "Solo lo esencial, ultra compacto",
        "preview_image": "minimal_preview.png",
        "template": """<center><bold>{{ business.name }}</bold></center>
#{{ sale.id }} | {{ sale.date }}
<center>--------------------------------</center>
{% for item in sale['items'] %}
{{ item.quantity }}x {{ item.product.name }}
<right>${{ item.subtotal }}</right>
{% endfor %}
<center>--------------------------------</center>
<right><bold>TOTAL: ${{ sale.total }}</bold></right>
{% if sale.is_credit %}
<right>Saldo: ${{ sale.balance }}</right>
{% endif %}
<center>Gracias</center>
<cut>"""
    },
    
    "receipt": {
        "name": "Comprobante",
        "description": "Formato de comprobante oficial",
        "preview_image": "receipt_preview.png",
        "template": """<center><bold>COMPROBANTE DE VENTA</bold></center>
<center>================================</center>
Negocio: {{ business.name }}
RIF: {{ business.document_id }}
Dirección: {{ business.address }}
Tel: {{ business.phone }}
<center>================================</center>
Fecha: {{ sale.date }}
Comprobante Nro: {{ sale.id }}
<center>================================</center>
{% if sale.customer %}
Cliente: {{ sale.customer.name }}
{% if sale.customer.id_number %}CI/RIF: {{ sale.customer.id_number }}{% endif %}
<center>================================</center>
{% endif %}
<bold>DETALLE DE LA VENTA:</bold>
{% for item in sale['items'] %}
{{ item.quantity }} {{ item.product.name }}
  @${{ item.unit_price }}
<right>${{ item.subtotal }}</right>
{% endfor %}
<center>================================</center>
<right><bold>TOTAL: ${{ sale.total }}</bold></right>
{% if sale.is_credit %}
<center>--------------------------------</center>
<center><bold>VENTA A CREDITO</bold></center>
<right>Saldo Pendiente: ${{ sale.balance }}</right>
{% endif %}
<center>================================</center>
<center>Firma del Cliente</center>
_______________________________
<center>================================</center>
<center>Gracias por su compra</center>
<cut>"""
    }
}

def get_preset_by_id(preset_id: str):
    """Get a template preset by ID"""
    return TEMPLATE_PRESETS.get(preset_id)

def get_all_presets():
    """Get all available template presets"""
    return {
        preset_id: {
            "id": preset_id,
            "name": preset["name"],
            "description": preset["description"],
            "preview_image": preset.get("preview_image")
        }
        for preset_id, preset in TEMPLATE_PRESETS.items()
    }
