$ErrorActionPreference = "Stop"
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker no está instalado o no está disponible en PATH."
}
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Archivo .env creado. Edita las contraseñas y DJANGO_SECRET_KEY antes de iniciar."
    exit 1
}
docker compose up --build -d
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
docker compose ps
Write-Host "Frontend: http://localhost:5173"
Write-Host "Admin: http://localhost:8000/admin/"
Write-Host "Si es la primera vez: docker compose exec api python manage.py createsuperuser"
