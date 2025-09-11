# HU-MRP-002: Análisis y Explosión de Avíos
**Versión:** 1.0

**Como** una Analista de Fichas,
**Quiero** abrir una nueva **Lista de Materiales** (que funcionalmente es una "Ficha de Producción") en estado "Borrador", ajustar y añadir los avíos necesarios, y pasarla a estado "En Progreso",
**Para que** quede registrada la explosión de avíos detallada y lista para la revisión de Logística.

### Criterios de Aceptación:
-   **Dado que** un BOM está en "Borrador", **Cuando** lo abro, **Entonces** debo poder editar su lista de componentes.
-   **Dado que** he finalizado los ajustes, **Cuando** presiono un botón "Enviar a Aprobación", **Entonces** el estado del BOM debe cambiar a "En Progreso" y volverse de solo lectura para mi rol.
