# Prueba manual — Loyverhaze

## Preparación
1. `git switch feat/foundation-catalog`.
2. `cp .env.example .env` (en PowerShell: `Copy-Item .env.example .env`).
3. Editar .env: DJANGO_SECRET_KEY, POSTGRES_PASSWORD y contraseña dentro de DATABASE_URL deben ser seguros y coincidentes.
4. Linux/macOS: `sh scripts/start.sh`. Windows PowerShell: `.\\scripts\\start.ps1` (si la política de ejecución lo permite).
5. `docker compose exec api python manage.py createsuperuser`.
6. Iniciar sesión en http://localhost:8000/admin/ y abrir http://localhost:5173.

## Verificación funcional
- [ ] Se abren la interfaz, la API y la base de datos sin errores.
- [ ] El Back Office comienza en Resumen de ventas y no muestra números inventados.
- [ ] Artículos → Categorías: crear “Bebidas”, actualizar y verla tras recargar.
- [ ] Artículos → Lista de artículos: crear “Café”, SKU CAFE-001, categoría Bebidas y precio 2500.00.
- [ ] Buscar CAFE-001, abrirlo, cambiar el precio y guardar.
- [ ] Recargar la página y comprobar que el cambio persiste.
- [ ] Abrir en incógnito y comprobar que la API no revela datos sin autenticación.
- [ ] `docker compose exec api python manage.py test modules.catalog` termina con éxito.
- [ ] `docker compose exec api python manage.py makemigrations --check --dry-run` no presenta cambios.
- [ ] `docker compose exec web npm run build` termina con éxito.

## Fallos
Usar `docker compose logs --tail=150 api web db` y adjuntar el mensaje de error sin copiar datos secretos.

## Límites
Esta entrega es de desarrollo: usa Django Admin para el inicio de sesión, no tiene RBAC granular ni aislamiento de empresas. No introducir datos comerciales reales todavía.
