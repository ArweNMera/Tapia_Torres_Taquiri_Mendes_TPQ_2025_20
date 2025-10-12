"""
Script para generar datos antropométricos sintéticos balanceados.

Genera datos realistas para todas las clasificaciones:
- NORMAL (BAZ entre -1 y +1)
- RIESGO (BAZ entre -2 y -1, o +1 y +2)
- MODERADO (BAZ entre -3 y -2, o +2 y +3)
- SEVERO (BAZ < -3 o > +3)

Usa las tablas OMS para calcular peso/talla realistas.
"""
