# Historia de Usuario (HU) - Programa de Ventas

**ID:** HU-001
**Título:** Creación y Gestión de Programas de Venta para Proyección de Demanda

**Como:** Planificador de Producción,
**Quiero:** Registrar un "Programa de Ventas" que contenga una proyección de la demanda por producto, color y talla,
**Para:** Poder generar órdenes de producción masivas y anticipar las necesidades de material.

---

### Criterios de Aceptación:

1.  **Creación del Programa de Venta:**
    *   El sistema debe permitir crear un nuevo registro de "Programa de Venta".
    *   El formulario debe incluir campos de cabecera como:
        *   N° de Programa (secuencia autoincremental)
        *   Año/Marca (relación a un modelo existente o campo de texto)
        *   Descripción
        *   Temporada
        *   Fecha de Registro
        *   Mes/Año de Venta
    *   El formulario debe tener un estado inicial de "Borrador".

2.  **Detalle de Artículos y Curva de Tallas/Colores:**
    *   Debe existir una sección para añadir líneas de artículos (productos a fabricar).
    *   Para cada artículo, se debe poder definir una matriz o detalle de "Colores/Tallas".
    *   Cada línea en el detalle de "Colores/Tallas" representará una futura Orden de Producción y debe contener:
        *   Color
        *   Cantidad a producir
        *   Lista de Materiales (BoM) asociada.

3.  **Flujo de Aprobación:**
    *   El programa de venta debe tener los siguientes estados: `Borrador`, `Aprobado`, `Finalizado`, `Cancelado`.
    *   Un usuario con permisos puede mover el programa de "Borrador" a "Aprobado".
    *   Un programa "Aprobado" no puede ser modificado en sus líneas de detalle.

4.  **Generación de Órdenes de Producción (OPs):**
    *   Desde un programa "Aprobado", debe existir un botón para "Generar Órdenes de Producción".
    *   Al hacer clic, el sistema debe crear una OP (`mrp.production`) por cada línea de "Color/Talla" registrada en el programa.
    *   Las OPs generadas deben tomar la información del programa: producto, cantidad, BoM y ubicaciones.
    *   Una vez generadas las OPs, el estado del programa debe cambiar a "Finalizado".

5.  **Trazabilidad:**
    *   Las OPs creadas deben tener una referencia al Programa de Venta que las originó.
    *   El Programa de Venta debe mostrar un listado (smart button) de las OPs que se generaron a partir de él.

### Notas Adicionales:
*   La interfaz debe ser intuitiva y similar al diseño proporcionado, permitiendo una carga rápida de datos en la matriz de tallas y colores.
*   El sistema debe incluir la configuración de seguridad necesaria para que solo roles específicos puedan crear, aprobar y generar OPs desde el programa.
