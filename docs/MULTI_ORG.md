# Organizaciones y sucursales — entrega inicial

## Alcance
- Modelos Organization, Store y Membership (owner, manager, cashier).
- Los artículos y categorías se asocian obligatoriamente a una organización.
- Cada consulta y mutación del catálogo verifica la membresía del usuario autenticado.
- El Back Office puede seleccionar entre las organizaciones a las que pertenece el usuario.
- La edición del catálogo requiere rol owner o manager; cashier dispone de lectura.
- No se aceptan IDs de organización inyectados en el cuerpo de un artículo para cambiar de negocio.
- La migración del catálogo anterior mantiene sus UUID y lo incorpora a "Mi negocio" / "Sucursal principal".

## Migrar la base existente (Windows, entorno local)
**Haz copia de seguridad de apps/api/db.sqlite3 antes de migrar** si ahí tienes datos de prueba que quieras conservar.

1. `git switch feat/foundation-catalog`
2. `git pull origin feat/foundation-catalog`
3. En el entorno Python de apps/api, `python manage.py migrate`.
4. Si el usuario existente no fue promovido automáticamente (solo se migran superusuarios preexistentes): `python manage.py assign_owner TU_USUARIO`.
5. `python manage.py test modules.organization modules.catalog config.test_auth`.
6. Reiniciar Vite y probar desde http://localhost:5173.

En bases nuevas también hay que crear el usuario con `python manage.py createsuperuser` y vincularlo mediante `python manage.py assign_owner TU_USUARIO`.

## Restricciones todavía pendientes
- Las sucursales existen en BD, pero no se asignan existencias, cajas ni operaciones por sucursal.
- La administración de organizaciones, miembros y sucursales todavía se realiza mediante Django Admin; no existe UI de empleados ni invitaciones.
- No se han implementado autorización granular por acción, auditoría, facturación, impuestos, inventario multisucursal o tenant-aware reporting.
- El desarrollo local con SQLite es temporal; la arquitectura comercial exige PostgreSQL.
- No usar esta entrega con datos reales hasta completar seguridad, pruebas y configuración productiva.
