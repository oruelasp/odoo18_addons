# ID: HU-MRP-002
# Título: Liquidación de Corte Detallada por Componente
**Versión:** 1.1

**Como** un Supervisor de Corte o Jefe de Producción,
**Quiero** acceder a una función de "Liquidación de Corte" directamente desde la línea de un componente elegible en una Orden de Producción,
**Para que** pueda registrar el consumo real a través de múltiples tendidos, visualizar la merma calculada, y usar esa información para **actualizar manualmente** el consumo y la producción de merma en la OP.

---
### Criterios de Aceptación:

*   **Dado que** un Administrador ha configurado las categorías de productos elegibles para liquidación,
    **Y que** estoy en la vista de formulario de una Orden de Producción,
    **Cuando** miro la pestaña "Componentes",
    **Entonces** al lado de cada línea de componente cuyo producto pertenezca a una categoría elegible, debe aparecer un nuevo botón de "Liquidación".

*   **Dado que** hago clic en el botón de "Liquidación" de una línea de componente,
    **Cuando** se abre el pop-up (vista de formulario),
    **Entonces** debo ver los detalles del componente (Producto, Demanda) en la cabecera y una sección de detalle para agregar una o más líneas de tendido.

*   **Dado que** ingreso los datos en una línea de tendido en el pop-up (como `Tendido Real`, `Trazo` y `Paños`),
    **Cuando** salgo de los campos numéricos,
    **Entonces** el sistema debe calcular y mostrar automáticamente el "Trazo Final", la "Cantidad de Merma" y la "Merma (%)" para esa línea y para el consolidado.

*   **Dado que** completo la liquidación y hago clic en "Guardar y Cerrar",
    **Entonces** el sistema debe guardar los datos de las líneas de liquidación para futuras consultas, **sin modificar automáticamente** la línea del subproducto de merma ni la cantidad consumida del componente.

*   **Dado que** he cerrado el pop-up de liquidación,
    **Cuando** voy a la pestaña "Subproductos",
    **Entonces** debo poder **ingresar manualmente la cantidad total de merma** calculada en la línea del subproducto correspondiente.

*   **Dado que** he cerrado el pop-up de liquidación,
    **Cuando** vuelvo a la pestaña "Componentes",
    **Entonces** debo poder **editar manualmente la cantidad consumida** en la línea del componente para que refleje el consumo real.

---
### Flujo de Trabajo del Usuario (Paso a Paso):

1.  El Jefe de Producción navega a la Orden de Producción de Corte.
2.  Va a la pestaña **"Componentes"** y hace clic en el icono de **"Liquidación de Corte"** en la fila del componente principal (ej. tela).
3.  Se abre un modal. El usuario hace clic en "Agregar una línea" para registrar el primer tendido.
4.  Ingresa los datos físicos (`Tendido Real`, `Nº de Paños`, `Trazo`, etc.) para esa línea. El sistema calcula la merma de la línea.
5.  Repite los pasos 3 y 4 para todos los tendidos necesarios.
6.  El sistema muestra la **Merma total resultante**. El usuario toma nota de este valor.
7.  Presiona **"Guardar y Cerrar"**. El modal se cierra, guardando los datos.
8.  El usuario navega a la pestaña **"Subproductos"** e **ingresa manualmente la cantidad de merma total** calculada.
9.  El usuario vuelve a la pestaña **"Componentes"** y **edita manualmente la cantidad en la columna "Consumido"**.
