import csv
import os
from datetime import datetime
import re

def parse_num(valor):
    valor = valor.strip().replace(",", "")
    if valor.endswith("K"):
        return int(float(valor[:-1]) * 1000)
    if valor.endswith("M"):
        return int(float(valor[:-1]) * 1000000)
    try:
        return int(valor)
    except Exception:
        return 0

def parse_fecha_publicacion(fecha_pub, año_actual):
    fecha_pub = fecha_pub.strip()
    # Si ya tiene año, lo intentamos parsear
    formatos = ["%b %d, %Y", "%b %d"]
    for fmt in formatos:
        try:
            dt = datetime.strptime(fecha_pub, fmt)
            if fmt == "%b %d":
                dt = dt.replace(year=año_actual)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            continue
    return fecha_pub  # Si no se puede parsear, dejar igual

def limpiar_csv(username):
    input_file = f"data/{username}_raw.csv"
    output_file = f"data/{username}_clean.csv"
    año_actual = datetime.now().year
    with open(input_file, newline='', encoding="utf-8") as infile, open(output_file, "w", newline='', encoding="utf-8") as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            # Limpiar fecha_publicacion
            row["fecha_publicacion"] = parse_fecha_publicacion(row["fecha_publicacion"], año_actual)
            # Limpiar contenido
            row["contenido"] = re.sub(r"\s+", " ", row["contenido"]).strip()
            # Convertir a int los campos numéricos
            for campo in ["respuestas", "retweets", "likes", "guardados", "vistas"]:
                row[campo] = parse_num(row[campo])
            writer.writerow(row)
    print(f"Archivo limpio guardado en {output_file}")

if __name__ == "__main__":
    limpiar_csv("interbank")
