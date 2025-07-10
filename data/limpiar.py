import csv
import os
from datetime import datetime, timezone, timedelta
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
    # Si es 'now', 'x m' (minutos), o formato relativo tipo '6 h', '7 h', etc.
    if fecha_pub.lower() == 'now':
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    match_min = re.match(r"(\d+) m", fecha_pub)
    if match_min:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    match = re.match(r"(\d+) h", fecha_pub)
    if match:
        horas = int(match.group(1))
        dt = datetime.now(timezone.utc) - timedelta(hours=horas)
        return dt.strftime("%Y-%m-%d")
    # Si ya tiene año, lo intentamos parsear
    try:
        dt = datetime.strptime(fecha_pub, "%b %d, %Y")
        return dt.strftime("%Y-%m-%d")
    except Exception:
        pass
    # Si es solo mes y día, parsear manualmente para evitar warning
    try:
        meses = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        partes = fecha_pub.split()
        if len(partes) == 2 and partes[0] in meses:
            mes = meses[partes[0]]
            dia = int(partes[1])
            hoy = datetime.now(timezone.utc).date()
            fecha_candidata = datetime(hoy.year, mes, dia).date()
            # Si la fecha es futura respecto a hoy, es del año pasado
            if fecha_candidata > hoy:
                fecha_candidata = datetime(hoy.year - 1, mes, dia).date()
            return fecha_candidata.strftime("%Y-%m-%d")
    except Exception:
        pass
    return fecha_pub  # Si no se puede parsear, dejar igual

def limpiar_csv(username):
    input_file = f"data/{username}_raw.csv"
    output_file = f"data/{username}_clean.csv"
    año_actual = datetime.now(timezone.utc).year
    file_exists = os.path.isfile(output_file)
    with open(input_file, newline='', encoding="utf-8") as infile, open(output_file, "a", newline='', encoding="utf-8") as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for row in reader:
            # Obtener la fecha de captura (primera columna)
            fecha_captura = row[fieldnames[0]] if fieldnames else None
            # Limpiar fecha_publicacion, usando fecha_captura si es relativa
            fecha_pub_original = row["fecha_publicacion"]
            fecha_pub_limpia = parse_fecha_publicacion(fecha_pub_original, año_actual)
            # Si la fecha original es 'now', 'x m', 'x h', etc., usar fecha_captura
            if fecha_pub_original.lower() == 'now' or re.match(r"(\d+) m", fecha_pub_original) or re.match(r"(\d+) h", fecha_pub_original):
                row["fecha_publicacion"] = fecha_captura
            else:
                row["fecha_publicacion"] = fecha_pub_limpia
            # Limpiar contenido
            row["contenido"] = re.sub(r"\s+", " ", row["contenido"]).strip()
            # Convertir a int los campos numéricos
            for campo in ["respuestas", "retweets", "likes", "guardados", "vistas"]:
                row[campo] = parse_num(row[campo])
            # No agregar si algún campo está vacío
            if any(str(row[campo]).strip() == '' for campo in fieldnames):
                continue
            writer.writerow(row)
    print(f"Archivo limpio guardado en {output_file}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = "interbank"
    limpiar_csv(username)
