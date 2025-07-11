import os
import sys
import subprocess

def limpiar_todos_los_raw():
    data_dir = os.path.dirname(os.path.abspath(__file__))
    archivos = [f for f in os.listdir(data_dir) if f.endswith('_raw.csv')]
    if not archivos:
        print('No se encontraron archivos *_raw.csv en el directorio data.')
        return
    for archivo in archivos:
        username = archivo.replace('_raw.csv', '')
        print(f'Limpiando: {archivo}...')
        # Ejecuta limpiar.py para cada archivo
        resultado = subprocess.run([sys.executable, os.path.join(data_dir, 'limpiar.py'), username], capture_output=True, text=True)
        print(resultado.stdout)
        if resultado.stderr:
            print('Error:', resultado.stderr)

if __name__ == "__main__":
    limpiar_todos_los_raw()