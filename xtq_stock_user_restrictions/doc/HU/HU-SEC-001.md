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
