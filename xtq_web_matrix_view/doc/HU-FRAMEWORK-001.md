# HU-FRAMEWORK-001: Framework de Vista Matriz Editable Genérica
**Versión:** 1.0

## 1- Rol, Necesidad y Objetivo
**Como** un Desarrollador/Implementador de Odoo,
**Quiero** tener un nuevo tipo de vista (`matrix_editable`) que pueda definir en XML y aplicar a cualquier modelo,
**Para que** pueda crear rápidamente interfaces de edición masiva para diferentes procesos de negocio (producción, ventas, compras) sin tener que reescribir toda la lógica del frontend cada vez.

## 2- Criterios de Aceptación
* Dado que un desarrollador crea un nuevo módulo, Cuando añade `xtq_web_matrix_view` a sus dependencias, Entonces debe poder usar `view_mode="matrix_editable"` en sus acciones de ventana.
* Dado que se define una vista de tipo `matrix_editable` en XML, Cuando se especifica un `get_data_route`, `save_route` y otros atributos, Entonces el componente JavaScript debe usar estas rutas para comunicarse con el backend.
* Dado que la vista se carga, Cuando el método `get_data_route` devuelve datos, Entonces el `MatrixRenderer` debe ser capaz de dibujar una tabla genérica basada en las listas de filas, columnas y valores recibidos.
* Dado que un usuario edita una celda y guarda, Cuando el `MatrixController` llama al `save_route`, Entonces debe enviar un diccionario con los IDs de los registros y los nuevos valores para que el backend los procese. 