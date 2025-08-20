# HU-MRP-003: Finalizar Producción desde Matriz

## 1. Rol e Interés

| Rol | Interés |
| :--- | :--- |
| Jefe de producción / Líder de taller | Necesita finalizar la producción registrada, asegurando que se generen los lotes correctos con sus atributos de Tono y Talla, y que el inventario se actualice de manera precisa. |

## 2. Historia de Usuario

**Como** planificador de producción,
**quiero** poder finalizar el registro de las cantidades producidas en la matriz,
**para** que el sistema divida la orden de producción principal, genere lotes con atributos específicos para cada nueva orden, y prepare todo para el registro final de consumo e inventario.

## 3. Flujo de Trabajo (Proceso Actualizado)

El proceso de finalización ahora se realiza en dos etapas claras:

### Etapa 1: División de la Orden de Producción

1.  El usuario abre una Orden de Producción (OP) que ya ha sido planificada y se encuentra en estado de matriz `En Progreso`.
2.  El usuario ha registrado las cantidades realmente producidas en el campo `Cantidad a Producir` de cada celda de la matriz.
3.  El usuario hace clic en el botón **"Dividir por Matriz"**.
4.  **El sistema realiza las siguientes acciones:**
    *   Valida que la suma de las cantidades en la matriz no supere la cantidad total de la OP.
    *   Calcula la cantidad "residual" (diferencia entre el total de la OP y el total de la matriz).
    *   La **OP original** se actualiza y su cantidad a producir se reduce a la cantidad residual. **No se cancela**. Su matriz se limpia y su estado de matriz pasa a `Realizado`.
    *   Por cada celda con cantidad en la matriz, se crea una **nueva Orden de Producción (backorder)** con esa cantidad específica.
    *   A cada nueva OP se le crea y asigna un único **Lote/Número de Serie** para el producto terminado.
    *   A cada Lote se le asignan los **atributos de Tono y Talla** correspondientes a su celda de origen en la matriz.
    *   Las nuevas OPs se confirman y se dejan en estado "Confirmado" o "En Progreso", listas para la producción.
5.  **Resultado:** El sistema redirige al usuario a una vista de lista que muestra todas las nuevas OPs que se han creado. La OP original ahora solo representa el saldo pendiente de producir.

### Etapa 2: Finalización de las Órdenes Individuales

1.  Desde la vista de lista, el usuario ahora puede gestionar cada nueva OP de forma independiente.
2.  El usuario abre una de las nuevas OPs.
3.  El sistema, a través de la lógica estándar de Odoo, requerirá que el usuario especifique los lotes de los componentes (ej. el lote de la tela) que se consumieron para producir este lote específico de producto terminado.
4.  Una vez registrado el consumo, el usuario hace clic en el botón estándar **"Realizado"**.
5.  **El sistema finaliza la OP**, mueve el lote del producto terminado al inventario y cierra el proceso para esa orden específica.
6.  Este proceso se repite para cada una de las OPs divididas.

## 4. Criterios de Aceptación

*   **[CA-FIN-001]** El botón "Dividir por Matriz" solo debe ser visible cuando el estado de la matriz sea `En Progreso`.
*   **[CA-FIN-002]** El sistema debe impedir la división si la suma de las cantidades de la matriz es mayor que la cantidad a producir de la OP original.
*   **[CA-FIN-003]** La OP original debe permanecer activa y su cantidad debe ser igual a la diferencia entre su cantidad original y el total de la matriz.
*   **[CA-FIN-004]** Se debe crear una nueva OP por cada celda de la matriz con una cantidad mayor a cero.
*   **[CA-FIN-005]** Cada nueva OP debe tener un lote de producto terminado único.
*   **[CA-FIN-006]** Cada lote generado debe tener los atributos de Tono (fila) y Talla (columna) correctos, heredados de la matriz.
*   **[CA-FIN-007]** Después de la división, el usuario debe ser redirigido a una vista de lista que muestre solo las nuevas OPs creadas.
*   **[CA-FIN-008]** Las nuevas OPs no deben tener ninguna configuración de matriz, comportándose como OPs estándar.
*   **[CA-FIN-009]** Al intentar finalizar una de las nuevas OPs, el sistema debe solicitar (si aplica) el consumo de componentes con seguimiento por lote/serie.
