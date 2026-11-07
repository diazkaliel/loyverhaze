# Inventario por sucursal — Entrega inicial

## Incluye

- Existencias por combinación de artículo y sucursal; los artículos sin movimientos muestran stock 0.
- Ledger inmutable de movimientos de entrada y ajuste (positivo o negativo).
- Registro transaccional: cantidad actual + evento de auditoría en una misma transacción.
- Bloqueo de la fila del artículo al registrar un movimiento; evita actualizaciones simultáneas inconsistentes en PostgreSQL.
- Claves UUID de idempotencia por organización para evitar doble contabilización en reintentos.
- Restricciones de stock no negativo, referencias por organización y permisos de escritura (propietario/administrador).
- Listado de los últimos 200 movimientos. Sin paginación todavía.

## Prueba en Windows con Python y Vite

1. Actualiza la rama `feat/foundation-catalog` y guarda una copia de la base de datos local si tiene información que quieres conservar.
2. Activa el entorno Python y entra a `apps/api`.
3. Ejecuta `python manage.py migrate`.
4. Ejecuta `python manage.py test modules.catalog modules.organization modules.inventory config.test_auth`.
5. Reinicia Django y Vite si no recargaron sus configuraciones automáticamente.
6. Entra a Loyverhaze → Inventario → Existencias.
7. Verifica que un artículo y una sucursal previamente creados aparezcan con stock 0.
8. Registra una Entrada de 10.000 unidades, comprueba stock 10.000.
9. Registra un Ajuste de -2.000, comprueba stock 8.000.
10. Intenta ajustar -9.000; debe rechazarse sin modificar stock ni historial.
11. Ve a Inventario → Movimientos y verifica que hay exactamente dos movimientos válidos.
12. Inicia sesión como cajero: solo puede leer, no registrar cambios.

## Límites

- No hay descuentos automáticos de inventario por ventas; módulo de ventas pendiente.
- No hay transferencias entre sucursales, órdenes de compra, lotes, seriales, reservas ni valoración.
- El historial no permite edición/borrado; futuras correcciones deben hacerse mediante movimientos compensatorios.
- Las filas de balance se crean al primer movimiento y se gestionan en transacciones; el modelo está pensado para PostgreSQL y la ejecución SQLite local no representa una prueba suficiente de concurrencia.
- No usar con inventario comercial real antes de validar migraciones, CI, pruebas de estrés, seguridad y operaciones de ventas.
