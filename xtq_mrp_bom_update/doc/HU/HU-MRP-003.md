# HU-MRP-003: Aprobación de la Ficha de Producción
**Versión:** 1.0

**Como** una Jefa de Logística,
**Quiero** revisar las Listas de Materiales que están en estado "En Progreso" y poder aprobarlas o rechazarlas, añadiendo un motivo en caso de rechazo,
**Para que** pueda dar la conformidad final a los componentes que se usarán en la producción.

### Criterios de Aceptación:
-   **Dado que** un BOM está "En Progreso", **Cuando** lo abro, **Entonces** debo ver los botones "Aprobar" y "Rechazar".
-   **Cuando** hago clic en "Aprobar", **Entonces** el estado del BOM debe cambiar a "Aprobado" y volverse de solo lectura.
-   **Cuando** hago clic en "Rechazar", **Entonces** el sistema debe solicitar un **motivo de rechazo** en un campo de texto, el estado del BOM debe volver a "Borrador" y la nota debe guardarse.
