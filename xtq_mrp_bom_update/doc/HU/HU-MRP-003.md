# HU-MRP-003: Aprobación de la Ficha de Producción
**Versión:** 3.0

**Como** una Jefa de Logística,
**Quiero** revisar los ECOs que están en estado "En Progreso" y poder confirmarlos o rechazarlos, añadiendo un motivo en caso de rechazo,
**Para que** pueda dar la conformidad final a los componentes que se usarán en la producción.

### Criterios de Aceptación:
-   **Dado que** un ECO está "En Progreso", **Cuando** lo abro, **Entonces** debo ver botones para confirmar o rechazar.
-   **Cuando** confirmo, **Entonces** el ECO pasa a "Confirmado", aplica la nueva revisión del BoM y lo hace efectivo (archivando la versión anterior).
-   **Cuando** rechazo, **Entonces** el sistema solicita un motivo, el ECO vuelve a "Borrador" y la nota se guarda.
