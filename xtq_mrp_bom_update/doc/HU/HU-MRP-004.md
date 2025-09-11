# HU-MRP-004: Actualización de Componentes en la OP
**Versión:** 3.0

**Como** un Jefe de Producción,
**Quiero** presionar el botón estándar **"Actualizar lista de materiales"** en la OP,
**Para que** el sistema verifique si la nueva revisión del BoM (aprobada vía ECO) está efectiva y, si es así, actualice la lista de componentes de mi OP con la versión final.

### Criterios de Aceptación:
-   **Dado que** presiono "Actualizar lista de materiales" en una OP, **Cuando** la revisión del BoM está efectiva (validada y vigente vía ECO), **Entonces** los componentes en la pestaña "Componentes" de la OP se actualizan.
-   **Dado que** presiono el botón, **Cuando** la revisión NO está efectiva, **Entonces** muestra un error: "Solo se pueden usar revisiones de BoM efectivas para actualizar la OP".
