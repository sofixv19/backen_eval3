# SGR La Serena — Evaluación Sumativa 3 (Programación Back End)

Continuación del proyecto "Sistema de Gestión de Resultados (SGR)" de las
delegaciones de la Municipalidad de La Serena. Sobre la base de la
**Evaluación Sumativa 2** (base de datos relacional + Django Admin), esta
evaluación **elimina por completo el uso de Django Admin para operar el
sistema** y lo reemplaza por una aplicación real con **autenticación,
perfiles de usuario, recuperación de contraseña por correo, dashboards
diferenciados y mantenedores/transacciones con Django Templates**.

**Trabajo en equipo (3 integrantes):** Sofía Veliz Espinosa, Ignacio
Sepúlveda y Elías. Según la pauta, por cada integrante adicional se
agregan 2 mantenedores y 1 transacción, por lo que el sistema incluye
**6 mantenedores y 3 transacciones**. Los módulos de Cargos, Metas y
Funcionarios parten del avance de Ignacio (gestionCargosApp y
registroActividadesApp), integrados aquí con CRUD real y permisos por
perfil.

## Qué cambió respecto a la Evaluación 2

| Evaluación 2 | Evaluación 3 |
|---|---|
| Operación del sistema desde Django Admin | Django Admin **no se usa** para operar; todo es con Django Templates propios |
| Sin inicio de sesión (sitio público) | Sistema de autenticación de Django: login, logout, vistas protegidas |
| Un solo tipo de usuario (superusuario) | 3 perfiles (grupos): **Administrador**, **Supervisor**, **Administrativo**, cada uno con permisos distintos |
| Sin recuperación de contraseña | Recuperación de contraseña por correo electrónico (Gmail SMTP), con token seguro |
| Botones Agregar/Modificar/Eliminar "en construcción" | CRUD completamente funcional en **6 mantenedores** (Delegaciones, Categorías, Cargos, Metas, Funcionarios, Vecinos) |
| "Registrar actividad" sin formulario real | **3 transacciones** con validaciones: Registrar actividad, Seguimiento de actividad y Solicitud vecinal |
| Un solo panel (portada con gráficos) | **3 dashboards**, uno por perfil, con accesos distintos |
| — | Página **Mi perfil** con foto, edición de datos y cambio de contraseña |

La base de datos relacional, el despliegue en AWS EC2 y el control de
versiones en GitHub (requisitos de la Evaluación 2) se mantienen.

## Estructura del proyecto

```
sgr_evaluacion/      # Configuración del proyecto (settings, urls raíz)
  estilos_formulario.py  # Mixin que aplica clases Bootstrap a los formularios
cuentas/             # App nueva: autenticación, perfiles (grupos), paneles, usuarios
  decorators.py        #   grupo_requerido / permiso_requerido (protección de vistas)
  forms.py              #   Login, recuperación de clave, creación/edición de usuarios
  views.py              #   Login/logout, 3 dashboards, gestión de usuarios
  management/commands/crear_grupos.py  # Crea los 3 perfiles con sus permisos
delegaciones/        # Aplicación 1: mantenedor de Delegaciones (CRUD completo)
  forms.py              #   DelegacionForm
gestion/             # Aplicación 2: mantenedor de Categorías + transacción de Actividades
  forms.py              #   CategoriaForm, ActividadForm
cargos/              # Aplicación 3: mantenedores de Cargos y de Metas institucionales
  management/commands/cargar_cargos.py  # Carga data/cargos.json de ejemplo
funcionarios/        # Aplicación 4: mantenedor de Funcionarios (RUT validado)
  rut.py                #   Validación del RUT chileno (dígito verificador)
  management/commands/cargar_funcionarios.py
atencion/            # Aplicación 5: mantenedor de Vecinos + transacción Solicitudes vecinales
  management/commands/cargar_atencion.py
data/                # JSON originales de la Evaluación 1 (fuente para el seed)
static/              # Bootstrap local, CSS propio e imágenes
templates/           # Plantilla base compartida
.env.example         # Plantilla de variables de entorno (copiar a .env)
```

## Perfiles de usuario y permisos

Los perfiles se implementan con **grupos de Django** (`django.contrib.auth.models.Group`),
cada uno con un subconjunto de los permisos que Django genera automáticamente
por modelo (`add_x`, `change_x`, `delete_x`, `view_x`). Se crean/actualizan
con:

```bash
python manage.py crear_grupos
```

| Perfil | Mantenedores | Transacciones | Usuarios |
|---|---|---|---|
| **Administrador** | CRUD completo en los 6 | Las 3 (registrar/modificar/eliminar actividades, seguimiento, registrar y cerrar solicitudes) | Crear, editar, ver |
| **Supervisor** | Crear, editar y ver (no elimina). Delegaciones: solo ver | Las 3 (registrar/modificar actividades, seguimiento, registrar y cerrar solicitudes) | — |
| **Administrativo** | Solo ver (excepto Vecinos: puede registrar) | Registrar actividades y solicitudes vecinales (no seguimiento, no cerrar, no modificar) | — |

Cada usuario pertenece a un único grupo, asignado desde **Gestión de
usuarios** (`/cuentas/usuarios/`, exclusivo del perfil Administrador). Al
iniciar sesión, cada usuario es redirigido automáticamente al dashboard que
corresponde a su perfil.

## Mi perfil

