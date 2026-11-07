# POS — primera venta real (efectivo)

## Referencia funcional
- https://help.loyverse.com/es/help/make-sales
- Flujo de Loyverse: Pantalla de ventas → seleccionar artículos → ticket lateral → Cobrar → Efectivo recibido → Nueva venta.
- Pantalla actual: cuadrícula a la izquierda y ticket a la derecha (estructura inicial); falta auditoría visual de posiciones exactas con capturas recientes de Loyverse.

## Alcance funcional
- Crea ventas confirmadas en efectivo con ticket de líneas y precios congelados.
- Calcula precios y cambio en Django usando Decimal; no confía en totales enviados por React.
- Valida sucursal activa y artículos pertenecientes a la organización.
- Una transacción ACID registra ticket, líneas y movimientos de salida de stock.
- Si no hay stock suficiente o efectivo suficiente, se revierte toda la venta.
- Clave UUID de idempotencia: reintentar el mismo cobro retorna la misma venta.
- Cajeros pueden cobrar; listado administrativo de ventas disponible para propietarios/administradores.
- No procesa tarjetas ni pagos externos; los cobros en efectivo son registros internos y no representan una integración con una pasarela.

## Prueba manual (Windows, Django + Vite)
1. Respaldar la base local de pruebas.
2. Actualizar `feat/foundation-catalog` con `git pull`.
3. En `apps/api`: `python manage.py migrate` y `python manage.py test modules.catalog modules.organization modules.inventory modules.sales config.test_auth`.
4. En `apps/web`: ejecutar `npm run build`, luego `npm run dev`.
5. Iniciar sesión en http://localhost:5173, abrir Ventas (POS).
6. Seleccionar sucursal y artículo con stock positivo. Agregar 2 unidades.
7. Cobrar efectivo suficiente. Verificar total, vuelto y nueva venta.
8. Inventario → Existencias: stock debe disminuir exactamente en 2.
9. Inventario → Movimientos: debe quedar una salida con razón «Venta».
10. Intentar vender más unidades de las disponibles: el servidor debe rechazar el cobro sin crear venta.
11. Iniciar sesión como cajero: puede vender pero no acceder a administración de empleados.
12. Confirmar que la misma clave de idempotencia no produce dos ventas (prueba automatizada).

## Restricciones y próximos pasos
- Sin descuento, impuestos fiscales, devoluciones, mesas, tickets abiertos, turnos/caja, impresión, pago con tarjeta, pagos fraccionados ni sincronización offline.
- Sin configuración monetaria formal por organización; importes de dos decimales para esta primera iteración.
- La venta solo se confirma online; el POS no es todavía offline-first.
- Debe pasar CI y pruebas de concurrencia en PostgreSQL antes de uso comercial.
