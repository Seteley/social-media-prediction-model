#!/usr/bin/env python3
"""
Script para mostrar las features requeridas para predicción de seguidores
"""

import json
from pathlib import Path
import joblib

def show_features_for_account(username):
    """Muestra las features requeridas para una cuenta específica."""
    
    # Verificar si existe el modelo
    model_path = Path(f"models/{username}/regresion.pkl")
    metrics_path = Path(f"metricas/{username}.json")
    
    print(f"🔍 Analizando features para: {username}")
    print("=" * 60)
    
    if model_path.exists():
        try:
            # Cargar modelo
            model_data = joblib.load(model_path)
            features_from_model = model_data['feature_names']
            target_var = model_data['target_variable']
            
            print(f"📊 Modelo encontrado: {model_path}")
            print(f"🎯 Variable objetivo: {target_var}")
            print(f"📈 Features requeridas desde el modelo ({len(features_from_model)}):")
            for i, feature in enumerate(features_from_model, 1):
                print(f"   {i}. {feature}")
            
        except Exception as e:
            print(f"❌ Error cargando modelo: {e}")
    
    if metrics_path.exists():
        try:
            # Cargar métricas
            with open(metrics_path, 'r', encoding='utf-8') as f:
                metrics = json.load(f)
            
            features_from_metrics = metrics.get('features_used', [])
            
            print(f"\n📋 Métricas encontradas: {metrics_path}")
            print(f"📈 Features desde métricas ({len(features_from_metrics)}):")
            for i, feature in enumerate(features_from_metrics, 1):
                print(f"   {i}. {feature}")
                
        except Exception as e:
            print(f"❌ Error cargando métricas: {e}")

def explain_features():
    """Explica qué significan las features temporales."""
    
    print(f"\n📚 EXPLICACIÓN DE FEATURES")
    print("=" * 60)
    
    feature_explanations = {
        'dia_semana': {
            'descripcion': 'Día de la semana (0=Lunes, 6=Domingo)',
            'tipo': 'Temporal - Categórica',
            'rango': '0-6',
            'ejemplo': 'Lunes=0, Martes=1, ..., Domingo=6'
        },
        'hora': {
            'descripcion': 'Hora del día en formato 24h',
            'tipo': 'Temporal - Numérica',
            'rango': '0-23',
            'ejemplo': '14 para las 2:00 PM'
        },
        'mes': {
            'descripcion': 'Mes del año',
            'tipo': 'Temporal - Categórica',
            'rango': '1-12',
            'ejemplo': 'Enero=1, Febrero=2, ..., Diciembre=12'
        },
        'engagement_rate': {
            'descripcion': 'Tasa de engagement (interacciones/vistas)',
            'tipo': 'Métrica - Numérica',
            'rango': '0.0-1.0',
            'ejemplo': '0.05 = 5% de engagement'
        },
        'total_tweets': {
            'descripcion': 'Número total de tweets de la cuenta',
            'tipo': 'Métrica - Numérica',
            'rango': '0+',
            'ejemplo': '1500 tweets totales'
        },
        'actividad_publicacion': {
            'descripcion': 'Nivel de actividad de publicación',
            'tipo': 'Métrica - Numérica',
            'rango': '0.0+',
            'ejemplo': '5.2 publicaciones promedio'
        }
    }
    
    for feature, info in feature_explanations.items():
        print(f"\n🔹 {feature}")
        print(f"   📝 {info['descripcion']}")
        print(f"   📊 Tipo: {info['tipo']}")
        print(f"   📏 Rango: {info['rango']}")
        print(f"   💡 Ejemplo: {info['ejemplo']}")

