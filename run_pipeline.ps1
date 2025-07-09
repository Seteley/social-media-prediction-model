# Ejecuta el pipeline localmente en PowerShell
# Navega a la raíz del proyecto antes de ejecutar este script

# 1. Instalar dependencias
# python -m pip install --upgrade pip
# pip install playwright beautifulsoup4
# pip install unofficial-livecounts-api
# playwright install chromium


# Lista de usuarios a procesar
$usuarios = @(
    'Interbank',
    'BanBif',
    'BancodelaNacion',
    'bcrpoficial',
    'BancoPichincha',
    'bbva_peru',
    'BCPComunica',
    'ScotiabankPE'
)

foreach ($username in $usuarios) {
    Write-Host "\nProcesando usuario: $username" -ForegroundColor Cyan
    python scraper/scrape_interbank.py $username
    python data/limpiar.py $username
    python data/metricas.py $username
}

# 5. Commit y push de resultados (opcional, requiere git configurado y permisos)
# git config --global user.name "github-actions[bot]"
# git config --global user.email "github-actions[bot]@users.noreply.github.com"
# git add data/*.csv
# if ($LASTEXITCODE -ne 0) { Write-Host "No hay archivos CSV nuevos en data/" }
# git add scraper/*.txt
# if ($LASTEXITCODE -ne 0) { Write-Host "No hay archivos TXT nuevos en scraper/" }
# git add scraper/*.csv
# if ($LASTEXITCODE -ne 0) { Write-Host "No hay archivos CSV nuevos en scraper/" }
# git commit -m "[auto] Actualización de datos por script local" 2>$null
# if ($LASTEXITCODE -ne 0) { Write-Host "No hay cambios para commitear" }
# git push
