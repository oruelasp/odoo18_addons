# ID: HU-MRP-001
# Título: Configuración de Categorías de Productos para Liquidación
**Versión:** 1.0

**Como** un Administrador del Sistema,
**Quiero** acceder a una sección en los Ajustes de Manufactura para configurar qué categorías de productos serán elegibles para el proceso de "Liquidación de Corte",
**Para que** pueda controlar con precisión en qué componentes de las Órdenes de Producción aparecerá el botón de liquidación, asegurando que solo los productos relevantes (como telas) tengan esta funcionalidad activa.

---
### Criterios de Aceptación:

*   **Dado que** soy un usuario con permisos de Administrador,
    **Cuando** navego a `Manufactura > Configuración > Ajustes`,
    **Entonces** debe existir una nueva sección llamada "Liquidación de Corte en Producción".

*   **Dado que** estoy en la sección "Liquidación de Corte en Producción",
    **Cuando** miro las opciones,
    **Entonces** debo ver un campo de selección múltiple (`Many2many`) que me permita elegir una o más "Categorías de Productos".

*   **Dado que** he seleccionado y guardado las categorías deseadas,
    **Cuando** un usuario de producción abre una Orden de Producción,
    **Entonces** el botón de "Liquidación" en la línea de un componente solo será visible si el producto de esa línea pertenece a una de las categorías seleccionadas (o a una categoría hija de las seleccionadas).
