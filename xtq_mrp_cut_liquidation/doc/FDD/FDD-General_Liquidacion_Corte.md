# Diseño Funcional General - Addon `xtq_mrp_cut_liquidation`
**Versión:** 1.1

### 1. Propósito, Objetivo y Alcance

*   **1.1. Propósito:**
    Este addon está diseñado para proporcionar una herramienta de asistencia al proceso de Liquidación de Corte. Su función es capturar los datos físicos de múltiples tendidos por componente y calcular automáticamente la merma resultante, sirviendo como una calculadora integrada y un registro detallado de la operación.

*   **1.2. Objetivo:**
    El objetivo es eliminar la necesidad de cálculos manuales de merma y proporcionar un registro auditable de los datos de cada liquidación. La herramienta asistirá al usuario, quien mantendrá el control final sobre la actualización de los registros de consumo y producción de subproductos en la Orden de Producción.

*   **1.3. Alcance:**
    *   **EN ALCANCE:** Añadir un botón de "Liquidación" a las líneas de componentes de las categorías configuradas. Abrir una vista de formulario para registrar múltiples líneas de liquidación (tendidos). Realizar el cálculo automático de la merma por línea y total. Guardar los datos de la liquidación en un nuevo modelo. Añadir una pantalla de configuración en los Ajustes de Manufactura.
    *   **FUERA DE ALCANCE:** La actualización automática de las cantidades consumidas (`stock.move`) y de las cantidades de subproductos. La generación de reportes de liquidación.

### 2. Restricciones y Variaciones

*   **Restricción:** La funcionalidad es invocada desde un `stock.move` en el contexto de `mrp.production`. La visibilidad del botón de acción dependerá de la configuración de categorías de producto.
*   **Decisión del Usuario:** La responsabilidad de transcribir la merma calculada y el consumo real a los campos correspondientes de la MO recae explícitamente en el usuario, garantizando un control manual y consciente.
*   **Arquitectura:** Se utilizará un modelo de datos persistente para las líneas de liquidación, vinculado al `stock.move` a través de una relación `One2many`, en lugar de un `TransientModel` (wizard).
