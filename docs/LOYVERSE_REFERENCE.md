# Referencia funcional de Loyverse — Loyverhaze

Principio: conservar la ubicación y jerarquía **verificadas** de los flujos de Loyverse; renovar únicamente su apariencia. No declarar equivalencia exacta cuando falten capturas actuales.

## Fuentes oficiales

- [Resumen de ventas en el Back Office](https://help.loyverse.com/es/help/sales-summary-report-back-office): al abrir el Back Office, el resumen de ventas aparece por defecto.
- [Añadir artículos desde Back Office](https://help.loyverse.com/es/help/how-add-items-loyverse-back-office): menú **Lista de artículos**, botón **Agregar artículo**, formulario **Crear artículo**, botón **Guardar**.
- [Vender por peso](https://help.loyverse.com/es/help/how-sell-items-weight): menú **Artículos → Lista de artículos**.
- [Añadir artículos y categorías en el TPV](https://help.loyverse.com/es/help/items-categories): desde el menú Artículos se accede a Categorías, con disposición específica móvil/tablet.

## Matriz de fidelidad

| Flujo | Jerarquía / orden | Posición exacta visual | Implementación actual |
|---|---|---|---|
| Abrir Back Office | Resumen de ventas por defecto | No verificada | Entrada informativa sin datos inventados |
| Artículos | Artículos → Lista de artículos | No verificada | Navegación, búsqueda, creación, edición |
| Categorías | Artículos → Categorías | No verificada | Navegación, búsqueda, creación, edición |
| Formulario artículo | Nombre, categoría, descripción, disponibilidad, precios y códigos | Requiere capturas | Campos básicos integrados con API |
| POS | Referencia móvil/tablet | No verificada | No implementado |

La navegación actual solo muestra opciones utilizables. Los demás menús se agregarán al construir sus módulos, manteniendo la jerarquía contrastada con Loyverse.

## Próxima verificación visual

Capturar el Back Office actual con autorización del usuario: 1) pantalla inicial, 2) menú Artículos expandido, 3) Lista de artículos, 4) formulario Crear artículo, 5) formulario Editar artículo, 6) Categorías. Comparar ubicaciones, tamaños y estados interactivos. Mantener identidad propia sin reproducir marcas ni activos propietarios.
