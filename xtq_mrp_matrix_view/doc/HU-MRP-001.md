# HU-MRP-001: Panel de Planificación de Corte para Lotes de Producción
**Versión:** 2.0

## Título: Panel de Planificación de Corte para Lotes de Producción

### Rol, Necesidad y Objetivo

**Como** un Jefe de Producción,
**Quiero** invocar una vista de matriz interactiva desde las Órdenes de Producción de Corte,
**Para que** pueda visualizar y editar masivamente las cantidades a producir, organizadas por los atributos de lote **"Tono"** y **"Talla Cortada"**, optimizando mi planificación.

## Criterios de Aceptación

* **Dado que** he filtrado las MOs de Corte por un "Documento Origen", **Cuando** activo la "Vista Matriz", **Entonces** el sistema debe cargar una cuadrícula usando los valores del atributo de lote "Tono" para las filas y "Talla Cortada" para las columnas.

* **Dado que** la matriz está cargada, **Cuando** edito la cantidad en una celda, **Entonces** los totales deben actualizarse en tiempo real.

* **Dado que** hago clic en "Acciones > Recalcular Cantidades", **Cuando** se ejecuta la acción, **Entonces** debe aparecer un modal mostrando los datos del picking y la producción sugerida.

* **Dado que** confirmo el recálculo, **Cuando** se procesa la confirmación, **Entonces** el sistema debe redistribuir la nueva cantidad en todas las celdas de la matriz.

* **Dado que** hago clic en "Guardar", **Cuando** se ejecuta la acción de guardado, **Entonces** el sistema debe actualizar las cantidades `product_qty` en las MOs de Corte correspondientes a cada celda.

---

**Autor:** Omar Ruelas Principe – XTQ GROUP 