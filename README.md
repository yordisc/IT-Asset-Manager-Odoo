# 🖥️ IT Asset Manager para Odoo 17

> **Módulo profesional de gestión de activos informáticos** | Proyecto de portafolio

Gestiona el ciclo de vida completo de activos IT (laptops, monitores, licencias) con asignación a empleados, tracking de garantía, reportes analíticos y seguridad basada en roles.

## ✨ Características Principales

| Característica | Descripción |
|---|---|
| **Gestión de Activos** | Crear, categorizar y dar seguimiento a todos los activos de IT |
| **Flujo de Estados** | Disponible → Asignado → Mantenimiento → Baja |
| **Asignación a Empleados** | Registrar asignaciones con historial completo |
| **Seguimiento de Garantía** | Alertas automáticas cuando la garantía está por vencer |
| **Control de Acceso** | Dos roles: Técnico (acceso total) y Empleado (solo propios activos) |
| **Reportes Analíticos** | Vistas de gráficos y pivotes por estado y tipo |
| **Demo Data Integrada** | 5 activos + 4 empleados + 3 asignaciones de ejemplo |
| **Suite de Tests** | 6 casos de prueba unitarios incluidos |

## 🚀 Quick Start

### Prerequisitos
- Docker & Docker Compose
- O: GitHub Codespaces (recomendado)

### Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/yordisc/IT-Asset-Manager-Odoo.git
   cd IT-Asset-Manager-Odoo
   ```

2. **Iniciar los servicios**
   ```bash
   docker compose up -d
   ```

3. **Acceder a Odoo**
   - 🌐 URL: http://localhost:8069
   - 📧 Usuario: `admin`
   - 🔑 Contraseña: `admin`

4. **Instalar el módulo**
   - Activar el Modo de Desarrollador (esquina superior derecha)
   - Ir a: Apps → Búsqueda: "IT Assets Manager"
   - Clic en Instalar

### Demo en 5 Minutos

**Como Técnico IT:**
1. Crear un nuevo activo (Laptops)
2. Asignarlo a un empleado
3. Verificar cambio de estado a "Asignado"
4. Devolver el activo y confirmación de cambio a "Disponible"

**Como Empleado:**
1. Cambiar usuario a: `empleado1.demo@example.com` / `admin`
2. Observar que **solo ve sus activos asignados** (regla de seguridad activa)
3. Ver detalles en la vista Kanban agrupada por estado

**Consultar Reportes:**
1. Ir a: Análisis → Gráfico de Activos
2. Ver distribución de estados en gráfico de barras
3. Cambiar a vista Pivote para matriz Estado × Tipo

---

## 📊 Estructura del Proyecto

```
.
├── .devcontainer/
│   └── devcontainer.json           # Config para GitHub Codespaces
├── docker-compose.yml              # Orchestración PostgreSQL + Odoo 17
├── config/
│   └── odoo.conf                   # Configuración de Odoo
├── addons/
│   └── it_assets_manager/          # 🎯 MÓDULO PRINCIPAL
│       ├── __init__.py
│       ├── __manifest__.py          # Metadatos del módulo
│       ├── models/                  # Lógica de negocio (ORM)
│       │   ├── it_asset.py         # Modelo principal de activos
│       │   ├── it_asset_category.py# Categorización
│       │   └── it_asset_assignment.py# Asignaciones y historial
│       ├── views/                   # Interfaces de usuario
│       │   ├── it_asset_views.xml  # Vistas Kanban, Tree, Form
│       │   └── it_assets_menu.xml  # Menú de navegación
│       ├── security/                # Control de acceso
│       │   ├── security_groups.xml # Definición de roles
│       │   └── ir.model.access.csv # Matriz de permisos
│       ├── data/
│       │   └── demo_data.xml       # Datos de demostración
│       ├── report/
│       │   └── it_asset_report_views.xml# Gráficos y pivotes
│       └── tests/
│           └── test_it_asset.py    # 6 casos de prueba unitarios
├── README.md
└── PLAN_DE_DESARROLLO.md
```

---

## 🏗️ Modelos de Datos

### it.asset (Activo)
| Campo | Tipo | Descripción |
|---|---|---|
| `name` | Char | Nombre único del activo |
| `asset_type` | Selection | Laptop, Monitor, Licencia, Periférico, Otro |
| `serial_number` | Char | Número de serie |
| `category_id` | M2O | Categoría del activo |
| `purchase_date` | Date | Fecha de compra |
| `warranty_end_date` | Date | Fecha de vencimiento de garantía |
| `state` | Selection | disponible, asignado, mantenimiento, baja |
| `current_employee_id` | computed | Empleado actual (desde asignación abierta) |
| `assignment_ids` | O2M | Historial de asignaciones |

### it.asset.assignment (Asignación)
| Campo | Tipo | Descripción |
|---|---|---|
| `asset_id` | M2O | Referencia al activo |
| `employee_id` | M2O | Empleado asignado |
| `assigned_date` | Date | Fecha de asignación |
| `returned_date` | Date | Fecha de devolución (si aplica) |
| `notes` | Text | Notas adicionales |

### it.asset.category (Categoría)
| Campo | Tipo | Descripción |
|---|---|---|
| `name` | Char | Nombre de la categoría |
| `code` | Char | Código único |

---

## 👥 Control de Acceso

### Grupos de Seguridad

| Grupo | Permisos | Vistas |
|---|---|---|
| **Técnico IT** | Lectura/Escritura/Borrado total | Todos los activos |
| **Empleado** | Solo lectura de propios activos | Via `current_employee_id` |

### Reglas de Acceso
- Un empleado solo ve activos donde `current_employee_id.user_id = usuario actual`
- Botones de acción (Asignar, Devolver, etc.) solo visibles para Técnico

---

## 📝 Casos de Prueba

Se incluyen **6 tests unitarios** con `TransactionCase`:

1. ✅ Crear activo con estado "disponible" por defecto
2. ✅ Asignar exitosamente a empleado
3. ✅ Rechazar doble asignación
4. ✅ Devolver activo y revertir a "disponible"
5. ✅ Rechazar baja con asignación activa
6. ✅ Validar historial de asignaciones múltiples

**Ejecutar tests:**
```bash
docker compose exec odoo odoo -d it_assets_demo --test-enable --stop-after-init -i it_assets_manager
```

---

## 📋 Stack Técnico

| Componente | Versión | Propósito |
|---|---|---|
| Odoo | 17 (Community) | Framework ERP |
| PostgreSQL | 15 | Base de datos |
| Python | 3.10+ | Lenguaje de desarrollo |
| Docker | Latest | Containerización |
| Git | 2.34+ | Control de versiones |

---

## 📂 Datos de Demostración

### Usuarios Pre-configurados
```
Técnico:    tecnico.demo@example.com / admin
Empleado 1: empleado1.demo@example.com / admin
Empleado 2: empleado2.demo@example.com / admin
Empleado 3: empleado3.demo@example.com / admin
```

### Activos de Ejemplo
- 5 activos con diferentes estados
- Distribuidos entre 3 empleados
- 3 asignaciones con historial completo

---

## 🔧 Desarrollo Local (Sin Codespaces)

```bash
# 1. Clonar
git clone <repo>
cd IT-Asset-Manager-Odoo

