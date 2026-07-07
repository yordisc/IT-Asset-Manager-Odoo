# Plan de desarrollo del módulo IT Asset Manager

Este documento concentra la parte operativa del proyecto. El README principal queda como mapa general del entorno y este archivo funciona como guía de implementación.

## 1. Orden recomendado

1. Crear la estructura base del módulo.
2. Hacer que el modelo de activos funcione sin lógica compleja.
3. Agregar asignaciones e historial de uso.
4. Incorporar seguridad y reglas de acceso.
5. Añadir vistas de análisis y reporte.
6. Completar con datos demo, tests y documentación.

## 2. Día 1 - Esqueleto del módulo

- Crear la carpeta `addons/it_assets_manager/` con sus archivos base.
- Crear `__manifest__.py` con nombre, versión, dependencias (`base`, `hr`), categoría y descripción.
- Crear `__init__.py` raíz y `models/__init__.py` para registrar modelos.
- Crear el modelo `it.asset.category` con nombre y código.
- Crear el modelo `it.asset` con estos campos:
  - `name` (Char, requerido)
  - `asset_type` (Selection: laptop / monitor / licencia / periférico / otro)
  - `serial_number` (Char)
  - `category_id` (Many2one a `it.asset.category`)
  - `purchase_date` (Date)
  - `warranty_end_date` (Date)
  - `state` (Selection: disponible / asignado / mantenimiento / baja, default disponible)
- Crear vistas de lista y formulario básicas.
- Crear menú principal y submenú para `Activos` y `Categorías`.
- Crear `ir.model.access.csv` mínimo.
- Confirmar que el módulo se instala sin errores antes de seguir.

### Checkpoint

Poder crear un activo a mano desde la interfaz sin errores.

## 3. Día 2 - Flujo de estados y asignaciones

- Crear el modelo `it.asset.assignment`:
  - `asset_id` (Many2one a `it.asset`)
  - `employee_id` (Many2one a `hr.employee`)
  - `assigned_date` (Date, default today)
  - `returned_date` (Date, opcional)
  - `notes` (Text)
- Agregar `assignment_ids` (One2many) en `it.asset` para ver el historial.
- Agregar botones en el formulario de `it.asset`:
  - `action_assign` crea un registro de asignación y cambia estado a `asignado`.
  - `action_return` cierra la asignación activa y cambia estado a `disponible`.
  - `action_send_maintenance` cambia estado a `mantenimiento`.
  - `action_retire` cambia estado a `baja`.
- Agregar validaciones básicas con `@api.constrains`.
- Agregar mensajes de error claros para que el usuario entienda qué pasó.

### Checkpoint

Flujo completo Disponible -> Asignado -> Mantenimiento -> Baja funcionando desde la UI.

## 4. Día 3 - Seguridad y vistas

- Crear `security_groups.xml` con dos grupos: `Técnico IT` y `Empleado`.
- Crear reglas de registro para que un `Empleado` solo vea sus activos asignados.
- Crear vista Kanban agrupada por `state`.
- Crear filtros guardados: `Por vencer garantía`, `En mantenimiento`, `Sin asignar`.
- Verificar qué grupo puede editar y cuál solo puede leer antes de cerrar el módulo.

### Checkpoint

Loguearse con un usuario de prueba del grupo `Empleado` y confirmar que solo ve lo suyo.

## 5. Día 4 - Reportes, demo data y documentación

- Crear una vista de reporte simple con `graph` y `pivot`.
- Crear `demo_data.xml` con 12-15 activos variados y 3-4 empleados de ejemplo.
- Agregar capturas de pantalla para el README.
- Revisar textos y ayudas de campo con `help=`.
- Dejar una versión de demo que pueda mostrarse en 5 minutos.

### Checkpoint

El módulo se ve terminado para una demo corta.

## 6. Tests a realizar

### 6.1 Tests unitarios

Usar `TransactionCase` de `odoo.tests.common`.

Casos mínimos:

1. Creación de activo: se crea con estado por defecto `disponible`.
2. Asignación exitosa: un activo disponible cambia a `asignado` y crea un registro en `it.asset.assignment`.
3. Asignación rechazada: intentar asignar un activo ya `asignado` debe lanzar `ValidationError`.
4. Devolución: devolver un activo asignado cierra la asignación activa y vuelve el estado a `disponible`.
5. Baja con asignación activa: intentar dar de baja un activo `asignado` debe lanzar `ValidationError`.
6. Historial correcto: un activo con 2 asignaciones y devoluciones tiene 2 registros en `assignment_ids` con fechas coherentes.

Ejecutar dentro del contenedor:

```bash
docker compose exec odoo odoo -d nombre_bd --test-enable --stop-after-init -i it_assets_manager
```

### 6.2 Tests manuales

- Crear activo desde el formulario sin errores de validación.
- Asignar el activo a un empleado y verificar que aparece en la columna `Asignado`.
- Intentar asignar el mismo activo dos veces y comprobar que aparece un mensaje de error claro.
- Devolver el activo y verificar que vuelve a `Disponible`.
- Mandar a mantenimiento y luego volver a servicio.
- Dar de baja un activo sin asignación activa.
- Loguearse como usuario `Empleado` y confirmar que solo ve activos propios.
- Revisar que el reporte de gráfico y pivot refleje los cambios de estado.
- Instalar el módulo desde cero en una base de datos nueva sin errores.

### 6.3 Criterios de aceptación mínimos

- El módulo instala sin errores.
- Un activo puede crearse, asignarse, devolverse y darse de baja según las reglas definidas.
- Un empleado solo ve sus propios activos.
- El reporte refleja el estado real de los activos.
- Los tests automáticos pasan en el contenedor.

## 7. Próximos pasos opcionales

- Notificación automática cuando `warranty_end_date` esté a 30 días de vencer.
- Botón para exportar historial de un activo a PDF.
- Endpoint XML-RPC simple para consultar activos desde un script externo.
