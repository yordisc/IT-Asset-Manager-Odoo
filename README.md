# IT Asset Manager — Módulo custom para Odoo

Proyecto de portafolio: módulo de gestión de activos IT (laptops, monitores,
licencias) construido desde cero sobre Odoo 17, pensado para demostrar
competencias de análisis de sistemas: modelado de datos, flujos de estado,
seguridad por roles, reportes y buenas prácticas de desarrollo.

## Objetivo del proyecto

Mostrar en una entrevista técnica (rol: Analista de Sistemas):
- Capacidad de modelar un dominio de negocio en un ERP real.
- Entendimiento de flujos de trabajo (estados, transiciones, validaciones).
- Nociones de seguridad (grupos, reglas de acceso).
- Capacidad de documentar y testear lo que se construye.

## Stack

- Odoo 17 (Community)
- PostgreSQL 15
- Docker / Docker Compose
- GitHub Codespaces como entorno de desarrollo
- Python 3.10+ (el que trae la imagen de Odoo)

---

## 1. Entorno Docker en Codespace

### 1.1 Estructura de carpetas del repo

```
it-assets-project/
├── .devcontainer/
│   └── devcontainer.json
├── docker-compose.yml
├── config/
│   └── odoo.conf
├── addons/
│   └── it_assets_manager/        <- nuestro módulo custom
│       ├── __init__.py
│       ├── __manifest__.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── it_asset.py
│       │   ├── it_asset_assignment.py
│       │   └── it_asset_category.py
│       ├── views/
│       │   ├── it_asset_views.xml
│       │   ├── it_asset_assignment_views.xml
│       │   └── it_assets_menu.xml
│       ├── security/
│       │   ├── ir.model.access.csv
│       │   └── security_groups.xml
│       ├── data/
│       │   └── demo_data.xml
│       ├── report/
│       │   └── it_asset_dashboard_views.xml
│       └── tests/
│           ├── __init__.py
│           └── test_it_asset.py
└── README.md
```

### 1.2 `docker-compose.yml`

```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo
      POSTGRES_DB: postgres
    volumes:
      - odoo-db-data:/var/lib/postgresql/data

  odoo:
    image: odoo:17
    depends_on:
      - db
    ports:
      - "8069:8069"
    environment:
      HOST: db
      USER: odoo
      PASSWORD: odoo
    volumes:
      - ./addons:/mnt/extra-addons
      - ./config:/etc/odoo
      - odoo-web-data:/var/lib/odoo

volumes:
  odoo-db-data:
  odoo-web-data:
```

### 1.3 `config/odoo.conf`

```ini
[options]
addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons
db_host = db
db_user = odoo
db_password = odoo
```

### 1.4 `.devcontainer/devcontainer.json`

```json
{
  "name": "Odoo IT Assets Dev",
  "dockerComposeFile": "../docker-compose.yml",
  "service": "odoo",
  "workspaceFolder": "/mnt/extra-addons",
  "forwardPorts": [8069, 5432],
  "postCreateCommand": "echo 'Entorno listo. Odoo en el puerto 8069'"
}
```

### 1.5 Levantar el entorno

```bash
docker compose up -d
# Codespace expondrá el puerto 8069 automáticamente
```

Primer arranque:
1. Abrir el puerto 8069 forwardeado por Codespace.
2. Crear base de datos nueva desde el asistente de Odoo (marcar "Demo data" en NO, para no ensuciar con datos genéricos).
3. Ir a **Ajustes → Activar modo desarrollador** (para ver logs de errores y recargar módulos fácil).
4. Instalar el módulo `it_assets_manager` desde **Aplicaciones** (buscar sin filtro de "Apps", con el filtro quitado).

---

## 2. Plan de desarrollo paso a paso

### Día 1 — Esqueleto del módulo
- [ ] Crear `__manifest__.py` con nombre, versión, dependencias (`base`, `hr`), categoría.
- [ ] Crear modelo `it.asset.category` (simple: nombre, código).
- [ ] Crear modelo `it.asset` con campos:
  - `name` (Char, requerido)
  - `asset_type` (Selection: laptop / monitor / licencia / periférico / otro)
  - `serial_number` (Char)
  - `category_id` (Many2one a `it.asset.category`)
  - `purchase_date` (Date)
  - `warranty_end_date` (Date)
  - `state` (Selection: disponible / asignado / mantenimiento / baja, default disponible)
- [ ] Vista de lista y formulario básicas.
- [ ] Menú principal y submenú "Activos" / "Categorías".
- [ ] Archivo `ir.model.access.csv` mínimo para que el usuario admin pueda ver algo.

**Checkpoint:** poder crear un activo a mano desde la interfaz sin errores.

