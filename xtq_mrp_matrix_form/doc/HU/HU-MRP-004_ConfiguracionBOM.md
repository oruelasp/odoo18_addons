---
### **Historia de Usuario (Versión Final)**

**ID:** `HU-MRP-004`
**Título:** Gestión de Componentes por Matriz de Atributos en la Lista de Materiales
**Módulo:** Fabricación / Listas de Materiales
**Rol de Usuario:** Analista de Diseño

#### **Declaración de la Historia**

**Como** un Analista de Diseño,
**Quiero** poder definir en la Lista de Materiales (BOM) una matriz de atributos (Talla/Color) y especificar para cada componente a qué combinación de atributos aplica,
**Para que** las Órdenes de Producción hereden esta lógica automáticamente, asegurando la consistencia de los datos y preparando el sistema para un registro de consumo preciso y por lotes.

#### **Contexto y Narrativa**
El proceso de negocio requiere que la Lista de Materiales (BOM) sea la fuente de verdad única que defina no solo *qué* componentes se usan, sino *cuándo* se usan, basándose en las características del producto final (como su talla y color). Esta configuración debe fluir de manera natural hacia la Orden de Producción (OP) para guiar el proceso de manufactura.

Este diseño centraliza la lógica de la "receta de producción" en la BOM, permitiendo una gestión más flexible y precisa de los componentes, independientemente de la estructura de variantes del producto final.

#### **Criterios de Aceptación (AC)**

*   **AC1:** Al crear una nueva BOM para un producto que tiene una "Configuración de Matriz de Producción" en su ficha, la BOM debe heredar y mostrar automáticamente estos atributos en su propia sección de configuración de matriz.
*   **AC2:** El Analista de Diseño debe poder editar los atributos de la matriz directamente en la BOM, independientemente de la configuración del producto.
*   **AC3:** Para cada línea de componente en la BOM, el Analista de Diseño debe poder seleccionar uno o varios valores de los atributos definidos en la matriz (ej. múltiples Tallas y/o múltiples Colores).
*   **AC4:** Al crear una Orden de Producción y seleccionar una BOM, la configuración de la "Matriz X,Y" en la OP **debe** poblarse desde la BOM, no desde la ficha del producto.
*   **AC5:** Al confirmar la OP, las líneas de movimiento de componentes (`stock.move`) **deben** contener la información de los atributos (Talla/Color) especificados en la línea de la BOM correspondiente.
*   **AC6:** La configuración base del sistema debe contemplar que los atributos `TALLA` y `COLOR` estén configurados con la opción **"Creación de variantes: Crear variantes"** para asegurar la compatibilidad con el framework de Odoo.

---

### **Especificación Funcional Detallada**

#### **A. Configuración General**
*   **Atributos:** Los atributos `TALLA` y `COLOR` deben existir en el sistema (`product.attribute`) y estar configurados con `Creación de variantes: Crear variantes`.

#### **B. Comportamiento en el Formulario del Producto (`product.template`)**
*   **Pestaña "Manufactura":** Existe una sección llamada "CONFIGURACIÓN DE MATRIZ DE PRODUCCIÓN".
*   **Campos:**
    *   `Atributo Matriz (Eje X, Filas)`: Un campo para seleccionar un `product.attribute`.
    *   `Atributo Matriz (Eje Y, Columnas)`: Un campo para seleccionar un `product.attribute`.
*   **Propósito:** Esta configuración actúa como el **valor por defecto** que se propondrá al crear una nueva Lista de Materiales para este producto.

#### **C. Comportamiento en la Lista de Materiales (`mrp.bom`)**
*   **Nueva Pestaña: "Configuración de Matriz"**
    *   Esta pestaña contendrá dos campos para definir los ejes de la matriz de la BOM:
        *   `Atributo Fila`: `Many2one` a `product.attribute`.
        *   `Atributo Columna`: `Many2one` a `product.attribute`.
*   **Lógica de Herencia:** Al crear una nueva BOM o al cambiar el producto en una BOM existente, el sistema deberá copiar automáticamente la configuración de la matriz desde la ficha del producto a los campos correspondientes en esta pestaña. Estos campos permanecerán editables.

#### **D. Comportamiento en las Líneas de Componentes de la BOM (`mrp.bom.line`)**
*   **Nuevas Columnas en la Lista de Componentes:**
    *   **`Valores Fila (ej. Color)`:** Un campo `Many2many` a `product.attribute.value` con el widget `many2many_tags`.
    *   **`Valores Columna (ej. Talla)`:** Un campo `Many2many` a `product.attribute.value` con el widget `many2many_tags`.
*   **Lógica de Dominio Dinámico:**
    *   El campo `Valores Fila` solo permitirá seleccionar valores que pertenezcan al atributo definido como "Atributo Fila" en la cabecera de la BOM.
    *   El campo `Valores Columna` solo permitirá seleccionar valores que pertenezcan al atributo definido como "Atributo Columna" en la cabecera de la BOM.

#### **E. Comportamiento en la Orden de Producción (`mrp.production`)**
*   **Lógica de Herencia de Matriz:**
    *   Al seleccionar una Lista de Materiales (BOM) en una OP, el sistema **deberá** leer la "Configuración de Matriz" (`Atributo Fila` y `Atributo Columna`) de la **BOM seleccionada** y poblar automáticamente la pestaña "Matriz X,Y" de la OP con esa información. La configuración de la ficha del producto debe ser ignorada en este punto.

#### **F. Comportamiento en las Líneas de Movimiento de la OP (`stock.move`)**
*   **Herencia de Atributos de Componente:**
    *   Al confirmar la OP, el sistema crea las líneas de movimiento (`stock.move`) para cada componente.
    *   Durante este proceso, el sistema **deberá** copiar los valores de `Valores Fila (ej. Color)` y `Valores Columna (ej. Talla)` desde cada `mrp.bom.line` a campos personalizados equivalentes en el `stock.move` correspondiente.
*   **Campos Requeridos en `stock.move`:**
    *   `Valores Fila Aplicables`: Campo `Many2many` a `product.attribute.value`.
    *   `Valores Columna Aplicables`: Campo `Many2many` a `product.attribute.value`.
