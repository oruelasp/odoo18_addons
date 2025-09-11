# HU-MRP-002: Análisis y Explosión de Avíos
**Versión:** 3.0

**Como** una Analista de Fichas,
**Quiero** abrir un ECO en estado "Borrador", presionar un botón "Actualizar Cantidades Proporcionales" (visible solo si hay OP relacionada), ajustar y añadir los avíos necesarios en la nueva revisión del BoM, y pasarlo a estado "En Progreso",
**Para que** quede registrada la explosión de avíos detallada y lista para la revisión de Logística.

### Criterios de Aceptación:
-   **Dado que** un ECO está en "Borrador", **Cuando** lo abro, **Entonces** debo poder editar la nueva revisión del BoM.
-   **Dado que** el BoM tiene un ECO y OP relacionados (verificado por campo booleano computado `has_related_eco_and_op`), **Entonces** un botón "Actualizar Cantidades Proporcionales" debe aparecer en la vista del BoM.
-   **Cuando** presiono "Actualizar Cantidades Proporcionales", **Entonces** las cantidades de componentes se recalculan proporcionalmente basadas en la cantidad de la OP relacionada.
-   **Dado que** he finalizado los ajustes, **Cuando** presiono un botón "Enviar a Aprobación", **Entonces** el estado del ECO debe cambiar a "En Progreso" y volverse de solo lectura para mi rol.
