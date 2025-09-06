# HU-001: Importar Producto Terminado de OP en Transferencia de Inventario

| **ID** | **Título** |
| :--- | :--- |
| `HU-INV-001` | Creación Asistida de Transferencias desde una Orden de Producción |

---

**Como un** Supervisor de Almacén / Producción,
**Quiero** importar el **producto terminado** de una **única** Orden de Producción a una transferencia de inventario usando un asistente,
**Para que** pueda registrar Entradas de Inventario de forma rápida, precisa y con una trazabilidad directa a la producción.

---

## Flujo Detallado del Usuario (Workflow)

1.  **Inicio:** El usuario crea una nueva Transferencia de Inventario (`stock.picking`) y la mantiene en estado **'Borrador'**.
2.  **Activación:** Un botón **"Importar desde OP"** es visible. El usuario hace clic en él.
3.  **Apertura del Asistente:** Se abre una ventana emergente.
4.  **Selección de Origen:**
    *   El usuario selecciona una **Orden de Producción** de una lista filtrada (estados `confirmado`, `planificado`, `en progreso`, `para cerrar`).
5.  **Carga de Producto:** El usuario hace clic en un botón "Cargar Producto", y la tabla del wizard se llena con el **producto terminado** de la OP.
6.  **Ajuste de Cantidad:** El usuario ajusta la "Cantidad Ejecutada" para reflejar lo que realmente se ha producido. La "Cantidad Programada" es de solo lectura.
7.  **Confirmación:** El usuario hace clic en **"Añadir y Cerrar"**.
8.  **Resultado Directo:** El wizard se cierra. La transferencia original ahora tiene:
    *   **Una nueva línea de producto** añadida desde el wizard con el producto terminado y la cantidad ejecutada.
    *   El campo **"Documento Origen"** **sobrescrito** con la referencia de la OP seleccionada.
    *   El nuevo campo **"Orden de Trabajo" (`Many2one`)** rellenado con la OT seleccionada (si se eligió una).
    *   El campo **"Proyecto"** actualizado con el proyecto de la OP (si estaba vacío).

---

## Reglas de Negocio y Lógica

- **Visibilidad del Botón:** El botón "Importar desde OP" solo es visible si `state == 'draft'`.
- **Filtro de OPs:** El campo para seleccionar la OP debe tener un `domain` que filtre por `state in ['confirmed', 'planned', 'progress', 'to_close']`.
- **Relación Única:** Una transferencia solo puede ser poblada desde una única OP. Si se vuelve a usar el wizard, los valores de `origin` y `workorder_id` serán reemplazados por los nuevos.
- **Propagación de Proyecto (Solo una vez):** El `project_id` de la OP solo se copia a la transferencia si el campo `project_id` de la transferencia está vacío.
- **Lógica de Cantidades:** La "Cantidad Programada" viene de `product_qty` de la OP y no es editable. La "Cantidad Ejecutada" se inicializa con `qty_producing` de la OP y es editable por el usuario.

---

## Criterios de Aceptación (Acceptance Criteria)

- **Dado que** una Transferencia está en estado 'Borrador', **entonces** el botón "Importar desde OP" debe ser visible.
- **Dado que** abro el wizard y selecciono una OP, **cuando** confirmo, **entonces** el campo "Documento Origen" debe ser **exactamente** la referencia de esa OP.
- **Dado que** selecciono una OT en el wizard, **cuando** confirmo, **entonces** el campo "Orden de Trabajo" (`workorder_id`) en la transferencia debe apuntar a ese registro de OT.
- **Dado que** el campo "Documento Origen" es "OP/005" y uso el wizard para importar "OP/007", **cuando** confirmo, **entonces** el campo "Documento Origen" debe ser `"OP/007"`.
- La tabla de selección del producto debe mostrar las columnas: Checkbox, Producto, Cantidad Programada (solo lectura), Cantidad Ejecutada (editable), y UoM.
- **Dado que** importo una OP con 10 unidades programadas y 8 en producción, **cuando** la línea se añade a la transferencia, **entonces** la cantidad del movimiento debe ser 8 (o el valor que el usuario haya editado).