# 2. Levantar servicios
docker compose up -d

# 3. Ver logs de Odoo
docker compose logs -f odoo

# 4. Esperar health check (1-2 min)
docker compose ps  # Esperar hasta que ambos servicios estén "healthy"

# 5. Acceder
# http://localhost:8069
```

---

## 🎓 Propósito Educativo

Este módulo demuestra:
- ✅ Modelado de datos en ERP (ORM)
- ✅ Máquinas de estado (flujos de negocio)
- ✅ Seguridad basada en roles
- ✅ Validaciones y constraints
- ✅ Vistas (Kanban, Tree, Form, Pivot, Graph)
- ✅ Buenas prácticas de testing
- ✅ Documentación código

**Ideal para:** Entrevistas técnicas, portafolio, aprendizaje de Odoo

---

## 📞 Soporte

Para más detalles técnicos, consultar [PLAN_DE_DESARROLLO.md](PLAN_DE_DESARROLLO.md)

---

**Versión:** 17.0.1.0.0 | **Estado:** ✅ Completado | **Última actualización:** Julio 2026

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

## 4. Demostración rápida (5 minutos)

### 4.1 Acceder a la aplicación

1. Abrir `http://localhost:8069` (puerto expuesto en Codespaces).
2. Login con credenciales de demo:
   - **Técnico IT**: usuario: `tecnico.demo@example.com` | contraseña: `admin`
   - **Empleado**: usuario: `empleado1.demo@example.com` | contraseña: `admin`
3. Ir a **IT Assets** desde el menú principal.

### 4.2 Flujo rápido como Técnico

1. **Ver dashboard**: Click en **Análisis** para ver gráficos de activos por estado.
2. **Crear un activo** (opcional): **Activos** → Nuevo → Rellenar datos → Guardar.
3. **Asignar**: Abrir un activo disponible → Click en **Asignar** → Seleccionar empleado → Guardar.
4. **Devolver**: Abrir el activo asignado → Click en **Devolver** → El activo vuelve a Disponible.
5. **Filtros**: Probar filtros como "Por vencer garantía" o "En mantenimiento".

### 4.3 Vista como Empleado

1. Loguearse como empleado.
2. Ver solo los activos asignados a ese usuario.
3. No puede realizar acciones de gestión (botones ocultos).

## 5. Datos de demo precargados

- **Usuarios**: tecnico.demo@example.com, empleado1.demo@example.com, empleado2.demo@example.com, empleado3.demo@example.com
- **Activos**: 5 activos variados (laptops, monitores, licencias)
- **Asignaciones**: 3 registros de ejemplo con historial completo
- **Categorías**: Laptops, Monitores, Licencias, Periféricos

## 6. Siguiente decisión técnica

Antes de empezar con tests automatizados, conviene validar manualmente la demo
o definir si se incluirán tests unitarios para el próximo milestone.
