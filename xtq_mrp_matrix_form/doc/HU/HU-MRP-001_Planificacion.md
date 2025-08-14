# HU-001: Planificar Cantidades Programadas usando Curva de Tallas
**Rol:** Jefe de Producción

## 1. Historia de Usuario
**Como** Jefe de Producción,
**Quiero**, después de configurar la matriz de Tonos y Tallas en una OP de Corte, utilizar un botón **"Recalcular Matriz"** que tome la cantidad total programada de la OP y la distribuya automáticamente en las celdas de "Cantidad Programada" de la matriz, basándose en la **proporción de la Curva de Tallas**,
**Para que** pueda establecer el plan de producción de forma rápida, precisa y sin cálculos manuales, asegurando que la distribución respete las proporciones comerciales.

## 2. Flujo de Trabajo (Paso a Paso)
1.  Abre una OP de Corte en estado **"Pendiente de Planificación"**. El campo "Cantidad" principal de la OP tiene un valor (ej. `1000`).
2.  Navega a la pestaña "Matriz de Producción".
3.  El sistema ha pre-poblado el eje Y (Tallas y su **Proporción de Curva**) desde el Programa de Ventas.
4.  El usuario añade los valores para el eje X (Tonos), por ejemplo: `'Tono 1'`, `'Tono 2'`.
5.  Hace clic en el botón **"Recalcular Matriz"** ubicado en la cabecera de la OP.
6.  El sistema ejecuta la lógica de distribución y actualiza los valores en las celdas de **"Cantidad Programada"** de la matriz.
7.  Realiza ajustes manuales finos en las celdas si es necesario.
8.  Hace clic en el botón **"Confirmar Planificación"** para bloquear la matriz y cederla al taller.

## 3. Criterios de Aceptación
-   **Dado** que el estado de la matriz es "Pendiente de Planificación", **entonces** las celdas de "Cantidad Programada" (`product_qty`) son editables y las de "Cantidad a Producir" (`qty_producing`) son de solo lectura.
-   Debe existir un botón "Recalcular Matriz" en el formulario de la OP.
-   **Cuando** hago clic en "Recalcular Matriz", **entonces** las celdas de "Cantidad Programada" deben poblarse con los valores correctos según la lógica de distribución.
-   **Cuando** hago clic en "Confirmar Planificación", **entonces** el estado de la matriz debe cambiar a "Planificación Confirmada", y los campos de "Cantidad Programada" deben volverse de solo lectura.