### Día 2 — Flujo de estados y asignaciones
- [ ] Modelo `it.asset.assignment`:
  - `asset_id` (Many2one a `it.asset`)
  - `employee_id` (Many2one a `hr.employee`)
  - `assigned_date` (Date, default today)
  - `returned_date` (Date, opcional)
  - `notes` (Text)
- [ ] Campo `assignment_ids` (One2many) en `it.asset` para ver el historial.
- [ ] Botones en el formulario de `it.asset`:
  - `action_assign` → crea un registro de asignación, cambia estado a "asignado"
  - `action_return` → cierra la asignación activa (`returned_date`), cambia estado a "disponible"
  - `action_send_maintenance` → cambia estado a "mantenimiento"
  - `action_retire` → cambia estado a "baja"
- [ ] Validaciones básicas (`@api.constrains`):
  - No permitir asignar un activo que no esté "disponible".
  - No permitir dar de baja un activo con asignación activa.

**Checkpoint:** flujo completo Disponible → Asignado → Mantenimiento → Baja funcionando desde la UI.

### Día 3 — Seguridad y vistas
- [ ] `security_groups.xml`: dos grupos, "Técnico IT" (lectura/escritura completa) y "Empleado" (solo lectura de sus propios activos asignados).
- [ ] Reglas de registro (`ir.rule`) para que un "Empleado" solo vea activos donde `assignment_ids.employee_id = user.employee_id`.
- [ ] Vista Kanban de `it.asset` agrupada por `state`, con tarjetas que muestren tipo, categoría y empleado asignado.
- [ ] Filtros guardados: "Por vencer garantía", "En mantenimiento", "Sin asignar".

**Checkpoint:** loguearse con un usuario de prueba del grupo "Empleado" y confirmar que solo ve lo suyo.

### Día 4 — Reportes, demo data y documentación
- [ ] Vista de reporte simple (gráfico de barras: cantidad de activos por estado y por categoría), usando `<graph>` y `<pivot>` view types de Odoo (no requiere código extra).
- [ ] `demo_data.xml` con 12-15 activos variados y 3-4 empleados de ejemplo con historial de asignación.
- [ ] Capturas de pantalla para el README (Kanban, formulario, reporte).
- [ ] Revisar y pulir textos, ayudas de campo (`help=` en los campos).

**Checkpoint:** el módulo se ve "terminado" para una demo de 5 minutos.

---

## 3. Tests a realizar

### 3.1 Tests unitarios (Odoo test framework, `tests/test_it_asset.py`)

Usar `TransactionCase` de `odoo.tests.common`. Casos mínimos:

1. **Creación de activo** — se crea con estado por defecto `disponible`.
2. **Asignación exitosa** — asignar un activo disponible cambia su estado a `asignado` y crea un registro en `it.asset.assignment`.
3. **Asignación rechazada** — intentar asignar un activo que ya está `asignado` debe lanzar `ValidationError`.
4. **Devolución** — devolver un activo asignado cierra la asignación activa (`returned_date` no nulo) y vuelve el estado a `disponible`.
5. **Baja con asignación activa** — intentar dar de baja un activo `asignado` debe lanzar `ValidationError`.
6. **Historial correcto** — un activo con 2 asignaciones y devoluciones tiene 2 registros en `assignment_ids`, ambos con fechas coherentes (assigned_date <= returned_date).

Ejecutar dentro del contenedor:
```bash
docker compose exec odoo odoo -d nombre_bd --test-enable --stop-after-init -i it_assets_manager
```

### 3.2 Tests manuales (checklist de QA)

- [ ] Crear activo desde el formulario, sin errores de validación.
- [ ] Asignar el activo a un empleado y verificar que aparece en la vista Kanban en la columna "Asignado".
- [ ] Intentar asignar el mismo activo dos veces → debe mostrar mensaje de error claro.
- [ ] Devolver el activo → vuelve a "Disponible" y el historial muestra la asignación cerrada.
- [ ] Mandar a mantenimiento y luego volver a servicio.
- [ ] Dar de baja un activo sin asignación activa → funciona.
- [ ] Loguearse como usuario "Empleado" y confirmar que solo ve activos propios.
- [ ] Revisar que el reporte de gráfico/pivot refleje los cambios de estado en tiempo real.
- [ ] Instalar el módulo desde cero en una base de datos nueva sin errores en el log.

---

## 4. Próximos pasos (opcional, si sobra tiempo)

- Notificación automática (actividad de Odoo) cuando `warranty_end_date` esté a 30 días de vencer.
- Botón de exportar historial de un activo a PDF.
- Endpoint XML-RPC simple para consultar activos desde un script externo (demuestra integración).

---

## 5. Cómo correr el proyecto (resumen rápido)

```bash
git clone <tu-repo>
cd it-assets-project
docker compose up -d
# abrir el puerto 8069 en Codespace
# crear base de datos -> instalar módulo "IT Assets Manager"
```