Cualquier usuario autenticado tiene una página **Mi perfil**
(`/cuentas/mi-perfil/`, accesible desde su nombre en el menú superior) donde
puede subir o cambiar su **foto de perfil** (JPG, PNG, WEBP o GIF, máx. 2 MB),
editar su nombre y correo, y **cambiar su contraseña** (pidiendo la
contraseña actual). La foto se guarda en el modelo `PerfilUsuario`
(relación 1 a 1 con el usuario de Django) y los archivos subidos quedan en
la carpeta `media/`, que no se sube a GitHub.

## Mantenedores y transacción

**Mantenedores (6)** — cada uno permite crear, buscar, listar, modificar y eliminar:

- **Delegaciones** (`/delegaciones/`).
- **Categorías** (`/gestion/categorias/`).
- **Cargos** (`/cargos/`).
- **Metas institucionales** (`/cargos/metas/`): ítem medible, valor
  objetivo y ponderación (máx. 100%) por cargo.
- **Funcionarios** (`/funcionarios/`): RUT con dígito verificador validado
  y único, correo único, delegación y cargo.
- **Vecinos** (`/atencion/vecinos/`): RUT validado, dirección y delegación
  de su sector.

Las relaciones usan `on_delete=PROTECT` donde corresponde: no se puede
eliminar una delegación, cargo, funcionario o vecino que tenga registros
asociados (el sistema muestra un mensaje en vez de un error).

**Transacciones (3):**

1. **Registrar actividad** (`/gestion/nueva/`): relaciona Delegación +
   Categoría, con código único normalizado.
2. **Seguimiento de actividad** (botón en la ficha de cada actividad):
   registra el cambio de estado + observación (mín. 10 caracteres, estado
   distinto al actual) y actualiza la actividad en una misma transacción
   de base de datos (`transaction.atomic` + `select_for_update`). Queda un
   historial con usuario y fecha.
3. **Solicitud vecinal** (`/atencion/solicitudes/nueva/`): relaciona Vecino
   + Delegación + Funcionario asignado (debe pertenecer a esa delegación y
   estar activo), genera un código `SOL-00001`, guarda quién la registró y
   luego se puede cerrar con una respuesta.

## Recuperación de contraseña por correo

Implementada reutilizando las vistas oficiales de Django
(`PasswordResetView` y las que completan el flujo), con plantillas propias.
El correo se envía por **SMTP de Gmail** usando una *contraseña de
aplicación* (no la contraseña normal de la cuenta). Configuración en `.env`:

```
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=tu_contrasena_de_aplicacion_16_caracteres
DEFAULT_FROM_EMAIL=tu_correo@gmail.com
```

Guía para generar la contraseña de aplicación: ver comentarios en
`.env.example`.

## Cómo ejecutar el proyecto en local (desarrollo)

1. Crear y activar un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate      # En Windows: venv\Scripts\activate
   ```
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Copiar el archivo de variables de entorno y completarlo (incluye ahora
   las variables `EMAIL_*`):
   ```bash
   cp .env.example .env
   ```
4. Aplicar las migraciones:
   ```bash
   python manage.py migrate
   ```
5. Crear los 3 perfiles (grupos) con sus permisos:
   ```bash
   python manage.py crear_grupos
   ```
6. Cargar los datos de ejemplo (delegaciones y actividades):
   ```bash
   python manage.py cargar_datos_iniciales
   ```
6.1. Cargar cargos, metas, funcionarios, vecinos y solicitudes de ejemplo:
   ```bash
   python manage.py cargar_cargos
   python manage.py cargar_funcionarios
   python manage.py cargar_atencion
   ```
7. Crear un superusuario (tiene acceso total, equivalente al perfil
   Administrador, sin necesidad de asignarle grupo):
   ```bash
   python manage.py createsuperuser
   ```
8. Levantar el servidor:
   ```bash
   python manage.py runserver
   ```
9. Abrir `http://127.0.0.1:8000/` — redirige a la pantalla de inicio de
   sesión (`/cuentas/ingresar/`).

Para crear usuarios de prueba con los otros 2 perfiles (Supervisor,
Administrativo), inicia sesión como el superusuario y usa **Gestión de
usuarios** desde el panel de Administrador.

## Cómo pasar a MySQL / Despliegue en AWS EC2

Se mantiene igual que en la Evaluación 2 (ver `.env.example` para las
variables `DB_*`), agregando dos pasos nuevos después de `migrate`:

```bash
python manage.py crear_grupos
python manage.py cargar_datos_iniciales
python manage.py cargar_cargos
python manage.py cargar_funcionarios
python manage.py cargar_atencion
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8000
```

No olvidar completar las variables `EMAIL_*` en el `.env` de la instancia
EC2 para que la recuperación de contraseña funcione también en producción.

## Control de versiones (Git y GitHub)

```bash
git add .
git commit -m "Evaluación Sumativa 3: autenticación, perfiles, recuperación de clave y mantenedores funcionales"
git push
```

El archivo `.gitignore` excluye `venv/`, `.env`, `db.sqlite3` y los archivos
de caché de Python.

## Notas

- Django Admin se mantiene registrado (`/admin/`) solo como herramienta de
  soporte técnico; **no se usa para ninguna operación del sistema** —todas
  las operaciones (login, CRUD, recuperación de contraseña) pasan por las
  rutas propias de cada app, con Django Templates.
- Los datos de `data/actividades.json` y `data/delegaciones.json` se
  conservan solo como fuente para el comando `cargar_datos_iniciales`.
- Uso de IA (Claude) documentado en la carpeta `docs_ia/` (prompts
  utilizados, respuestas obtenidas y su aplicación en el desarrollo).
