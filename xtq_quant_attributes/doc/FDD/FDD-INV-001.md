# FDD-INV-001: Visualización Avanzada de Atributos de Calidad en Selección de Lotes

## 1. Propósito y Alcance

El propósito de esta funcionalidad es **mejorar la usabilidad** del proceso de reserva de lotes (rollos de tela) en las transferencias de inventario. Se busca proporcionar al usuario una **visión consolidada y comparable de los atributos de calidad** de múltiples lotes en una sola pantalla.

El alcance se limita a modificar la interfaz de la ventana emergente de selección de inventario para productos específicos.

## 2. Arquitectura de la Solución: Extensión de Vista con Columnas Dinámicas

Se modificará el comportamiento de la ventana emergente ("Agregar una línea") en las Transferencias de Inventario.

-   **Activación Condicional:** La funcionalidad se activará **únicamente para productos que tengan un campo booleano "Mostrar Atributos de Calidad en Picking"** marcado en su plantilla (`product.template`).
-   **Inyección de Columnas (Frontend):** Cuando se active, un componente **JavaScript** interceptará la carga de la vista de lista de los `stock.quant` disponibles.
-   **Consulta de Datos (Backend):** El JavaScript realizará una única llamada al backend para obtener los valores de los atributos de calidad para todos los lotes visibles.
-   **Renderizado Dinámico:** El JavaScript **inyectará dinámicamente nuevas columnas** en la vista de lista para cada atributo relevante (Tono, Ancho, etc.) y poblará las celdas.

## 3. Brechas Técnicas y Desarrollos

-   **Desarrollo Menor/Medio:** Se requiere la creación de un componente JavaScript/OWL para extender el `ListRenderer` de Odoo y un método Python de soporte en el backend.

## 4. Próximos Pasos

El diseño técnico detallado se encuentra en la especificación `DEV-INV-001`.
