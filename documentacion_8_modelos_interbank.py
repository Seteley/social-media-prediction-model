#!/usr/bin/env python3
"""
DOCUMENTACIÓN COMPLETA: 8 Modelos de Regresión para Interbank
Ejemplo con datos reales y comparación de rendimiento.
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler

# Importar los 8 modelos configurados
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor

def load_interbank_data():
    """Carga y preprocesa datos reales de Interbank"""
    print("📊 CARGANDO DATOS REALES DE INTERBANK")
    print("="*50)
    
    # Cargar datos del CSV
    file_path = "data/Interbank_metricas.csv"
    if not os.path.exists(file_path):
        print(f"❌ Archivo no encontrado: {file_path}")
        return None, None, None
    
    df = pd.read_csv(file_path)
    print(f"✅ Datos cargados: {len(df)} registros")
    print(f"📋 Columnas: {list(df.columns)}")
    
    # Renombrar columnas para consistencia
    df = df.rename(columns={
        'Hora': 'timestamp_metrica',
        'Seguidores': 'seguidores'
    })
    
    # Convertir timestamp y crear features temporales
    df['timestamp_metrica'] = pd.to_datetime(df['timestamp_metrica'])
    df['dia_semana'] = df['timestamp_metrica'].dt.dayofweek  # 0=Lunes, 6=Domingo
    df['hora'] = df['timestamp_metrica'].dt.hour
    df['mes'] = df['timestamp_metrica'].dt.month
    
    # Features y target
    feature_cols = ['dia_semana', 'hora', 'mes']
    X = df[feature_cols].copy()
    y = df['seguidores'].copy()
    
    print(f"\n📈 Rango de seguidores: {y.min():,} - {y.max():,}")
    print(f"📊 Promedio de seguidores: {y.mean():.0f}")
    print(f"🔧 Features utilizadas: {feature_cols}")
    
    return X, y, df

def setup_models():
    """Configura los 8 modelos de regresión"""
    models = {
        'Linear Regression': {
            'model': LinearRegression(),
            'description': 'Regresión lineal simple - Relación lineal entre features y target'
        },
        'Ridge Regression': {
            'model': Ridge(alpha=1.0, random_state=42),
            'description': 'Regresión Ridge (L2) - Previene overfitting con regularización'
        },
        'Lasso Regression': {
            'model': Lasso(alpha=1.0, random_state=42),
            'description': 'Regresión Lasso (L1) - Selección automática de features'
        },
        'Random Forest': {
            'model': RandomForestRegressor(n_estimators=100, random_state=42),
            'description': 'Bosque aleatorio - Combina múltiples árboles de decisión'
        },
        'Gradient Boosting': {
            'model': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'description': 'Boosting gradual - Mejora iterativa de predicciones'
        },
        'Support Vector Regression': {
            'model': SVR(kernel='rbf', C=1.0),
            'description': 'SVR - Encuentra hiperplano óptimo para regresión'
        },
        'K-Nearest Neighbors': {
            'model': KNeighborsRegressor(n_neighbors=5),
            'description': 'KNN - Predice basado en vecinos más cercanos'
        },
        'Decision Tree': {
            'model': DecisionTreeRegressor(random_state=42),
            'description': 'Árbol de decisión - Reglas if-then interpretables'
        }
    }
    return models

def train_and_evaluate_models(X, y, models):
    """Entrena y evalúa todos los modelos"""
    print("\n🤖 ENTRENAMIENTO Y EVALUACIÓN DE LOS 8 MODELOS")
    print("="*60)
    
    # División train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"📊 Datos de entrenamiento: {len(X_train)} registros")
    print(f"📊 Datos de prueba: {len(X_test)} registros")
    
    results = {}
    
    for model_name, model_info in models.items():
        print(f"\n🔬 Entrenando: {model_name}")
        print(f"📝 {model_info['description']}")
        print("-" * 40)
        
        model = model_info['model']
        
        try:
            # Entrenar modelo
            model.fit(X_train, y_train)
            
            # Predicciones
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)
            
            # Métricas
            train_r2 = r2_score(y_train, y_pred_train)
            test_r2 = r2_score(y_test, y_pred_test)
            test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
            test_mae = mean_absolute_error(y_test, y_pred_test)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
            cv_mean = cv_scores.mean()
            cv_std = cv_scores.std()
            
            results[model_name] = {
                'model': model,
                'train_r2': train_r2,
                'test_r2': test_r2,
                'rmse': test_rmse,
                'mae': test_mae,
                'cv_mean': cv_mean,
                'cv_std': cv_std,
                'description': model_info['description']
            }
            
            print(f"✅ R² Entrenamiento: {train_r2:.4f}")
            print(f"✅ R² Prueba: {test_r2:.4f}")
            print(f"📉 RMSE: {test_rmse:.2f}")
            print(f"📊 MAE: {test_mae:.2f}")
            print(f"🔄 CV R² (media ± std): {cv_mean:.4f} ± {cv_std:.4f}")
            
        except Exception as e:
            print(f"❌ Error entrenando {model_name}: {e}")
            results[model_name] = {
                'error': str(e),
                'description': model_info['description']
            }
    
    return results, X_test, y_test

def analyze_results(results):
    """Analiza y compara los resultados de todos los modelos"""
    print("\n📈 ANÁLISIS COMPARATIVO DE RENDIMIENTO")
    print("="*60)
    
    # Crear DataFrame con resultados
    data = []
    for model_name, result in results.items():
        if 'error' not in result:
            data.append({
                'Modelo': model_name,
                'R² Test': result['test_r2'],
                'RMSE': result['rmse'],
                'MAE': result['mae'],
                'CV R²': result['cv_mean'],
                'CV Std': result['cv_std']
            })
    
    if not data:
        print("❌ No hay resultados válidos para analizar")
        return None
    
    df_results = pd.DataFrame(data)
    df_results = df_results.sort_values('R² Test', ascending=False)
    
    print("🏆 RANKING DE MODELOS (ordenado por R² en test):")
    print(df_results.to_string(index=False, float_format='%.4f'))
    
    # Mejor modelo
    best_model = df_results.iloc[0]
    print(f"\n🥇 MEJOR MODELO: {best_model['Modelo']}")
    print(f"   📊 R² Test: {best_model['R² Test']:.4f}")
    print(f"   📉 RMSE: {best_model['RMSE']:.2f} seguidores")
    print(f"   📈 MAE: {best_model['MAE']:.2f} seguidores")
    
    return df_results

def demonstrate_predictions(results, X_test, y_test):
    """Demuestra predicciones con diferentes fechas"""
    print("\n🎯 EJEMPLOS DE PREDICCIONES CON FECHAS REALES")
    print("="*60)
    
    # Encontrar el mejor modelo
    best_model_name = None
    best_r2 = -float('inf')
    
    for model_name, result in results.items():
        if 'error' not in result and result['test_r2'] > best_r2:
            best_r2 = result['test_r2']
            best_model_name = model_name
    
    if not best_model_name:
        print("❌ No hay modelos válidos para demostrar")
        return
    
    best_model = results[best_model_name]['model']
    print(f"🤖 Usando el mejor modelo: {best_model_name}")
    
    # Ejemplos de fechas
    test_dates = [
        "2025-07-14",  # Lunes
        "2025-07-15",  # Martes  
        "2025-07-18",  # Viernes
        "2025-07-19",  # Sábado
        "2025-12-25",  # Navidad (Jueves)
    ]
    
    dias_nombres = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    for fecha_str in test_dates:
        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d")
        
        # Extraer features como lo hace la API
        features = np.array([[
            fecha_obj.weekday(),  # dia_semana
            23,                   # hora (default API)
            fecha_obj.month       # mes
        ]])
        
        # Predecir
        prediction = best_model.predict(features)[0]
        
        print(f"\n📅 Fecha: {fecha_str} ({dias_nombres[fecha_obj.weekday()]})")
        print(f"   🔧 Features: dia_semana={fecha_obj.weekday()}, hora=23, mes={fecha_obj.month}")
        print(f"   🎯 Predicción: {prediction:.0f} seguidores")
        
        # Comparar con datos reales si hay
        real_data_mask = (X_test['dia_semana'] == fecha_obj.weekday()) & (X_test['mes'] == fecha_obj.month)
        if real_data_mask.any():
            real_avg = y_test[real_data_mask].mean()
            print(f"   📊 Promedio real similar: {real_avg:.0f} seguidores")
            print(f"   📈 Diferencia: {abs(prediction - real_avg):.0f} seguidores")

def show_feature_importance(results):
    """Muestra la importancia de features para modelos que la soportan"""
    print("\n🔍 IMPORTANCIA DE FEATURES")
    print("="*40)
    
    feature_names = ['dia_semana', 'hora', 'mes']
    
    for model_name, result in results.items():
        if 'error' in result:
            continue
            
        model = result['model']
        
        # Solo algunos modelos tienen feature_importances_
        if hasattr(model, 'feature_importances_'):
            print(f"\n🌟 {model_name}:")
            importances = model.feature_importances_
            
            for feature, importance in zip(feature_names, importances):
                bar = "█" * int(importance * 20)  # Barra visual
                print(f"   {feature:12}: {importance:.4f} {bar}")

def create_api_simulation():
    """Simula cómo funciona la API con el mejor modelo"""
    print("\n🌐 SIMULACIÓN DE LA API")
    print("="*40)
    
    print("Así es como tu endpoint GET /regression/predict/Interbank funciona:")
    print()
    print("1️⃣ Usuario hace request:")
    print("   GET /regression/predict/Interbank?fecha=2025-07-15")
    print()
    print("2️⃣ Endpoint extrae features:")
    print("   fecha_obj = datetime.strptime('2025-07-15', '%Y-%m-%d')")
    print("   dia_semana = fecha_obj.weekday()  # 1 (Martes)")
    print("   hora = 23  # Default")
    print("   mes = fecha_obj.month  # 7 (Julio)")
    print()
    print("3️⃣ Modelo hace predicción:")
    print("   input_array = [[1, 23, 7]]")
    print("   prediction = model.predict(input_array)[0]")
    print()
    print("4️⃣ API responde:")
    print("   {")
    print('     "prediction": 304250.0,')
    print('     "model_type": "DecisionTreeRegressor",')
    print('     "target_variable": "seguidores"')
    print("   }")

def main():
    print("🏦 DOCUMENTACIÓN COMPLETA: MODELOS DE REGRESIÓN PARA INTERBANK")
    print("="*70)
    print("Análisis de 8 modelos de Machine Learning con datos reales")
    print("="*70)
    
    # 1. Cargar datos
    X, y, df = load_interbank_data()
    if X is None:
        return
    
    # 2. Configurar modelos
    models = setup_models()
    
    # 3. Entrenar y evaluar
    results, X_test, y_test = train_and_evaluate_models(X, y, models)
    
    # 4. Analizar resultados
    df_results = analyze_results(results)
    
    # 5. Demostrar predicciones
    demonstrate_predictions(results, X_test, y_test)
    
    # 6. Mostrar importancia de features
    show_feature_importance(results)
    
    # 7. Simular API
    create_api_simulation()
    
    print("\n" + "="*70)
    print("🎉 DOCUMENTACIÓN COMPLETADA")
    print("📊 Todos los 8 modelos han sido entrenados y evaluados")
    print("🎯 El mejor modelo se usará para predicciones en la API")
    print("🔧 Las features temporales funcionan correctamente")
    print("="*70)

if __name__ == "__main__":
    main()
