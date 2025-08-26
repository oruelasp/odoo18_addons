# HU-003: Finalizar Producción y Crear Lote Único

**Rol:** Jefe de Producción / Responsable de Calidad

## 1. Historia de Usuario

**Como** Responsable de Calidad o Jefe de Producción,
**Quiero** que al "Marcar como Hecho" una Orden de Producción con matriz, el sistema genere **un único Lote/Número de Serie** estándar,
**Para que** la trazabilidad se mantenga simple y directa, sabiendo que toda la información detallada de la producción (el desglose de la matriz) reside en la Orden de Producción de origen.

## 2. Flujo de Trabajo (Paso a Paso)

1.  Abre una OP cuyo estado de matriz sea "En Ejecución".
2.  Hace clic en el botón estándar **"Marcar como Hecho"**.
3.  Si el producto requiere seguimiento, Odoo invoca la creación del lote a través de `action_generate_serial`.
4.  Nuestra lógica intercepta este momento y crea **un único** `stock.lot` estándar, sin añadirle información adicional.
5.  La OP se asocia a este único lote.
6.  El flujo estándar de Odoo finaliza, la OP se marca como "Hecha" y el lote es registrado en el inventario.
7.  Posteriormente, si un usuario necesita conocer el desglose de la producción de ese lote, puede navegar desde el lote a su Orden de Producción de origen y consultar la pestaña "Matriz X,Y", que contiene toda la información detallada.

## 3. Criterios de Aceptación

-   **Dado** que tengo una OP con una matriz, **cuando** hago clic en "Marcar como Hecho", **entonces** el sistema debe crear **exactamente un** `stock.lot` estándar.
-   **Y** el `name` del `stock.lot` creado debe ser idéntico al `name` de la Orden de Producción de origen para facilitar la trazabilidad.
-   **Y** el `stock.lot` creado NO debe contener campos o tablas adicionales con el detalle de la matriz.
-   **Y** la trazabilidad hacia el detalle de la matriz se logra a través de la relación Lote -> Orden de Producción Origen.
-   **Y** la lógica para la creación del lote simple debe residir en la sobrescritura del método `action_generate_serial` de `mrp.production`.
-   **Y** el sistema NO debe crear Órdenes de Producción parciales.
