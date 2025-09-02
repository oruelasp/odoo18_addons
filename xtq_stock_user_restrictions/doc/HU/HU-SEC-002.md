# HU-SEC-002: Experiencia del Usuario de Almacén Restringido

| Campo | Descripción |
| :--- | :--- |
| **Como un** | Operario de Almacén con acceso restringido |
| **Quiero** | que la interfaz de Odoo me muestre automáticamente solo los tipos de operación (en el resumen) y las listas de transferencias que pertenecen a mi almacén y responsabilidades asignadas, |
| **Para que** | pueda trabajar de manera más rápida y segura, sin la distracción o el riesgo de procesar un documento de otra planta por error. |

### Escenario de Aceptación

*   **Dado** que mi Administrador ha configurado mi usuario para ver únicamente el Almacén "Planta Mariscal Nieto" y el Tipo de Operación "Salidas Internas".
*   **Cuando** me logueo en Odoo y navego al módulo de `Inventario`.
*   **Entonces**, en el "Resumen General", la única tarjeta de operación que debo ver es la de "Salida Interna: Planta Mariscal Nieto".
*   **Y cuando** navego a `Operaciones > Transferencias`, la lista solo debe mostrarme los pickings cuyo tipo de operación sea "Salida Interna: Planta Mariscal Nieto".
*   **Pero cuando** abro uno de esos pickings de salida y edito el campo "Ubicación de Destino", **SÍ** debo poder ver en la lista y seleccionar una ubicación que pertenezca a la "Planta Santa Lucía".
