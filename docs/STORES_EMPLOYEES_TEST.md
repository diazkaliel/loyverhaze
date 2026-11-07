# Sucursales y empleados — prueba manual

Esta entrega agrega pantallas funcionales a la navegación del Back Office:
- **Personal → Empleados**: listar, crear usuario nuevo (nombre y contraseña inicial) y modificar su rol.
- **Configuración → Sucursales**: listar, crear, renombrar y activar/desactivar sucursales.

## Ejecutar en Windows

1. Respaldar la base de pruebas actual.
2. Desde la raíz: `git switch feat/foundation-catalog` y `git pull origin feat/foundation-catalog`.
3. Con Python activado en `apps/api`, ejecutar `python manage.py migrate` y `python manage.py test modules.organization modules.catalog config.test_auth`.
4. Reiniciar Vite desde `apps/web`: `npm run dev`.
5. Abrir http://localhost:5173 e iniciar sesión como propietario de «Mi negocio».

## Escenarios

1. Ir a **Configuración → Sucursales**, crear «Sucursal Norte», renombrarla y verificar la persistencia tras recargar.
2. Ir a **Personal → Empleados**, crear «cajero_prueba» con contraseña única suficientemente robusta y rol Cajero.
3. Cerrar sesión, iniciar sesión como «cajero_prueba» y verificar que puede leer el catálogo, pero no modificarlo ni gestionar empleados/sucursales.
4. Volver al propietario, cambiar el rol del empleado a Administrador, comprobar que ahora puede administrar artículos y sucursales.
5. Verificar que no es posible cambiar el rol del último propietario a Cajero o Administrador.
6. Comprobar que los endpoints de otro negocio no revelan registros.

## Notas

- La cuenta nueva **no** es automáticamente personal de Django Admin. Solo pertenece a la organización activa.
- Las sucursales aún no pueden asignarse a empleados, existencias, cajas y ventas.
- El alta de empleados todavía no incluye invitaciones por correo, cambio obligatorio de contraseña inicial, segundo factor, recuperación de contraseña ni auditoría de accesos.
- No es una versión apta para producción.
