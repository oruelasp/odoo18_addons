# Especificación Técnica - Addon `xtq_mrp_matrix_form`
**Versión:** 1.2

## 1. Modelo de Datos

### 1.1. `product.template` (Plantilla de Producto)
Se añadirán los siguientes campos para la configuración de la matriz:
- `matrix_attribute_x_id`: `Many2one` a `product.attribute` (Atributo para el eje X).
- `matrix_attribute_y_id`: `Many2one` a `product.attribute` (Atributo para el eje Y).

### 1.2. `mrp.production` (Orden de Producción)
- `matrix_state`: `Selection` con los valores: `[('pending', 'Pendiente'), ('planned', 'Programada'), ('progress', 'Ejecutado'), ('done', 'Realizado')]`. Default: `'pending'`.
- `matrix_x_value_ids`: `Many2many` a `product.attribute.value` (Valores seleccionados para el eje X).
- `matrix_y_value_ids`: `Many2many` a `product.attribute.value` (Valores para el eje Y).
- `matrix_curve_ids`: `One2many` al nuevo modelo `mrp.production.curve.line`.
- `matrix_line_ids`: `One2many` al modelo `mrp.production.matrix.line`.

### 1.3. `mrp.production.curve.line` (Nuevo Modelo)
- `production_id`: `Many2one` a `mrp.production`.
- `attribute_value_id`: `Many2one` a `product.attribute.value` (La Talla).
- `proportion`: `Integer` (La proporción de la curva).

### 1.4. `mrp.production.matrix.line` (Línea de Matriz)
- `product_qty`: `Float` (**Cantidad Programada**).
- `qty_producing`: `Float` (**Cantidad a Producir Ahora**).
- `production_id`, `x_attribute_value_id`, `y_attribute_value_id`: Relaciones.

## 2. Vistas (XML) y Componente Web (JS/OWL)

### 2.1. `mrp_production_views.xml`
- Añadir el campo `matrix_state` como un `statusbar` en la cabecera.
- Añadir los botones "Recalcular Matriz" y "Confirmar Planificación".
- Añadir la configuración de la matriz en una sección de la cabecera.
- La pestaña "Matriz" contendrá el widget que mostrará la matriz.

### 2.2. Widget JS/OWL (Brecha 1 - Frontend)
El componente JavaScript/OWL (`production_matrix_widget.js` y `.xml`) deberá ser desarrollado para cumplir con los siguientes requerimientos visuales y funcionales:

- **Doble Cabecera de Columnas:**
    - La cabecera de la matriz (`<thead>`) deberá renderizar **dos filas (`<tr>`)**.
    - La **primera fila** mostrará los nombres de los valores del eje Y (ej. "Talla 28", "Talla 30", etc.).
    - La **segunda fila**, directamente debajo de la primera, mostrará la proporción de la curva de tallas correspondiente a cada columna (ej. "4", "4", "2"). El método `get_matrix_data` del backend deberá proveer esta información.

- **Estructura de la Celda de Datos:**
    - Cada celda (`<td>`) de la matriz que representa una combinación de atributos deberá renderizar una estructura visual que muestre ambos valores: la cantidad a producir y la cantidad programada.
    - El formato visual sugerido es: `[Campo de entrada editable para qty_producing] / [Texto de solo lectura para product_qty]`.
    - Ejemplo: `_ / 100`. El guion bajo representa el campo de entrada.

- **Control de Edición Dinámico:**
    - La capacidad de editar los campos `product_qty` (en la fase de planificación) y `qty_producing` (en la fase de ejecución) debe ser controlada dinámicamente.
    - El widget recibirá el valor del campo `matrix_state` del registro principal y aplicará la lógica de `readonly` a los campos correspondientes basándose en este estado.

## 3. Lógica de Negocio (Backend - Python)

### 3.1. Botón "Recalcular Matriz" (Brecha 2)
- **Método:** `action_recalculate_matrix()` en `mrp.production`.
- **Lógica:**
    1. Lee `self.product_qty`.
    2. Lee los valores del eje X (`matrix_x_value_ids`).
    3. Lee la curva de tallas de `matrix_curve_ids`.
    4. Ejecuta la distribución en dos pasos: divide la cantidad total entre el número de filas de eje X (ejemplo: tonos), y luego distribuye ese resultado para cada fila según la proporción de la curva.
    5. Actualiza los valores de `product_qty` en los registros `matrix_line_ids`.

### 3.2. Botón "Confirmar Planificación"
- **Método:** `action_confirm_planning()`
- **Lógica:** Cambia el estado `matrix_state` a `'planned'`.
- **Edición:** Al cambiar el estado ningún campo de `product_qty` en la matriz puede ser editable. Y el que debe ser editable desde ese momento es `qty_producing`

### 3.3. Botón "Producir Lotes" (Brecha 3)
- **Método:** `action_produce_lots()`
- **Lógica:**
    1. Itera sobre las líneas de la matriz donde `qty_producing > 0`.
    2. Para cada línea, llama al método nativo `self.action_generate_serial()` para crear un `stock.lot`.
    3. Asigna los atributos de Tono y Talla a este lote utilizando `xtq_attribute_lot`.
    4. Crea los registros `stock.move.line` para detallar la producción de cada lote.
    5. Llama al método `button_mark_done()` de Odoo.
    6. Devuelve una `action` que redirige a la vista de lista de las MOs parciales generadas.

## 4. Brechas Técnicas a Resolver

- **Brecha 1: Widget de Matriz (Desarrollo Principal):** Crear un componente JS/OWL que renderice la matriz de doble cabecera, la estructura de celda `[a producir] / [programado]`, y controle la edición dinámica según el estado `matrix_state`.
- **Brecha 2: Lógica de Recálculo (Backend):** Crear la función Python para la regla de tres de la curva de tallas.
- **Brecha 3: Lógica de "Explosión" de Lotes (Backend):** Desarrollar el método Python para el botón "Producir Lotes", asegurando la reutilización de `action_generate_serial`.
- **Brecha 4: Control de Estados:** Implementar el campo `matrix_state` y la lógica de los botones para gestionar su transición.