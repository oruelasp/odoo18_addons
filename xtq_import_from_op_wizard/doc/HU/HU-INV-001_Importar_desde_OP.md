# HU-001: Importar Componentes de Orden de Producción en Picking

| **ID** | **Título** |
| :--- | :--- |
| `HU-INV-001` | Creación Asistida y Acumulativa de Transferencias desde Órdenes de Producción |

---

**Como un** Supervisor de Almacén / Producción,
 **Quiero** importar los componentes de una Orden de Producción (y opcionalmente de una Orden de Trabajo) a una transferencia de inventario usando un asistente, pudiendo repetir el proceso para añadir componentes de otras OPs a la misma transferencia,
 **Para que** pueda crear Guías de Salida de forma rápida, precisa y con trazabilidad completa y acumulada.

---

## Flujo Detallado del Usuario (Workflow)

1.  **Inicio:** El usuario crea una nueva Transferencia de Inventario (`stock.picking`) y la mantiene en estado **'Borrador'**.
2.  **Activación:** Un nuevo botón **"Importar desde OP"** es visible en el formulario, ya que la transferencia está en estado 'Borrador'. El usuario hace clic en él.
3.  **Apertura del Asistente:** Se abre una única ventana emergente (pop-up).
4.  **Selección de Origen:**
    - El usuario selecciona una **Orden de Producción** de una lista que solo muestra OPs en estado `confirmado`, `planificado`, `en progreso` o `para cerrar`.
    - Opcionalmente, selecciona una **Orden de Trabajo** de una lista que se filtra automáticamente para mostrar solo las que pertenecen a la OP seleccionada.
5.  **Carga Dinámica de Componentes (`onchange`):** Inmediatamente después de seleccionar la OP (o la OT), la sección inferior del wizard se refresca, mostrando una tabla con los componentes requeridos.
6.  **Selección de Componentes:** La tabla muestra cada componente con:
    - Un **Checkbox** (marcado por defecto).
    - El **Producto**.
    - La **Cantidad Prevista** (solo lectura).
    - La **Cantidad a Mover** (editable, con el valor de la prevista por defecto).
    - La **UoM**.
    El usuario desmarca los ítems que no necesita y ajusta las "Cantidades a Mover" si es necesario.
7.  **Confirmación:** El usuario hace clic en el botón **"Añadir y Cerrar"**.
8.  **Resultado Acumulativo:** El wizard se cierra. La transferencia original ahora tiene:
    - **Nuevas líneas de producto** añadidas a las existentes, pobladas con los componentes y cantidades seleccionadas.
    - El campo **"Documento Origen"** actualizado, añadiendo la nueva referencia de la OP a las ya existentes.
    - El nuevo campo **"Origen de OT"** actualizado, añadiendo la referencia de la OT (si se seleccionó).
    - El campo **"Proyecto"** actualizado con el proyecto de la OP (solo si el campo estaba vacío).

---

## Reglas de Negocio y Lógica

- **Visibilidad del Botón:** El botón "Importar desde OP" solo es visible si `state == 'draft'`.
- **Filtro de OPs:** El campo para seleccionar la OP debe tener un `domain` que filtre por `state in ['confirmed', 'planned', 'progress', 'to_close']`.
- **Concatenación Acumulativa:** Si el campo `origin` ya tiene valor (ej. "OP/001"), al importar una nueva (`OP/002`), el campo se actualizará a `"OP/001, OP/002"`. Lo mismo aplica para el nuevo campo `workorder_origin`.
- **Propagación de Proyecto (Solo una vez):** El `project_id` de la OP solo se copia a la transferencia si el campo `project_id` de la transferencia está vacío. Esto evita sobreescribir un proyecto ya establecido.

---

## Criterios de Aceptación (Acceptance Criteria)

- **Dado que** una Transferencia está en estado 'Borrador', **entonces** el botón "Importar desde OP" debe ser visible.
- **Dado que** una Transferencia está en estado 'Realizado', **entonces** el botón "Importar desde OP" NO debe ser visible.
- **Dado que** abro el wizard, **cuando** busco una OP, **entonces** la lista no debe mostrar OPs en estado 'borrador', 'hecho' o 'cancelado'.
- **Dado que** selecciono una OP, **cuando** abro el selector de Órdenes de Trabajo, **entonces** solo deben aparecer las OTs de esa OP.
- **Dado que** el campo "Documento Origen" es "OP/005" y uso el wizard para importar "OP/007", **cuando** confirmo, **entonces** el campo "Documento Origen" debe ser `"OP/005, OP/007"`.
- La tabla de selección de componentes debe mostrar las columnas: Checkbox, Producto, Cantidad Prevista, Cantidad a Mover (editable), y UoM.
