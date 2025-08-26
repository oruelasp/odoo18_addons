# HU-001: Importar Componentes de Orden de Producción en Picking

| **ID** | **Título** |
| :--- | :--- |
| `HU-INV-001` | Creación Asistida de Transferencias desde una Orden de Producción |

---

**Como un** Supervisor de Almacén / Producción,
**Quiero** importar los componentes de una **única** Orden de Producción (y opcionalmente una Orden de Trabajo) a una transferencia de inventario usando un asistente,
**Para que** pueda crear Guías de Salida de forma rápida, precisa y con una trazabilidad directa.

---

## Flujo Detallado del Usuario (Workflow)

1.  **Inicio:** El usuario crea una nueva Transferencia de Inventario (`stock.picking`) y la mantiene en estado **'Borrador'**.
2.  **Activación:** Un nuevo botón **"Importar desde OP"** es visible. El usuario hace clic en él.
3.  **Apertura del Asistente:** Se abre una ventana emergente.
4.  **Selección de Origen:**
    *   El usuario selecciona una **Orden de Producción** de una lista filtrada (estados `confirmado`, `planificado`, `en progreso`, `para cerrar`).
    *   Opcionalmente, selecciona una **Orden de Trabajo** de una lista filtrada por la OP anterior.
5.  **Carga de Componentes:** El usuario hace clic en un botón "Cargar Componentes", y la tabla del wizard se llena con los materiales requeridos.
6.  **Selección de Componentes:** El usuario ajusta las "Cantidades a Mover" y desmarca los ítems que no necesita.
7.  **Confirmación:** El usuario hace clic en **"Añadir y Cerrar"**.
8.  **Resultado Directo:** El wizard se cierra. La transferencia original ahora tiene:
    *   **Nuevas líneas de producto** añadidas desde el wizard.
    *   El campo **"Documento Origen"** **sobrescrito** con la referencia de la OP seleccionada.
    *   El nuevo campo **"Orden de Trabajo" (`Many2one`)** rellenado con la OT seleccionada.
    *   El campo **"Proyecto"** actualizado con el proyecto de la OP (si estaba vacío).

---

## Reglas de Negocio y Lógica

- **Visibilidad del Botón:** El botón "Importar desde OP" solo es visible si `state == 'draft'`.
- **Filtro de OPs:** El campo para seleccionar la OP debe tener un `domain` que filtre por `state in ['confirmed', 'planned', 'progress', 'to_close']`.
- **Relación Única:** Una transferencia solo puede ser poblada desde una única OP. Si se vuelve a usar el wizard, los valores de `origin` y `workorder_id` serán reemplazados por los nuevos.
- **Propagación de Proyecto (Solo una vez):** El `project_id` de la OP solo se copia a la transferencia si el campo `project_id` de la transferencia está vacío.

---

## Criterios de Aceptación (Acceptance Criteria)

- **Dado que** una Transferencia está en estado 'Borrador', **entonces** el botón "Importar desde OP" debe ser visible.
- **Dado que** abro el wizard y selecciono una OP, **cuando** confirmo, **entonces** el campo "Documento Origen" debe ser **exactamente** la referencia de esa OP.
- **Dado que** selecciono una OT en el wizard, **cuando** confirmo, **entonces** el campo "Orden de Trabajo" (`workorder_id`) en la transferencia debe apuntar a ese registro de OT.
- **Dado que** el campo "Documento Origen" es "OP/005" y uso el wizard para importar "OP/007", **cuando** confirmo, **entonces** el campo "Documento Origen" debe ser `"OP/007"` (no una concatenación).
- La tabla de selección de componentes debe mostrar las columnas: Checkbox, Producto, Cantidad Prevista, Cantidad a Mover (editable), y UoM.
