# Documento de Diseño Funcional (FDD) - Revisado

| **Código** | **Título** |
| :--- | :--- |
| `FDD-INV-001` | Arquitectura para la Creación Asistida de Transferencias desde OPs |

---

## 1. Propósito y Alcance

El propósito de esta funcionalidad es **optimizar drásticamente** el proceso de creación de transferencias manuales (ej. Entradas de Inventario desde producción) que están vinculadas a Órdenes de Producción. Se busca eliminar la digitación manual del producto terminado y sus cantidades, reducir errores y asegurar una trazabilidad completa entre la logística y la producción.

---

## 2. Arquitectura de la Solución: Asistente de Importación

Se desarrollará un **asistente (wizard) de una sola ventana**. Un botón de activación (`"Importar desde OP"`) será visible en el formulario de Transferencia de Inventario **únicamente cuando el registro se encuentre en estado 'Borrador'**.

Este wizard permitirá al usuario:

- **Seleccionar** una única Orden de Producción (OP) de una lista filtrada por estados relevantes (confirmado, en progreso, etc.).
- **Seleccionar** opcionalmente una Orden de Trabajo específica de esa OP.
- **Visualizar** el producto terminado de la OP, su cantidad programada (informativa) y ajustar la cantidad ejecutada (lo que realmente se produjo).
- **Poblar o añadir** una línea a la transferencia con el producto y cantidad seleccionados.
- **Propagar** datos de trazabilidad clave como el Documento Origen, el origen de la Orden de Trabajo y el Proyecto.

---

## 3. Brechas Técnicas y Desarrollos

- **Desarrollo Menor:** Se modificará el `TransientModel` (wizard) existente y la lógica asociada para cumplir con los requerimientos detallados en la Historia de Usuario `HU-INV-001`.

---

## 4. Próximos Pasos

El diseño detallado, el flujo de usuario y los criterios de aceptación para este desarrollo se encuentran especificados en la siguiente Historia de Usuario:
- **`HU-INV-001`**: *Creación Asistida de Transferencias desde Órdenes de Producción*.
