"""
Plantilla mejorada y simplificada para tickets
Usa una sola columna para evitar problemas de alineación
"""

from ferreteria_refactor.backend_api.database.db import SessionLocal
from ferreteria_refactor.backend_api.models.models import BusinessConfig

# Plantilla simplificada y funcional
SIMPLE_TEMPLATE = """<center><bold>{{ business.name }}</bold></center>
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
<center>Saldo Pendiente: ${{ sale.balance }}</center>
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

def update_template():
    db = SessionLocal()
    try:
        config = db.query(BusinessConfig).filter_by(key='ticket_template').first()
        
        if config:
            print("📝 Actualizando a plantilla simplificada...")
            config.value = SIMPLE_TEMPLATE
            db.commit()
            print("✅ Plantilla actualizada!")
            print("\n💡 Cambios:")
            print("   - Eliminada tabla de dos columnas")
            print("   - Formato más limpio y legible")
            print("   - Todos los tags funcionan correctamente")
        else:
            print("❌ No se encontró ticket_template")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Actualizando a plantilla simplificada...")
    update_template()
