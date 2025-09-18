# Especificación Técnica: `xtq_quant_attributes`
**Versión:** 1.0

## 1. Arquitectura General

La solución se implementará mediante la extensión de componentes existentes en Odoo, tanto en el backend como en el frontend, para lograr una funcionalidad no invasiva y escalable.

-   **Backend:** Se añadirá un campo de control en `product.template` y un método de consulta en `stock.lot`. No se modificarán modelos de `stock` críticos como `stock.quant` o `stock.move.line`.
-   **Frontend:** Se utilizará la técnica de "patching" de JavaScript para extender el `Renderer` de la vista de lista utilizada en la selección de lotes. La lógica será condicional y se activará únicamente para los productos configurados.

## 2. Modelo de Datos (Python)

### 2.1. Modelo `product.template`
-   **Archivo:** `models/product_template.py`
-   **Propósito:** Añadir un campo de activación para la funcionalidad.
-   **Campos a añadir:**
    -   `show_quality_attrs_in_picking`:
        -   **Tipo:** `fields.Boolean`
        -   **String:** "Mostrar Atributos de Calidad en Picking"
        -   **Help:** "Si se marca, la ventana de selección de lotes para este producto mostrará columnas adicionales con sus atributos de calidad."
        -   **Visibilidad:** Debe ser visible en el formulario del producto solo si el campo `tracking` está configurado como `'lot'`.

### 2.2. Modelo `stock.lot`
-   **Archivo:** `models/stock_lot.py`
-   **Propósito:** Crear un método eficiente para que el frontend pueda consultar los atributos de múltiples lotes en una sola llamada.
-   **Métodos a añadir:**
    -   `get_attributes_for_lots_view(self, lot_ids)`:
        -   **Decorador:** `@api.model`
        -   **Input:** `lot_ids` (una lista de enteros con los IDs de `stock.lot`).
        -   **Lógica de Negocio:**
            1.  Identificar los `product.attribute` que están marcados como `is_lot_attribute = True`. Estos serán las cabeceras de las columnas.
            2.  Realizar una única consulta al modelo `stock.lot.attribute.line` para obtener todos los valores de atributos para la lista de `lot_ids` proporcionada.
            3.  Procesar los resultados y estructurarlos en un formato JSON optimizado para el consumo del frontend.
        -   **Contrato de Salida (Output JSON):** El método debe devolver un diccionario JSON con la siguiente estructura:
            ```json
            {
                "headers": ["Tono", "Ancho Real", "% Trama", "% Urdimbre"],
                "data": {
                    "101": { "Tono": "7", "Ancho Real": "1.68" },
                    "102": { "Tono": "6", "% Trama": "-3%" },
                    ...
                }
            }
            ```
            Donde las claves de `data` son los `lot_id`.

## 3. Vistas (XML)

### 3.1. `views/product_template_views.xml`
-   **Propósito:** Añadir el campo de activación al formulario del producto.
-   **Especificación:**
    -   Heredar de la vista `stock.view_template_property_form`.
    -   Añadir el campo `show_quality_attrs_in_picking` después del campo `tracking`.
    -   Utilizar el atributo `attrs` para que el campo sea invisible si `tracking` es diferente de `'lot'`.

## 4. Componente Web (JavaScript / OWL)

### 4.1. Extensión del Renderer de la Vista de Selección de Lotes
-   **Componente Objetivo:** El desarrollador debe identificar el `Renderer` específico que Odoo v18 utiliza para la vista de lista dentro del modal de selección de lotes (probablemente un componente dentro del módulo `stock` o `web`).
-   **Técnica:** Utilizar `patch` del framework de Odoo para extender el componente sin modificar el código original.
-   **Lógica a Implementar en el Patch:**
    1.  **`willStart()` Hook:**
        -   Sobreescribir el hook `willStart`.
        -   Dentro de este hook, obtener el `product_id` del `stock.move` que se está procesando.
        -   Realizar un primer RPC para leer el valor del campo `show_quality_attrs_in_picking` de ese producto.
        -   Si el valor es `True`, obtener la lista de `lot_id` que se van a renderizar y realizar un segundo RPC al método `get_attributes_for_lots_view` del backend.
        -   Almacenar el resultado (headers y data) en el estado del componente (ej. `this.lotAttributes`).
    2.  **Modificación del Renderizado:**
        -   **Cabeceras:** Extender la lógica que renderiza las cabeceras de la tabla (`<thead>`) para que, si `this.lotAttributes.headers` existe, se añadan nuevas celdas (`<th>`) por cada header.
        -   **Filas:** Extender la lógica que renderiza las filas (`<tbody><tr>`). Para cada fila (que corresponde a un `stock.quant` o similar), obtener su `lot_id`.
        -   Buscar ese `lot_id` en `this.lotAttributes.data`.
        -   Añadir nuevas celdas (`<td>`) a la fila, mostrando el valor de cada atributo correspondiente. Si un lote no tiene un valor para un atributo, la celda debe quedar vacía.
