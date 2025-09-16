# HU-MRP-004: Actualización de Componentes en la OP
**Versión:** 1.0

**Como** un Jefe de Producción,
**Quiero** presionar el botón estándar **"Actualizar lista de materiales" (`action_update_bom`)** en la OP,
**Para que** el sistema verifique si la Lista de Materiales principal (`bom_id`) está aprobada y, si es así, actualice la lista de componentes de mi OP con la versión final.

### Criterios de Aceptación:
-   **Dado que** presiono "Actualizar lista de materiales" en una OP, **Cuando** el BOM en el campo `bom_id` está en estado "Aprobado", **Entonces** los componentes en la pestaña "Componentes" de la OP se actualizan.
-   **Dado que** presiono "Actualizar lista de materiales", **Cuando** el BOM en el campo `bom_id` NO está en estado "Aprobado", **Entonces** el sistema debe mostrar un mensaje de error indicando que "Solo se pueden usar Listas de Materiales aprobadas para actualizar la OP".
