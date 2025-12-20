-- Script SQL para actualizar la plantilla de ticket directamente en la base de datos
-- Ejecutar esto en pgAdmin o psql

UPDATE business_config 
SET value = '<center><bold>{{ business.name }}</bold></center>
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
{% for item in sale.items %}
{{ item.product.name }}
  {{ item.quantity }} x ${{ item.unit_price }} = ${{ item.subtotal }}
{% endfor %}
================================
<right><bold>TOTAL: ${{ sale.total }}</bold></right>
================================
<center>Gracias por su compra</center>
<center>{{ business.name }}</center>
<cut>'
WHERE key = 'ticket_template';
