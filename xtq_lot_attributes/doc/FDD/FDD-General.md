# Documento de Diseño Funcional (FDD)

| **Código** | **Título** |
| :--- | :--- |
| `FDD-INV-002` | Arquitectura para el Registro de Atributos en Lotes/Nº de Serie |

---

## 1. Propósito y Alcance

El propósito de esta funcionalidad es **extender el modelo de datos de Lotes/Nº de Serie (`stock.lot`)** para permitir el registro estructurado de información específica y variable que caracteriza a cada lote. Actualmente, Odoo no ofrece una forma nativa de registrar atributos detallados (como especificaciones técnicas, mediciones de calidad o características de producción) a nivel de lote.

Esta solución busca cerrar esa brecha, proporcionando una **herramienta flexible y escalable** para capturar estos datos críticos, mejorando la trazabilidad y proporcionando información vital para los procesos de calidad y producción.

---

## 2. Arquitectura de la Solución: Reutilización de Modelos Nativos

La solución se basa en **heredar y extender la funcionalidad existente de Odoo**, evitando la creación de estructuras de datos redundantes.

-   **Reutilización del Modelo de Atributos:** En lugar de crear un nuevo maestro de atributos, se reutilizará el modelo nativo `product.attribute`. Esto garantiza consistencia y permite una gestión centralizada.
-   **Extensión del Modelo de Lotes:** Se añadirá una relación `One2many` al modelo `stock.lot` para vincularlo a un nuevo modelo que contendrá las líneas de atributos.
-   **Nuevo Modelo de Líneas:** Se creará un nuevo modelo, `stock.lot.attribute.line`, que servirá como tabla intermedia para almacenar cada par "Atributo-Valor" asociado a un lote específico.
-   **Interfaz de Usuario Integrada:** Se añadirá una nueva pestaña en el formulario de Lote/Nº de Serie para permitir un registro de datos intuitivo y centralizado.
-   **Menú de Configuración:** Se creará un nuevo menú en la configuración de Inventario para el mantenimiento global de todas las líneas de atributos registradas.

---

## 3. Brechas Técnicas y Desarrollos

-   **Desarrollo Menor:** Se creará un nuevo addon de Odoo (`xtq_lot_attributes`) que contendrá:
    *   Un nuevo modelo (`stock.lot.attribute.line`).
    *   Extensiones (herencias) de los modelos `stock.lot` y `product.attribute`.
    *   Vistas XML para integrar la nueva funcionalidad en la interfaz de Odoo.
    *   Reglas de seguridad para el nuevo modelo.

---

## 4. Próximos Pasos

El diseño detallado, el flujo de usuario y los criterios de aceptación para este desarrollo se encuentran especificados en la siguiente Historia de Usuario:
-   **`HU-INV-002`**: *Registro y Consulta de Atributos Específicos en Lotes/Nº de Serie*.
