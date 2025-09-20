# Development Design Document (DEV) - Programa de Ventas

## 1. Arquitectura Técnica

El módulo `xtq_mrp_sales_program` introducirá nuevos modelos en la base de datos de Odoo para permitir la persistencia de los programas de venta. La arquitectura se basa en la conversión de los modelos transitorios del addon `mrp_mass_production_order` a modelos estándar (`models.Model`).

## 2. Modelo de Datos

Se crearán los siguientes modelos:

### 2.1. `sales.program` (Programa de Venta)

Hereda de `models.Model`. Este será el objeto principal.

| Nombre del Campo               | Tipo              | Descripción                                                                 | Atributos Clave                               |
| ------------------------------ | ----------------- | --------------------------------------------------------------------------- | --------------------------------------------- |
| `name`                         | `Char`            | N° de Programa, secuencia autogenerada.                                     | `required=True`, `copy=False`, `readonly=True`|
| `description`                  | `Char`            | Descripción del programa.                                                   |                                               |
| `state`                        | `Selection`       | Estado del workflow (`draft`, `approved`, `done`, `cancel`).                  | `default='draft'`, `required=True`            |
| `date_planned_start`           | `Datetime`        | Fecha de inicio planificada.                                                |                                               |
| `company_id`                   | `Many2one`        | Compañía.                                                                   | `default=lambda self: self.env.company`       |
| `line_ids`                     | `One2many`        | Líneas de artículos a producir (`sales.program.line`).                      |                                               |
| `production_ids`               | `One2many`        | Órdenes de Producción generadas (`mrp.production`).                         | `readonly=True`                               |
| `production_count`             | `Integer`         | Campo computado para el smart button de OPs.                                | `compute='_compute_production_count'`         |
| **Campos heredados del Wizard:** |                   |                                                                             |                                               |
| `picking_type_id`              | `Many2one`        | Tipo de Operación (`stock.picking.type`).                                   | `domain="[('code', '=', 'mrp_operation')]"`   |
| `location_src_id`              | `Many2one`        | Ubicación de Componentes (`stock.location`).                                |                                               |
| `location_dest_id`             | `Many2one`        | Ubicación de Productos Terminados (`stock.location`).                       |                                               |
| `tag_ids`                      | `Many2many`       | Etiquetas (`mrp.tag`) a aplicar a todas las OPs.                            |                                               |

### 2.2. `sales.program.line` (Línea de Programa de Venta)

Hereda de `models.Model`. Representa cada producto a fabricar.

| Nombre del Campo      | Tipo       | Descripción                           | Atributos Clave |
| --------------------- | ---------- | ------------------------------------- | --------------- |
| `program_id`          | `Many2one` | Referencia al programa de venta padre.  | `ondelete='cascade'` |
| `product_id`          | `Many2one` | Producto a fabricar (`product.product`).| `required=True` |
| `product_qty`         | `Float`    | Cantidad a fabricar.                  | `required=True` |
| `product_uom_id`      | `Many2one` | Unidad de Medida (`uom.uom`).         | `required=True` |
| `bom_id`              | `Many2one` | Lista de Materiales (`mrp.bom`).      |                 |
| `tag_ids`             | `Many2many`| Etiquetas específicas para esta línea.  |                 |

### 2.3. Extensión a `mrp.production`

Se añadirá un campo para la trazabilidad.

| Nombre del Campo      | Tipo       | Descripción                               |
| --------------------- | ---------- | ----------------------------------------- |
| `sales_program_id`    | `Many2one` | Vínculo al Programa de Venta de origen.   |

## 3. Lógica de Negocio (Métodos Principales)

*   **`sales.program`:**
    *   `_compute_production_count()`: Calcula el número de OPs en `production_ids`.
    *   `action_approve()`: Cambia el estado a `approved`.
    *   `action_generate_productions()`:
        *   Contendrá la lógica principal adaptada de `action_create` del wizard.
        *   Iterará sobre `self.line_ids`.
        *   Creará las `mrp.production` vinculándolas con `sales_program_id=self.id`.
        *   Cambiará el estado a `done`.
    *   `action_cancel()`: Cambia el estado a `cancel`.
    *   `action_draft()`: Resetea el estado a `draft`.
    *   `create()`: Sobrescrito para generar la secuencia `name`.

## 4. Estructura de Ficheros

```
xtq_mrp_sales_program/
├── __init__.py
├── __manifest__.py
├── doc/
│   ├── FDD.md
│   ├── HU.md
│   └── DEV.md
├── models/
│   ├── __init__.py
│   ├── sales_program.py
│   └── mrp_production.py (para la extensión)
├── security/
│   ├── ir.model.access.csv
│   └── sales_program_security.xml
└── views/
    └── sales_program_views.xml
```

## 5. Prácticas de Odoo v18

*   **Vistas:** Se utilizará la etiqueta `<list>` en lugar de `<tree>`.
*   **Atributos condicionales:** Se usarán atributos directos como `invisible="state == 'draft'"` en lugar de `attrs="{'invisible': [('state', '=', 'draft')]}"`.
*   **Campos computados:** Se usará `precompute=True` en campos `compute` no almacenados donde sea aplicable para mejorar el rendimiento de la UI.
