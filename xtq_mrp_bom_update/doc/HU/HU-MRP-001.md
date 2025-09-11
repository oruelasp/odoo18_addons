# HU-MRP-001: Creación de la Ficha de Producción
**Versión:** 1.0

**Como** un Jefe de Producción,
**Quiero** presionar un botón "Crear Ficha de Producción" en una OP confirmada,
**Para que** el sistema duplique automáticamente la Lista de Materiales base, la asigne como el nuevo BOM de mi OP y recalcule las cantidades de los componentes en base a la cantidad total de la OP, dejándolo listo para el análisis de avíos.

### Criterios de Aceptación:
-   **Dado que** una OP está confirmada con un BOM base, **Cuando** presiono "Crear Ficha de Producción", **Entonces** se debe crear un nuevo registro en `mrp.bom`.
-   El campo `reference` del nuevo BOM debe contener el nombre de la OP.
-   La cantidad a producir (`product_qty`) del nuevo BOM debe ser igual a la cantidad de la OP.
-   Las cantidades de los componentes del nuevo BOM deben ser recalculadas proporcionalmente.
-   El campo `bom_id` de la OP debe apuntar a este nuevo BOM.
-   El BOM original debe ser almacenado en el nuevo campo `sample_bom_id` de la OP.
