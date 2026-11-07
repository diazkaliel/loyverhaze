# Cajas registradoras y turnos — prueba manual

## Cambios de comportamiento
A partir de esta etapa **no se puede confirmar una venta en efectivo sin una caja abierta** en la sucursal correspondiente. Las ventas de pruebas anteriores se conservan; la relación del turno es opcional solo para el historial previo a esta versión.

## Preparar Windows (Python + Vite)
1. Guardar copia de `apps/api/db.sqlite3` si hay pruebas que conservar.
2. `git switch feat/foundation-catalog` y `git pull origin feat/foundation-catalog`.
3. Con el entorno Python activado, desde `apps/api`: `python manage.py migrate`.
4. Pruebas: `python manage.py test modules.catalog modules.organization modules.inventory modules.sales modules.cash config.test_auth`.
5. Desde `apps/web`: `npm run build` y `npm run dev`. Reiniciar Django si no se recarga automáticamente.

## Verificaciones
- [ ] Abrir Back Office → Turnos y efectivo.
- [ ] Abrir una caja de una sucursal con saldo inicial 10000.
- [ ] Intentar abrir una segunda caja en la misma sucursal: debe rechazarlo.
- [ ] Ir a Ventas (POS), elegir la sucursal y vender un artículo por 2500 con efectivo suficiente.
- [ ] Regresar a Turnos y efectivo: el esperado debe ser 12500 (el vuelto no aumenta el efectivo neto).
- [ ] Registrar entrada de 1000 con motivo y salida de 500 con motivo: esperado 13000.
- [ ] Cerrar como propietario/administrador contando 12900: diferencia -100.
- [ ] Comprobar que el turno queda cerrado, no se permite ingresar movimientos y el POS no deja cobrar en esa sucursal hasta reabrir una caja.
- [ ] Abrir un nuevo turno y comprobar que conserva el historial del anterior.
- [ ] Comprobar el rol Cajero: puede abrir y mover efectivo pero no cerrar un turno.

## Pendientes
- Modelo simplificado de **una caja abierta por sucursal**, sin terminales/cajones independientes.
- Sin operaciones de cajero asignado a una caja, autorización por terminal, transferencia de fondos o comprobantes fiscales.
- Cierres históricos no se reabren ni editan; los cobros no constituyen procesamiento externo de pagos.
- En PostgreSQL se debe evaluar concurrencia y pruebas de carrera; SQLite temporal no sustituye esa validación.
- No utilizar con ventas reales antes del hardening y auditoría completa.
