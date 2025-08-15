# HU-003: Finalizar Producción y "Explotar" Matriz
**Rol:** Jefe de Producción / Líder de Taller (Responsable de Cierre)

## 1. Historia de Usuario
**Como** Jefe de Producción o Líder de Taller,
**Quiero** hacer clic en un botón "Producir Lotes" en la Orden de Producción para que el sistema tome las cantidades registradas en "Cantidad a Producir" de la matriz,
**Para que** pueda ejecutar la producción masiva de todas las variantes de Tono y Talla de una sola vez, creando automáticamente los lotes con sus atributos correctos y, al finalizar, ver una lista de todas las órdenes de producción parciales que se generaron.

## 2. Flujo de Trabajo (Paso a Paso)
1. Abre una OP cuyo estado de matriz sea "En Ejecución" o `progress`.
2. Verifica que las cantidades en "Cantidad a Producir" de la matriz sean correctas.
3. Hace clic en el botón **"Producir Lotes"**.
4. El sistema ejecuta el proceso de "explosión" en segundo plano.
5. **Al finalizar la acción, el sistema redirige al usuario a la vista de lista de Órdenes de Producción, pre-filtrada para mostrar únicamente las nuevas MOs parciales que se acaban de crear como resultado de la producción.**
6. La matriz de la OP original se actualiza para reflejar las nuevas cantidades producidas.

## 3. Criterios de Aceptación
- **Dado** que tengo una OP con cantidades > 0 en las celdas de "Cantidad a Producir", **cuando** hago clic en "Producir Lotes", **entonces** el sistema debe crear un nuevo registro de Lote (`stock.lot`) por cada celda que se está produciendo.
- **Y** a cada lote nuevo se le deben asignar los atributos de Tono y Talla correspondientes (invocando a `xtq_attribute_lot`).
- **Y** el sistema debe registrar una producción (parcial o total), detallando la cantidad producida para cada lote específico.
- **Y** si la producción fue parcial, la OP principal debe permanecer abierta y crearse una OP residual.
- **Y** después de una ejecución exitosa, el sistema DEBE redirigir al usuario a una vista de lista que muestre las MOs parciales generadas.
