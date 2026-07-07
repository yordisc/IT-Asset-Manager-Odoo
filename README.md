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

## Alcance del README

Este archivo se usará como mapa de construcción del proyecto. La idea es que
cada sección responda a una pregunta concreta: qué se necesita, qué se va a
crear, en qué orden hacerlo y cómo validar que quedó bien.

## Estado actual del repositorio

En este punto el repo solo tiene la base de infraestructura para Codespaces y
Odoo:
- `.devcontainer/devcontainer.json`
- `docker-compose.yml`
- `config/odoo.conf`
- `addons/` como carpeta destino para los módulos custom

Todavía no existe el módulo `it_assets_manager`; este README describe cómo lo
vamos a construir paso a paso.

## Stack

- Odoo 17 (Community)
- PostgreSQL 15
- Docker / Docker Compose
- GitHub Codespaces como entorno de desarrollo
- Python 3.10+ (el que trae la imagen de Odoo)

## Requisitos previos

- Tener acceso a GitHub Codespaces o, en su defecto, Docker y Docker Compose
  instalados localmente.
- Usar una base de datos nueva para el proyecto para evitar mezclar datos de
  pruebas con datos reales.
- Tener claro que Odoo 17 Community será la plataforma base de desarrollo.

---

## 1. Entorno Docker en Codespace

### 1.1 Estructura de carpetas del repo

```
IT-Asset-Manager-Odoo/
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

### 1.2 Cómo leer esta estructura

- `.devcontainer/` define cómo se abrirá el proyecto en Codespaces.
- `docker-compose.yml` levanta PostgreSQL y Odoo.
- `config/odoo.conf` define la configuración mínima de Odoo.
- `addons/` contendrá todos los módulos personalizados del proyecto.
- `README.md` funcionará como guía de implementación y validación.

### 1.3 `docker-compose.yml`

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

### 1.4 `config/odoo.conf`

```ini
[options]
addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons
db_host = db
db_user = odoo
db_password = odoo
```

### 1.5 `.devcontainer/devcontainer.json`

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

### 1.6 Levantar el entorno

```bash
docker compose up -d
# Codespace expondrá el puerto 8069 automáticamente
```

Primer arranque:
1. Abrir el workspace en Codespaces o levantar Docker Compose localmente.
2. Esperar a que PostgreSQL y Odoo estén disponibles.
3. Abrir el puerto 8069 y entrar al asistente de Odoo.
4. Crear una base de datos nueva y dejar la opción de demo desactivada.
5. Ir a **Ajustes → Activar modo desarrollador** para facilitar depuración.
6. Instalar el módulo `it_assets_manager` desde **Aplicaciones**.

### 1.7 Qué debe funcionar antes de avanzar

- Odoo debe abrir sin errores en `http://localhost:8069` o en el puerto que
  exponga Codespaces.
- La conexión a PostgreSQL debe quedar estable.
- La carpeta `addons/` debe estar montada dentro del contenedor.
- El archivo `odoo.conf` debe ser leído por el servicio de Odoo.

---

## 2. Plan de desarrollo y validación

La parte operativa del proyecto quedó separada en [PLAN_DE_DESARROLLO.md](PLAN_DE_DESARROLLO.md).

Ahí está el orden recomendado de implementación, los checkpoints por día, los
tests unitarios, la checklist manual de QA y los criterios mínimos de
aceptación.

## 3. Cómo correr el proyecto

```bash
git clone <tu-repo>
cd IT-Asset-Manager-Odoo
docker compose up -d
# abrir el puerto 8069 en Codespace
# crear base de datos -> instalar módulo "IT Assets Manager"
```

## 4. Siguiente decisión técnica

Antes de empezar a programar el módulo, conviene decidir si la primera entrega
va a incluir solo la capa funcional mínima o si también dejaremos listas desde
el inicio las vistas Kanban y de reporte.