def show_prediction_examples():
    """Muestra ejemplos de cómo hacer predicciones."""
    
    print(f"\n🎯 EJEMPLOS DE PREDICCIÓN")
    print("=" * 60)
    
    print("📡 Método RECOMENDADO - Usando fecha:")
    print("   http://localhost:8000/regression/predict/BanBif?fecha=2025-07-11")
    print("   📅 Fecha: 2025-07-11 (se asume hora 23:00)")
    print("   🔧 Se calcula automáticamente:")
    print("      • dia_semana = 4 (Viernes)")
    print("      • mes = 7 (Julio)")
    print("      • hora = 23 (fin del día)")
    
    print(f"\n📋 Ejemplos de fechas comunes:")
    from datetime import datetime, timedelta
    hoy = datetime.now()
    
    ejemplos_fechas = [
        (hoy, "Hoy"),
        (hoy + timedelta(days=1), "Mañana"),
        (hoy + timedelta(days=7), "Próxima semana"),
        (hoy + timedelta(days=30), "En un mes"),
        (datetime(2025, 12, 25), "Navidad 2025"),
        (datetime(2025, 1, 1), "Año Nuevo 2025")
    ]
    
    for fecha_obj, descripcion in ejemplos_fechas:
        fecha_str = fecha_obj.strftime("%Y-%m-%d")
        dia_sem = fecha_obj.weekday()  # 0=Lunes
        mes_num = fecha_obj.month
        dia_nombre = fecha_obj.strftime("%A")
        mes_nombre = fecha_obj.strftime("%B")
        
        print(f"\n   📅 {descripcion}: fecha={fecha_str}")
        print(f"      URL: /regression/predict/BanBif?fecha={fecha_str}")
        print(f"      Equivale a: dia_semana={dia_sem} ({dia_nombre}), mes={mes_num} ({mes_nombre}), hora=23")
    
    print(f"\n📡 Método alternativo - Parámetros individuales:")
    example_url = "http://localhost:8000/regression/predict/BanBif?"
    params = [
        "dia_semana=1",      # Martes
        "hora=23",           # Fin del día
        "mes=7"              # Julio
    ]
    full_url = example_url + "&".join(params)
    print(f"   {full_url}")
    
    print(f"\n📋 Significado de los parámetros:")
    print(f"   • dia_semana=1 → Martes")
    print(f"   • hora=23 → 11:00 PM (fin del día)")
    print(f"   • mes=7 → Julio")
    
    print(f"\n🔄 Ejemplos de valores comunes:")
    
    dias = ["Lunes=0", "Martes=1", "Miércoles=2", "Jueves=3", "Viernes=4", "Sábado=5", "Domingo=6"]
    print(f"\n   📅 Días de la semana:")
    for dia in dias:
        print(f"      • {dia}")
    
    print(f"\n   🕐 Horas importantes:")
    horas = ["Mañana temprano: 6-9", "Mañana: 9-12", "Tarde: 12-18", "Noche: 18-23"]
    for hora in horas:
        print(f"      • {hora}")
    
    print(f"\n   📆 Meses:")
    meses = ["Enero=1", "Febrero=2", "Marzo=3", "Abril=4", "Mayo=5", "Junio=6",
             "Julio=7", "Agosto=8", "Septiembre=9", "Octubre=10", "Noviembre=11", "Diciembre=12"]
    for i in range(0, len(meses), 4):
        print(f"      • {', '.join(meses[i:i+4])}")

def main():
    """Función principal."""
    
    print("🔍 ANÁLISIS DE FEATURES PARA PREDICCIÓN DE SEGUIDORES")
    print("=" * 70)
    
    # Mostrar features para cuentas disponibles
    accounts = ["BanBif", "Interbank", "BCPComunica"]
    
    for account in accounts:
        model_path = Path(f"models/{account}/regresion.pkl")
        if model_path.exists():
            show_features_for_account(account)
            break
    
    # Explicar features
    explain_features()
    
    # Mostrar ejemplos
    show_prediction_examples()
    
    print(f"\n✅ Análisis completado!")
    print(f"💡 Para hacer predicciones, usa la API: python run_api.py")

if __name__ == "__main__":
    main()
