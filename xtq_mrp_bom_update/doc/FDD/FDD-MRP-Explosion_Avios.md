# Documento de Diseño Funcional (FDD): Explosión de Avíos (Ficha de Producción)
**Versión:** 1.1

---

### 1. Resumen Ejecutivo y Objetivos

Este documento define el diseño funcional para gestionar el proceso de **"Explosión de Avíos"** en Odoo v18. El objetivo es transformar el proceso actual en un flujo de trabajo integrado y auditable directamente vinculado a la Orden de Producción (OP).

La solución introduce el concepto de **"Ficha de Producción"**, que es una copia única y editable de la Lista de Materiales (BOM) base, permitiendo un ajuste detallado de los componentes y un flujo de aprobación formal.

### 2. Análisis del Proceso Actual (AS-IS)

-   **Flujo de Trabajo:** Las analistas reciben la ficha técnica, ajustan cantidades en SIGAP y envían un reporte a Logística.
-   **Puntos de Dolor:** La "explosión" ocurre fuera del BOM final de la OP, el flujo de aprobación es externo y no hay control de versiones claro.

### 3. Propuesta de Solución (TO-BE)

Se propone un flujo de trabajo que extiende la funcionalidad de las Listas de Materiales y las Órdenes de Producción.

1.  **OP con BOM Base:** Una OP se crea utilizando un BOM "plantilla" o de "muestra".
2.  **Botón "Crear Ficha de Producción":** Un nuevo botón en la OP duplicará el BOM base, lo vinculará a la OP y lo pondrá en estado "Borrador".
3.  **Ajuste y Flujo de Estados:** La nueva "Ficha de Producción" (el BOM duplicado) pasará por los estados: `Borrador` -> `En Progreso` -> `Aprobado` / `Rechazado`.
4.  **Actualización Controlada:** El Jefe de Producción solo podrá actualizar los componentes de la OP si la "Ficha de Producción" asociada está en estado "Aprobado".

### 4. Flujo de Trabajo Detallado

1.  **(Jefe de Producción):** Crea una OP con un BOM base (la "Orden de Muestra").
2.  **(Jefe de Producción):** Confirma la OP (esto genera el requerimiento de tela).
3.  **(Jefe de Producción):** Presiona el nuevo botón **"Crear Ficha de Producción"**.
    -   *Sistema (Automático):* Duplica el BOM base, lo vincula a la OP (asignándolo al campo `bom_id`), mueve el BOM original al nuevo campo `sample_bom_id`, ajusta las cantidades de los componentes proporcionalmente a la cantidad de la OP y deja el nuevo BOM en estado "Borrador".
4.  **(Analista de Fichas):** Abre la "Ficha de Producción" (el nuevo BOM) en estado "Borrador". Realiza la explosión de avíos y la pasa a estado **"En Progreso"**.
5.  **(Jefa de Logística):** Revisa la "Ficha de Producción" que está "En Progreso". La aprueba (pasa a estado **"Aprobado"**) o la rechaza (vuelve a "Borrador" con una nota).
6.  **(Jefe de Producción):** En la OP, presiona el botón estándar **"Actualizar lista de materiales" (`action_update_bom`)**.
    -   *Sistema:* Verifica que el `bom_id` de la OP esté en estado "Aprobado". Si es así, actualiza los componentes. Si no, muestra un error.

### 5. Mapeo de Datos y Configuraciones

-   **Modelo `mrp.bom`:**
    -   `state`: `Selection` con los estados: `[('draft', 'Borrador'), ('in_progress', 'En Progreso'), ('approved', 'Aprobado'), ('rejected', 'Rechazado')]`.
    -   `rejection_note`: Campo `Text` para el motivo del rechazo.
-   **Modelo `mrp.production`:**
    -   `sample_bom_id`: `Many2one` a `mrp.bom` (este es el único campo nuevo).
-   **Vista `mrp.production.form`:**
    -   Añadir el botón **"Crear Ficha de Producción"** junto al campo `bom_id`.
    -   Hacer visible el nuevo campo `sample_bom_id`.
