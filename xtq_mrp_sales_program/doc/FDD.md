# Functional Design Document (FDD) - Programa de Ventas

## 1. Visión General

Este documento describe el diseño funcional del módulo **Programa de Ventas** (`xtq_mrp_sales_program`). El objetivo es proporcionar una herramienta en Odoo para que la empresa Brandint pueda registrar sus proyecciones de demanda interna, gestionarlas a través de un flujo de aprobación y generar las Órdenes de Producción (OPs) correspondientes de forma masiva.

Esta funcionalidad reemplaza el proceso manual realizado en plantillas externas y se basa en la lógica del módulo `mrp_mass_production_order`, pero transformándola de un asistente a un modelo persistente con un ciclo de vida propio.

## 2. Actores y Roles

*   **Planificador de Producción:** Usuario principal. Responsable de crear, editar y solicitar la aprobación de los programas de venta.
*   **Gerente de Producción:** Usuario con permisos para aprobar o rechazar programas de venta y autorizar la generación de OPs.

## 3. Flujo de Proceso (Workflow)

El programa de venta seguirá un flujo de estados simple:

1.  **Borrador (`draft`):** Estado inicial. El programa puede ser modificado libremente.
2.  **Aprobado (`approved`):** El programa ha sido revisado y aceptado. En este estado, ya no se pueden modificar las líneas de producción. Desde aquí se pueden generar las OPs.
3.  **Finalizado (`done`):** Las OPs asociadas han sido generadas. El registro es de solo lectura.
4.  **Cancelado (`cancel`):** El programa ha sido anulado y no se puede procesar.

![Workflow](https://i.imgur.com/your-workflow-diagram.png)  <!-- Placeholder for a real diagram -->

## 4. Diseño de la Interfaz de Usuario (UI)

La interfaz se compondrá de las siguientes vistas:

### 4.1. Vista de Lista (List View)

Mostrará un resumen de todos los programas de venta con columnas clave:
*   N° de Programa
*   Descripción
*   Año/Marca
*   Fecha de Registro
*   Estado (con un badge de color)

### 4.2. Vista de Formulario (Form View)

Será la vista principal para la interacción con el registro.

*   **Cabecera:** Contendrá un `statusbar` para visualizar el estado y los botones de acciones (`Aprobar`, `Generar OPs`, `Cancelar`, `Resetear a Borrador`).
*   **Campos Principales:**
    *   N° de Programa, Año/Marca, Descripción, Temporada, etc. (basados en la imagen provista).
    *   Campos técnicos heredados del wizard: Tipo de Operación, Ubicación de Componentes y Ubicación de Productos Terminados.
*   **Pestañas (Notebook):**
    *   **Artículos a Producir:** Una vista de lista editable (`One2many`) para las líneas del programa (`sales.program.line`). Cada línea permitirá especificar el producto, la cantidad total, la BoM y las `tags`.
    *   **Órdenes de Producción:** Una vista de lista (`One2many` de solo lectura) que mostrará las OPs generadas a partir de este programa.

### 4.3. Smart Buttons

*   Un "smart button" en la parte superior del formulario mostrará el número de OPs generadas y permitirá navegar directamente a ellas.

## 5. Lógica de Negocio Detallada

*   **Creación de OPs:** El botón "Generar OPs" ejecutará una función que replicará la lógica de `action_create` del wizard original. Por cada registro en el `One2many` "Artículos a Producir", se creará una `mrp.production`.
*   **Trazabilidad:** Se añadirá un campo `Many2one` en el modelo `mrp.production` llamado `sales_program_id` para vincularlo con su programa de origen.
*   **Seguridad:** Se crearán dos grupos de seguridad: "Usuario de Programa de Ventas" y "Manager de Programa de Ventas". El acceso a los botones y la edición de registros en ciertos estados estará restringido por estos grupos.

## 6. Integración

*   **MRP:** El módulo se integra directamente con `mrp.production` para la creación de OPs.
*   **Stock:** Utiliza `stock.location` y `stock.picking.type` para la gestión de ubicaciones y operaciones.
*   **Product:** Se basa en `product.product` para la selección de artículos a fabricar.
*   **MRP Tags:** Depende de `mrp_tag` para permitir el etiquetado de las OPs generadas.
