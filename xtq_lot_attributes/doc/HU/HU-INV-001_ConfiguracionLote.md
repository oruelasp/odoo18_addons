# Historia de Usuario (HU)

| **ID** | **Título** |
| :--- | :--- |
| `HU-INV-002` | Registro y Consulta de Atributos Específicos en Lotes/Nº de Serie |

---

**Como un** Gerente de Calidad / Almacén,
**Quiero** configurar qué atributos son relevantes para los lotes y luego registrar los valores específicos de esos atributos para cada lote que ingresa,
**Para que** pueda mantener una trazabilidad detallada de las características de mi inventario y facilitar la consulta de esta información a otros departamentos.

---

## Flujo Detallado del Usuario (Workflow)

#### **Parte 1: Configuración (Realizada una sola vez por un Administrador)**

1.  **Inicio:** El usuario Administrador de Inventario navega a `Inventario > Configuración > Productos > Atributos`.
2.  **Creación/Edición de Atributo:** Crea un nuevo atributo (ej. "Tonalidad") o edita uno existente.
3.  **Marcado para Lotes:** Activa la nueva casilla booleana **"Es un Atributo de Lote"**. Esto designa el atributo como elegible para ser usado en el control de lotes.
4.  **Definición de Valores:** En la pestaña "Valores del Atributo", añade los posibles valores que este puede tomar (ej. "Tono A", "Tono B", "Tono C").
5.  Repite el proceso para todos los atributos necesarios (ej. "Ancho Real", "% Encogimiento", etc.).

#### **Parte 2: Registro de Datos (Realizado día a día por un Usuario de Inventario)**

1.  **Inicio:** El usuario recibe un nuevo producto con seguimiento por lote (ej. un rollo de tela).
2.  **Acceso al Lote:** Navega a `Inventario > Productos > Lotes/Nº de Serie` y crea un nuevo registro de lote o abre uno existente.
3.  **Navegación:** Hace clic en la nueva pestaña **"Atributos"** dentro del formulario del lote.
4.  **Añadir Atributo:** Hace clic en "Añadir una línea".
5.  **Selección de Atributo:** En la columna "Atributo", se despliega una lista que **únicamente** muestra los atributos que fueron marcados como "Es un Atributo de Lote" en la configuración. El usuario selecciona "Tonalidad".
6.  **Selección de Valor:** En la columna "Valor", se despliega una lista que **únicamente** muestra los valores asociados al atributo "Tonalidad" (ej. "Tono A", "Tono B", "Tono C"). El usuario selecciona el valor correspondiente.
7.  **Repetición:** Repite los pasos 4-6 para todos los demás atributos medidos para ese lote.
8.  **Guardado:** Guarda el formulario del lote. La información de los atributos queda permanentemente asociada a ese lote.

---

## Reglas de Negocio y Lógica

-   **Filtrado de Atributos:** El campo `attribute_id` en las líneas de atributos de lote debe tener un `domain` que filtre por `is_lot_attribute == True`.
-   **Filtrado de Valores:** El campo `value_id` debe tener un `domain` dinámico que filtre los valores basándose en el `attribute_id` seleccionado en la misma línea.
-   **Unicidad:** No se puede añadir el mismo `attribute_id` dos veces al mismo `lot_id`. Se debe implementar una `_sql_constraints` en el modelo `stock.lot.attribute.line`.
-   **Integridad de Maestros:** Desde la pestaña "Atributos" en el formulario del lote, los usuarios **no deben poder** crear ni editar atributos o valores. Se debe implementar con `options="{'no_create': True, 'no_open': True}"` en la vista.

---

## Criterios de Aceptación (Acceptance Criteria)

-   **Dado que** voy a la configuración de un Atributo, **entonces** debe existir una casilla "Es un Atributo de Lote".
-   **Dado que** estoy en el formulario de un Lote, **cuando** añado una línea en la pestaña "Atributos", **entonces** el campo "Atributo" solo debe mostrar aquellos con la casilla "Es un Atributo de Lote" activada.
-   **Dado que** selecciono un Atributo en una línea, **cuando** hago clic en "Valor", **entonces** la lista de valores debe corresponder únicamente a ese atributo.
-   **Dado que** intento añadir el atributo "Tonalidad" por segunda vez al mismo lote, **cuando** guardo, **entonces** el sistema debe mostrar un error de validación indicando que el atributo ya existe.
-   **Dado que** soy un usuario de inventario, **cuando** navego al nuevo menú en `Inventario > Configuración > Productos > Líneas de Atributos de Lote`, **entonces** puedo ver una lista de todas las líneas de atributos registradas en el sistema.
