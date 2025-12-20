"""
Script para corregir la plantilla de ticket - VERSIÓN CORREGIDA
Usa sale['items'] en lugar de sale.items para evitar conflicto con dict.items()
"""

from ferreteria_refactor.backend_api.database.db import SessionLocal
from ferreteria_refactor.backend_api.models.models import BusinessConfig

# Plantilla correcta usando sale['items'] en lugar de sale.items
CORRECT_TEMPLATE = """<center><bold>{{ business.name }}</bold></center>
<center>{{ business.address }}</center>
<center>RIF: {{ business.document_id }}</center>
<center>Tel: {{ business.phone }}</center>
================================
Fecha: {{ sale.date }}
Factura: #{{ sale.id }}
{% if sale.customer %}
Cliente: {{ sale.customer.name }}
{% endif %}
{% if sale.is_credit %}
<center><bold>*** A CREDITO ***</bold></center>
Saldo Pendiente: ${{ sale.balance }}
{% endif %}
================================
<left>PRODUCTO</left><right>TOTAL</right>
--------------------------------
{% for item in sale['items'] %}
{{ item.product.name }}
  {{ item.quantity }} x ${{ item.unit_price }} = ${{ item.subtotal }}
{% endfor %}
================================
<right><bold>TOTAL: ${{ sale.total }}</bold></right>
================================
<center>Gracias por su compra</center>
<center>{{ business.name }}</center>
<cut>"""

def fix_template():
    db = SessionLocal()
    try:
        config = db.query(BusinessConfig).filter_by(key='ticket_template').first()
        
        if not config:
            print("⚠️  No existe ticket_template, creando...")
            config = BusinessConfig(key='ticket_template', value=CORRECT_TEMPLATE)
            db.add(config)
        else:
            print("📝 Actualizando ticket_template con sale['items']...")
            config.value = CORRECT_TEMPLATE
        
        db.commit()
        print(f"✅ Plantilla actualizada correctamente!")
        print(f"   Cambio clave: sale.items → sale['items']")
        print("\n🎉 Ahora prueba 'Imprimir Prueba' desde el frontend")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Corrigiendo plantilla de ticket (VERSIÓN 2)...")
    fix_template()
