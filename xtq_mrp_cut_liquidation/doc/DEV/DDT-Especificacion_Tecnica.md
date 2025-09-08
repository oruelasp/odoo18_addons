# Especificación Técnica - Addon `xtq_mrp_cut_liquidation`
**Versión:** 1.1

## 1. Modelo de Datos

### 1.1. `mrp.cut.liquidation.line` (Nuevo Modelo)
Este modelo almacenará cada línea de tendido de una liquidación.
*   `stock_move_id`: `Many2one` a `stock.move` (Vínculo a la cabecera).
*   `sequence`: `Integer` ("Nº Tendido").
*   `fabric_width`: `Float` ("Ancho Tela").
*   `fabric_out_qty`: `Float` ("Salida Tela").
*   `actual_spread_meters`: `Float` ("Tendido Real").
*   `difference_qty`: `Float` ("Difer.", computado `fabric_out_qty - actual_spread_meters`).
*   `marker_length`: `Float` ("Trazo").
*   `number_of_plies`: `Integer` ("Paños").
*   `final_marker_qty`: `Float` ("Trazo Final", computado `marker_length * number_of_plies`).
*   `scrap_percentage`: `Float` ("Merma (%)").
*   `scrap_quantity`: `Float` ("Cant. Merma", computado).
*   `effective_consumption`: `Float` ("Consumo Efectivo", computado).

### 1.2. `stock.move` (Modelo Heredado)
Se extiende para gestionar la liquidación.
*   `liquidation_line_ids`: `One2many` a `mrp.cut.liquidation.line`.
*   `liquidation_visible`: `Boolean` (Computado, para visibilidad del botón).
*   `total_scrap_qty`: `Float` ("Merma Total", computado, suma de `scrap_quantity`).
*   `total_effective_consumption`: `Float` ("Consumo Real Total", computado, suma de `effective_consumption`).

### 1.3. `res.config.settings` (Modelo Heredado)
Se añade la configuración del módulo.
*   `liquidation_product_categ_ids`: `Many2many` a `product.category`.
*   `module_xtq_mrp_cut_liquidation`: `Boolean` (Campo técnico para la instalación).

## 2. Vistas (XML)

### 2.1. `res_config_settings_views.xml` (Nueva Vista)
*   Heredar la vista de Ajustes de Manufactura para añadir la sección "Liquidación de Corte" y el campo `liquidation_product_categ_ids`.

### 2.2. `mrp_production_views.xml` (Vista Heredada)
*   Modificar la vista de árbol de `move_raw_ids`.
*   Añadir un `button` que llame al método `action_open_cut_liquidation`.
*   El atributo `invisible` del botón estará ligado al campo `liquidation_visible`.

### 2.3. `mrp_cut_liquidation_views.xml` (Nueva Vista)
*   Definir la `ir.actions.act_window` que abre la vista formulario del `stock.move`.
*   Crear una vista `form` específica para la liquidación (`view_mode`: `form`).
    *   **Cabecera:** Campos de `stock.move` en modo solo lectura (`product_id`, `product_uom_qty`).
    *   **Cuerpo:** Campo `liquidation_line_ids` renderizado como una lista editable (`tree` editable `bottom`).
    *   **Pie de Página:** Campos totalizadores (`total_scrap_qty`, `total_effective_consumption`).

## 3. Lógica de Negocio (Backend - Python)

### 3.1. `mrp.cut.liquidation.line` (Lógica de Líneas)
*   Implementar métodos `@api.depends` u `@api.onchange` para todos los campos calculados (`difference_qty`, `final_marker_qty`, etc.).

### 3.2. `stock.move` (Lógica de Cabecera)
*   **Método `@api.depends` para `liquidation_visible`:**
    *   Obtendrá las categorías configuradas en `res.config.settings`.
    *   Verificará si la categoría del `product_id` (o alguna de sus categorías padre) está en la lista.
    *   Devolverá `True` o `False`.
*   **Método `action_open_cut_liquidation()`:**
    *   Método llamado por el botón.
    *   Devolverá una acción de ventana (`act_window`) apuntando a la vista de formulario de liquidación del `stock.move` actual (`res_id: self.id`).
*   **Métodos `@api.depends` para los campos de totales:**
    *   Sumarán los valores correspondientes de las `liquidation_line_ids`.
