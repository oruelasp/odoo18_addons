# HU-MRP-001: Creación de la Ficha de Producción
**Versión:** 3.0

**Como** un Jefe de Producción,
**Quiero** seleccionar la acción estándar "Crear una orden de cambio de ingeniería" desde una OP confirmada,
**Para que** el sistema cree un ECO que duplique automáticamente la Lista de Materiales base y genere una nueva revisión vinculada a mi OP, dejándola lista para el análisis de avíos.

### Criterios de Aceptación:
-   **Dado que** una OP está confirmada con un BoM base, **Cuando** selecciono "Crear una orden de cambio de ingeniería" desde el menú de acciones de la OP, **Entonces** se debe crear un nuevo ECO en `mrp.eco` vinculado al BoM y a la OP.
-   El ECO debe generar una nueva revisión del BoM con el nombre de la OP en su descripción.
-   El campo `bom_id` de la OP debe poder actualizarse a la nueva revisión una vez aplicada.
-   El BoM original debe rastrearse (e.g., vía `sample_bom_id` custom en OP).
