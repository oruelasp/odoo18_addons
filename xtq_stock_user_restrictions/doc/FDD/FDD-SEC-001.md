# Documento de Diseño Funcional (FDD)

**Código de Documento:** FDD-SEC-001
**Versión:** 1.0
**Fecha:** [Fecha Actual]
**Módulo:** `xtq_stock_user_restrictions` (Restricciones de Inventario por Usuario)

---

## 1. Propósito, Objetivo y Alcance

### 1.1. Propósito
Este documento describe el diseño de un nuevo módulo para Odoo v18 que extiende el sistema de seguridad estándar, permitiendo restringir el acceso de los usuarios a Almacenes y Tipos de Operación específicos.

### 1.2. Objetivo
El objetivo es proporcionar a los administradores una herramienta para configurar permisos de inventario granulares por usuario, con el fin de:
- **Mejorar la Seguridad:** Prevenir que los usuarios accedan a operaciones de plantas o áreas que no les corresponden.
- **Aumentar la Eficiencia:** Simplificar la interfaz del usuario, mostrando solo las operaciones relevantes para su rol y reduciendo la carga visual.
- **Minimizar Errores:** Reducir el riesgo de que un usuario procese por error una transferencia de otro almacén.

### 1.3. Alcance
- **EN ALCANCE:**
    - Modificar el formulario de Usuario para añadir una sección de configuración de restricciones de inventario.
    - Implementar reglas de seguridad que filtren las vistas de "Tipos de Operación" y "Transferencias" (`stock.picking`) según la configuración del usuario.
    - Asegurar que la restricción no impida la visibilidad de las ubicaciones (`stock.location`) de otros almacenes al seleccionar un origen o destino.
- **FUERA DE ALCANCE:**
    - La restricción de acceso a otros modelos de Odoo (como Órdenes de Producción, Pedidos de Compra, etc.).
    - La lógica de negocio interna de las transferencias de inventario.

---

## 2. Análisis del Proceso Actual (AS-IS en Odoo Estándar)
En Odoo estándar, los permisos de inventario se gestionan a través de grupos de acceso generales ("Usuario" o "Administrador"). Un usuario con el permiso "Usuario" tiene visibilidad y acceso para operar en **todos** los almacenes y tipos de operación de la compañía. Esto es ineficiente y riesgoso en un entorno con múltiples plantas o almacenes, como el de BRANDINT.

---

## 3. Propuesta de Solución (TO-BE)

### 3.1. Arquitectura de la Solución
La solución se implementará directamente en el **formulario de configuración del Usuario**. No se utilizará el configurador general de la compañía. Se creará una nueva sección que permitirá al administrador definir reglas específicas para cada usuario.

El control de acceso se aplicará mediante **reglas de seguridad a nivel de registro**, que son un mecanismo estándar de Odoo. Estas reglas filtrarán dinámicamente lo que el usuario ve en las listas y vistas kanban, basándose en su configuración personal.

**Excepción Crítica:** Las reglas de seguridad **no se aplicarán** a la visualización de las **Ubicaciones de Inventario**. Esto es fundamental para permitir que un usuario de la Planta A pueda seleccionar una ubicación de la Planta B como destino en una transferencia, garantizando la fluidez de las operaciones inter-planta.

### 3.2. Diseño de la Interfaz de Usuario
En el formulario de **Usuario** (`Configuración > Usuarios y Compañías > Usuarios`), se añadirá una nueva pestaña llamada **"Restricciones de Inventario"**.

Dentro de esta pestaña, se encontrarán los siguientes controles:

1.  **Activar Restricciones de Inventario:** Un checkbox (`[ ]`). Si no está marcado, el usuario mantiene el comportamiento estándar de Odoo. Si está marcado, se aplican las reglas definidas a continuación.

2.  **Tabla de Reglas de Acceso:** Una tabla donde el administrador puede añadir múltiples líneas. Cada línea representa una regla para un almacén y contendrá las siguientes columnas:
    *   **Almacén Permitido:** Un campo de selección para elegir un Almacén de la lista de almacenes de la compañía.
    *   **Tipos de Operación Permitidos:** Un campo de selección múltiple que permite elegir uno o varios Tipos de Operación.
        *   **Lógica Importante:** Si para un almacén dado, este campo se deja **en blanco**, el sistema interpretará que el usuario tiene acceso a **TODOS** los tipos de operación de ese almacén. Si se selecciona al menos uno, el acceso se restringirá únicamente a los seleccionados.

---

## 4. Flujo Detallado del Usuario (Administrador)

1.  El Administrador navega a `Configuración > Usuarios y Compañías > Usuarios` y abre la ficha de un operario de almacén.
2.  Va a la nueva pestaña **"Restricciones de Inventario"**.
3.  Marca el checkbox **"Activar Restricciones de Inventario"**.
4.  Hace clic en "Añadir una línea" en la tabla de reglas.
5.  En la nueva línea, selecciona el Almacén "Planta Mariscal Nieto".
6.  En la misma línea, en la columna "Tipos de Operación Permitidos", selecciona "PRODUCCION MN: Salidas Internas" y "MN: Recepciones".
7.  Guarda los cambios en la ficha del usuario.

---

## 5. Criterios de Aceptación

- Un administrador DEBE poder activar/desactivar las restricciones desde la ficha del usuario.
- Un administrador DEBE poder definir una o más reglas, asignando almacenes y tipos de operación específicos a un usuario.
- Si un usuario tiene la restricción activada, al ingresar al módulo de Inventario, DEBE ver únicamente los Tipos de Operación permitidos en su configuración.
- En las vistas de lista de Transferencias, el usuario restringido DEBE ver únicamente los pickings que pertenecen a los Tipos de Operación que tiene permitidos.
- Un usuario restringido, al procesar una transferencia de salida, DEBE poder ver y seleccionar ubicaciones de destino que pertenezcan a almacenes a los que no tiene acceso.
