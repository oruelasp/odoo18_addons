# Diseño Funcional General - Addon `xtq_mrp_matrix_form`
**Versión:** 1.2

## 1. Propósito, Objetivo y Alcance

### 1.1. Propósito
Este addon está diseñado para resolver una brecha fundamental en la gestión de producción con variantes en Odoo, centralizando la planificación y ejecución de múltiples variantes (ej. Talla/Tono) en una única Orden de Producción (OP) a través de una interfaz de matriz dinámica.

### 1.2. Objetivo
El objetivo es proporcionar una herramienta visual e intuitiva dentro del formulario de la OP que permita a los usuarios definir, planificar y registrar la producción de cada combinación de atributos, simplificando la gestión masiva sin sacrificar la precisión del inventario y la trazabilidad a nivel de lote.

### 1.3. Alcance
- **EN ALCANCE:** Modificar la OP para incluir la matriz, permitir configuración de ejes desde el producto, desarrollar la lógica de "explosión" de la matriz para crear lotes con atributos, y manejar producciones parciales.
- **FUERA DE ALCANCE:** El proceso de creación inicial de las OPs, reportes personalizados basados en la matriz, y el addon `xtq_lot_attributes` (dependencia).

## 2. Restricciones y Variaciones

- **Restricción:** El addon está diseñado para matrices de dos dimensiones.
- **Variación (OP de Corte vs. OP de Prenda):** La lógica de finalización se adaptará. En una **OP de Corte**, creará lotes de un producto semielaborado con atributos. En una **OP de Prenda**, generará movimientos de inventario para las **variantes del producto terminado**.
- **Dependencia:** Este módulo requiere la instalación y correcta configuración del addon `xtq_lot_attributes`.
