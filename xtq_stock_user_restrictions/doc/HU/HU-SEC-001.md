# HU-SEC-001: Configuración de Restricciones por Administrador

| Campo | Descripción |
| :--- | :--- |
| **Como un** | Administrador del Sistema |
| **Quiero** | poder configurar, en la ficha de cada usuario, una tabla de reglas que me permita asignar uno o más almacenes y, para cada uno, especificar la lista de tipos de operación que puede gestionar, |
| **Para que** | pueda asegurar que los operarios de almacén solo interactúen con las tareas que les corresponden, minimizando errores y simplificando su interfaz de trabajo. |

### Escenario de Aceptación

*   **Dado** que estoy logueado como Administrador.
*   **Y** navego a la ficha del usuario "John K." en `Configuración > Usuarios y Compañías > Usuarios`.
*   **Cuando** voy a la nueva pestaña "Restricciones de Inventario" y activo el checkbox "Activar Restricciones de Inventario".
*   **Y** añado una línea en la tabla de reglas con los siguientes valores:
    *   **Almacén Permitido:** "Planta Mariscal Nieto"
    *   **Tipos de Operación Permitidos:** "PRODUCCION MN: Salidas Internas"
*   **Y** guardo los cambios.
*   **Entonces** el sistema debe almacenar y aplicar estas reglas exclusivamente para el usuario "John K.", sin afectar a otros usuarios.

### Escenario de Aceptación Alternativo: Tipos de Operación sin Almacén

*   **Dado** que existen tipos de operación que no están asociados a ningún almacén (ej. "Control de Calidad Global").
*   **Y** estoy en la ficha del usuario "John K." con las restricciones activadas.
*   **Cuando** añado una nueva línea en la tabla de reglas, dejo el campo **"Almacén Permitido" en blanco**.
*   **Y** en la columna "Tipos de Operación Permitidos", selecciono "Control de Calidad Global".
*   **Y** guardo los cambios.
*   **Entonces** el sistema debe permitir a "John K." acceder únicamente a ese tipo de operación, además de las otras reglas que tenga configuradas.

---
**Nota Importante sobre la Lógica de las Reglas:** Para que una regla sea válida, debe tener o bien un **Almacén Permitido** o al menos un **Tipo de Operación Permitido**. No se pueden crear líneas completamente vacías.
