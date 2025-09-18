# ID: HU-INV-001
# Título: Selección de Lotes (Rollos) Asistida por Atributos de Calidad
**Versión:** 1.0

## Rol, Necesidad y Objetivo

**Como** una planificadora de UDP (Erika),
**Quiero** ver los atributos de calidad clave (Tono, Ancho Real, % Trama, % Urdimbre) como columnas en la pantalla de selección de rollos cuando estoy realizando un comprometido de tela,
**Para que** pueda comparar y seleccionar los rollos más adecuados para una Orden de Producción de manera rápida y eficiente, sin tener que abrir cada lote individualmente.

## Workflow del Usuario

1.  **Configuración (Admin):** Un administrador navega a la plantilla del producto "DENIM STRECH ART. 5238 NEGRO". En la pestaña de Inventario, marca la nueva casilla **"Mostrar Atributos de Calidad en Picking"**.
2.  **Ejecución (Usuario UDP):** Erika abre un Picking de Compromiso (`ATMN/Existencias` -> `ATMN/Salida`).
3.  Hace clic en **"Agregar una línea"** y selecciona el producto "DENIM STRECH...".
4.  **Resultado:** La ventana emergente que muestra los lotes disponibles se carga con **columnas adicionales**: "Tono", "Ancho Real", "% Trama", etc.
5.  **Toma de Decisión:** Erika puede ahora ordenar la lista por "Tono" para agrupar visualmente los rollos similares y tomar la mejor decisión.
6.  **Selección:** Selecciona las líneas de los rollos que cumplen con los criterios y confirma.

## Criterios de Aceptación

-   Debe existir un nuevo campo booleano `show_quality_attrs_in_picking` en el modelo `product.template`.
-   Si el booleano es `False` para un producto, la ventana de selección de lotes debe funcionar de manera estándar.
-   Si el booleano es `True`, la ventana debe mostrar columnas adicionales correspondientes a los atributos marcados como "Es un Atributo de Lote".
-   Las nuevas columnas deben ser ordenables.
