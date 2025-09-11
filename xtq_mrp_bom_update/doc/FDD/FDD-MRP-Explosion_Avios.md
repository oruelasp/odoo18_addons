# Documento de Diseño Funcional (FDD): Explosión de Avíos (Ficha de Producción)
**Versión:** 3.0 (Basado en PLM/ECO Estándar)

---

### 1. Resumen Ejecutivo y Objetivos

Este documento define el diseño funcional para gestionar el proceso de **"Explosión de Avíos"** en Odoo v18, reutilizando el módulo estándar PLM (Product Lifecycle Management) a través de Órdenes de Cambio de Ingeniería (ECO). El objetivo es integrar el flujo de trabajo en Odoo sin desarrollos excesivos, vinculándolo directamente a la Orden de Producción (OP).

La solución usa ECOs como "Fichas de Producción", que generan revisiones controladas del BoM base, con un flujo de aprobación y activación de versiones. Se minimizan customizaciones, usando acciones estándar donde sea posible.

### 2. Análisis del Proceso Actual (AS-IS)

-   **Flujo de Trabajo:** Las analistas reciben la ficha técnica, ajustan cantidades en SIGAP y envían un reporte a Logística.
-   **Puntos de Dolor:** La "explosión" ocurre fuera del BOM final de la OP, el flujo de aprobación es externo y no hay control de versiones claro.

### 3. Propuesta de Solución (TO-BE)

Se propone reutilizar PLM para extender la funcionalidad de BoMs y OPs, con mínimas customizaciones.

1.  **OP con BoM Base:** Una OP se crea utilizando un BoM "plantilla" o de "muestra".
2.  **Creación de ECO desde OP:** Usar el botón estándar "Crear una orden de cambio de ingeniería" en la OP para generar un ECO que duplica el BoM base.
3.  **Ajuste y Flujo de Estados:** El ECO pasa por estados: `Borrador` -> `En Progreso` -> `Confirmado` / `Rechazado`, con aprobación. La explosión de avíos se hace en la nueva revisión del BoM.
4.  **Actualización Controlada:** Al aplicar el ECO, la nueva versión del BoM se activa. El Jefe de Producción actualiza la OP solo si la versión es efectiva.

### 4. Flujo de Trabajo Detallado (Usando PLM/ECO Estándar)

1.  **(Jefe de Producción):** Crea una OP con un BoM base (la "Orden de Muestra").
2.  **(Jefe de Producción):** Confirma la OP (esto genera el requerimiento de tela).
3.  **(Jefe de Producción):** Desde la OP, selecciona la acción estándar **"Crear una orden de cambio de ingeniería"** (en el menú de acciones).
    -   *Sistema (Automático):* Crea un ECO vinculado al BoM base de la OP, generando una nueva revisión del BoM en estado "Borrador".
4.  **(Analista de Fichas):** Abre el ECO en "Borrador". En la nueva revisión del BoM, presiona un botón custom **"Actualizar Cantidades Proporcionales"** (visible solo si hay ECO y OP relacionados). Esto recalcula cantidades basadas en la OP. Realiza la explosión de avíos y pasa el ECO a "En Progreso".
5.  **(Jefa de Logística):** Revisa el ECO en "En Progreso". Lo confirma (pasa a "Confirmado", aplica cambios y activa la nueva versión del BoM) o lo rechaza (vuelve a "Borrador" con nota).
6.  **(Jefe de Producción):** En la OP, presiona **"Actualizar lista de materiales"**.
    -   *Sistema:* Verifica que la nueva versión del BoM (vía ECO) sea efectiva. Si es así, actualiza los componentes. Si no, muestra un error.

### 5. Mapeo de Datos y Configuraciones (Basado en PLM)

-   **Modelo `mrp.eco`:**
    - Usar estados estándar: `new` (Borrador), `progress` (En Progreso), `confirmed` (Aprobado).
    - Añadir campo custom `rejection_note` para motivo de rechazo.
-   **Modelo `mrp.bom`:**
    - Usar revisiones de PLM para diferenciar versiones.
    - Añadir campo booleano computado `has_related_eco_and_op` (verdadero si hay ECO vinculado con OP asociada).
    - Añadir botón custom "Actualizar Cantidades Proporcionales" (visible si `has_related_eco_and_op` es verdadero; recalcula cantidades basadas en OP).
-   **Modelo `mrp.production`:**
    - Campo `sample_bom_id`: `Many2one` a `mrp.bom` (para rastrear el BoM base original).
-   **Vista `mrp.production.form`:**
    - No se necesita botón custom; usar acción estándar para crear ECO.
-   **Dependencias:** Agregar `'mrp_plm'` en `__manifest__.py`.
-   **Customizaciones Adicionales:** Wizard para rechazo en ECO, campo booleano y botón en BoM, validación condicional en `action_update_bom`.
