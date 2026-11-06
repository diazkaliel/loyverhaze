# Loyverhaze — instalación local (primera entrega)

## Requisitos

Docker Engine y Docker Compose.

## Inicio

1. Copiar `.env.example` como `.env` y establecer contraseñas y clave secreta locales seguras.
2. Ejecutar `docker compose up --build -d` desde la raíz.
3. Crear usuario administrador: `docker compose exec api python manage.py createsuperuser`.
4. Abrir `http://localhost:8000/admin/`, iniciar sesión con el administrador.
5. Abrir `http://localhost:5173` para utilizar el catálogo.
6. API OpenAPI: `http://localhost:8000/api/schema/` (requiere sesión).

## Pruebas

- API: `docker compose exec api python manage.py test modules.catalog`.
- Comprobar migraciones: `docker compose exec api python manage.py makemigrations --check --dry-run`.
- Compilación frontend: `docker compose exec web npm run build`.

## Alcance de esta entrega

- CRUD API para categorías y artículos con UUID, importes decimales, restricciones y permisos de escritura solo para personal administrador.
- Interfaz de listado y creación, con resultados reales desde PostgreSQL; no incluye edición/borrado desde la UI aunque la API lo soporte.
- Autenticación por sesión Django a través de /admin/ como acceso transitorio de desarrollo. **No es el flujo final de inicio de sesión del POS**.
- Arquitectura inicial **monotaller**. Falta separar por organización/sucursal, autorización granular y permisos por acción; no se debe utilizar con datos reales ni desplegar en producción todavía.
- Menús y distribución todavía **provisionales**, hasta contrastar las pantallas de Loyverse.

## Pendientes críticos

Autenticación propia del producto, organizaciones y sucursales, controles de aislamiento de datos por tenant, contratos API generados, workflow CI, bloqueo de dependencias, lint/format, pruebas E2E, auditoría y configuración de producción.
