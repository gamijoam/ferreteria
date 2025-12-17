"""
Script de Diagnóstico: Verificar Deduplicación de Monedas
Ejecutar: python debug_currency_dedup.py
"""

import sys
import os
sys.path.append(os.getcwd())

from backend_api.database.db import SessionLocal
from backend_api.models import models

def diagnose():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("🔍 DIAGNÓSTICO: DEDUPLICACIÓN DE MONEDAS")
        print("=" * 60)
        
        # 1. Verificar tasas en la base de datos
        print("\n1️⃣  TASAS EN LA BASE DE DATOS:")
        print("-" * 60)
        rates = db.query(models.ExchangeRate).filter(
            models.ExchangeRate.is_active == True
        ).order_by(
            models.ExchangeRate.currency_code,
            models.ExchangeRate.is_default.desc()
        ).all()
        
        if not rates:
            print("❌ No hay tasas activas en la base de datos")
            print("\n💡 Solución: Ejecuta el endpoint /config/debug/seed")
            return
        
        print(f"Total de tasas activas: {len(rates)}\n")
        
        for rate in rates:
            default_marker = "⭐ DEFAULT" if rate.is_default else ""
            print(f"  • {rate.name:15} | Code: {rate.currency_code:4} | Symbol: {rate.currency_symbol:4} | Rate: {rate.rate:8.2f} {default_marker}")
        
        # 2. Agrupar por currency_code (simular deduplicación)
        print("\n2️⃣  DEDUPLICACIÓN POR currency_code:")
        print("-" * 60)
        
        unique_currencies = {}
        for rate in rates:
            code = rate.currency_code
            # Priorizar la tasa default
            if code not in unique_currencies or rate.is_default:
                unique_currencies[code] = {
                    'name': rate.name,
                    'code': code,
                    'symbol': rate.currency_symbol,
                    'rate': rate.rate,
                    'is_default': rate.is_default
                }
        
        print(f"Monedas únicas (después de deduplicar): {len(unique_currencies)}\n")
        
        for code, curr in unique_currencies.items():
            print(f"  • {curr['name']:15} | Code: {curr['code']:4} | Symbol: {curr['symbol']:4} | Rate: {curr['rate']:8.2f}")
        
        # 3. Verificar problema específico: VES duplicado
        print("\n3️⃣  VERIFICACIÓN ESPECÍFICA: BOLÍVARES (VES):")
        print("-" * 60)
        
        ves_rates = [r for r in rates if r.currency_code == 'VES']
        
        if len(ves_rates) > 1:
            print(f"✅ Encontradas {len(ves_rates)} tasas para VES (correcto para multi-tasa)")
            print("\nDetalles:")
            for rate in ves_rates:
                print(f"  • {rate.name:15} | Symbol: '{rate.currency_symbol}' | Default: {rate.is_default}")
            
            # Verificar que todas tengan el mismo símbolo
            symbols = set(r.currency_symbol for r in ves_rates)
            if len(symbols) == 1:
                print(f"\n✅ CORRECTO: Todas las tasas VES usan el mismo símbolo: '{symbols.pop()}'")
                print("   El frontend debe mostrar solo 1 input para Bolívares")
            else:
                print(f"\n❌ ERROR: Las tasas VES usan símbolos diferentes: {symbols}")
                print("   Esto causará múltiples inputs en el frontend")
                print("\n💡 Solución: Actualiza todas las tasas VES para usar 'Bs':")
                for rate in ves_rates:
                    if rate.currency_symbol != 'Bs':
                        print(f"   UPDATE exchange_rates SET currency_symbol = 'Bs' WHERE id = {rate.id};")
        elif len(ves_rates) == 1:
            print(f"⚠️  Solo hay 1 tasa para VES (funciona, pero no es multi-tasa)")
        else:
            print("❌ No hay tasas para VES")
        
        # 4. Resultado esperado en el frontend
        print("\n4️⃣  RESULTADO ESPERADO EN CASH OPENING MODAL:")
        print("-" * 60)
        
        # Filtrar no-anchor (USD es anchor)
        non_anchor = [c for c in unique_currencies.values() if c['code'] != 'USD']
        
        print("Inputs que deben aparecer:")
        print("  1. USD (Dólar) - Moneda base")
        for i, curr in enumerate(non_anchor, start=2):
            print(f"  {i}. {curr['code']} ({curr['name']})")
        
        total_inputs = 1 + len(non_anchor)
        print(f"\nTotal de inputs esperados: {total_inputs}")
        
        if total_inputs == 3:
            print("✅ CORRECTO: 3 inputs (USD, COP, BS)")
        elif total_inputs == 4:
            print("❌ ERROR: 4 inputs detectados")
            print("   Revisa que no haya monedas duplicadas con símbolos diferentes")
        
        print("\n" + "=" * 60)
        print("✅ DIAGNÓSTICO COMPLETADO")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    diagnose()
