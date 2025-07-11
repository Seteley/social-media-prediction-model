#!/usr/bin/env python3
"""
Ejemplo simple: Predicción usando fecha
"""

from datetime import datetime, timedelta

def mostrar_ejemplos_fecha():
    print("🎯 PREDICCIÓN DE SEGUIDORES USANDO FECHA")
    print("=" * 60)
    
    print("✨ MÉTODO SIMPLE: Solo proporciona la fecha")
    print("   La API calcula automáticamente:")
    print("   • Día de la semana (0=Lunes, 6=Domingo)")
    print("   • Mes (1-12)")
    print("   • Hora = 23 (fin del día)")
    
    hoy = datetime.now()
    
    ejemplos = [
        ("Hoy", hoy),
        ("Mañana", hoy + timedelta(days=1)),
        ("Fin de semana", hoy + timedelta(days=(5-hoy.weekday()))),  # Próximo sábado
        ("Próximo mes", hoy + timedelta(days=30)),
        ("Navidad", datetime(2025, 12, 25)),
    ]
    
    print(f"\n📅 EJEMPLOS DE USO:")
    
    for descripcion, fecha_obj in ejemplos:
        fecha_str = fecha_obj.strftime("%Y-%m-%d")
        dia_nombre = fecha_obj.strftime("%A")
        mes_nombre = fecha_obj.strftime("%B")
        
        print(f"\n🔸 {descripcion}:")
        print(f"   📡 URL: http://localhost:8000/regression/predict/BanBif?fecha={fecha_str}")
        print(f"   📅 Significa: {dia_nombre} {fecha_obj.day} de {mes_nombre}, {fecha_obj.year} a las 23:00")
        
        # Calcular valores que usará el modelo
        dia_semana = fecha_obj.weekday()
        mes = fecha_obj.month
        print(f"   🧮 Modelo recibe: dia_semana={dia_semana}, mes={mes}, hora=23")
    
    print(f"\n💡 VENTAJAS DEL NUEVO MÉTODO:")
    print(f"   ✅ Más fácil de usar: solo una fecha")
    print(f"   ✅ Más intuitivo: fecha natural en lugar de números")
    print(f"   ✅ Menos errores: no hay que calcular día de la semana")
    print(f"   ✅ Consistente: siempre usa fin del día (23:00)")
    
    print(f"\n🔧 ALTERNATIVA (método anterior):")
    print(f"   Si prefieres usar parámetros individuales:")
    print(f"   http://localhost:8000/regression/predict/BanBif?dia_semana=4&hora=23&mes=7")

if __name__ == "__main__":
    mostrar_ejemplos_fecha()
