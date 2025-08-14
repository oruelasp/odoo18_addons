# HU-002: Registrar Cantidades a Producir en Matriz
**Rol:** Líder de Taller

## 1. Historia de Usuario
**Como** Líder de Taller,
**Quiero** ver la matriz de una OP planificada y registrar las cantidades **a producir ahora** (`qty_producing`) directamente en cada celda,
**Para que** pueda reportar el avance de la producción de forma clara y detallada por cada Tono y Talla, preparando la orden para su finalización.

## 2. Flujo de Trabajo (Paso a Paso)
1. Abre una OP en estado "Planificación Confirmada".
2. Navega a la pestaña "Matriz de Producción".
3. Para cada celda, el sistema muestra la información en el formato: `[Campo editable: Cantidad a Producir] / [Campo bloqueado: Cantidad Programada]`.
4. Ingresa las cantidades que se van a producir en esta tanda en el campo **"Cantidad a Producir"** de cada celda.
5. **Guarda** los cambios en la OP. La producción aún no se ha ejecutado.

## 3. Criterios de Aceptación
- **Dado** que el estado de la matriz es "Planificación Confirmada", **entonces** cada celda debe mostrar un campo de entrada para **"Cantidad a Producir"** (`qty_producing`) y un valor de solo lectura para **"Cantidad Programada"** (`product_qty`), separados por un "/".
- El Líder de Taller DEBE poder editar los valores de "Cantidad a Producir".
- El Líder de Taller NO DEBE poder editar los valores de "Cantidad Programada".
