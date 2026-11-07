# Inicio de sesión Loyverhaze — verificación manual

Este flujo utiliza sesiones de Django y token CSRF, no credenciales almacenadas en el navegador.

## Windows / desarrollo sin Docker

- Actualizar rama: `git switch feat/foundation-catalog && git pull origin feat/foundation-catalog`.
- Mantener el backend Django activo en http://localhost:8000 (con el entorno Python local configurado).
- Reiniciar Vite desde `apps/web`: `npm run dev`.
- Abrir http://localhost:5173 y comprobar que aparece el formulario de Loyverhaze.
- Iniciar sesión con un usuario Django existente, verificar el catálogo y cerrar sesión mediante «Salir».
- Recargar: la sesión debe conservarse después de iniciar sesión, pero no después de cerrar sesión.
- Credenciales incorrectas deben producir un error sin iniciar sesión.
- En DevTools → Network, las solicitudes de API deben usar el origen `localhost:5173` y rutas `/api/session/`, `/api/login/` y `/api/logout/`.

## Pruebas automatizadas

Backend: `python manage.py test config.test_auth modules.catalog`
Frontend: `npm run build`

## Limitaciones

Este inicio de sesión es una primera versión para desarrollo. Falta protección contra intentos reiterados de acceso, registro de eventos de seguridad, MFA cuando corresponda, controles de sesión y políticas de contraseñas de producción. Las cuentas siguen gestionándose desde Django Admin. No reutilizar credenciales publicadas en chats ni utilizar esta versión con datos comerciales reales. PostgreSQL es la base de datos obligatoria para el despliegue comercial.
