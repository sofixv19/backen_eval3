# Uso de IA — Evaluación Sumativa 3 (Programación Back End)

Herramienta utilizada: **Claude** (Anthropic), a través de Claude en modo
Cowork. Este documento resume, por etapa, los prompts utilizados, el tipo de
respuesta obtenida y cómo se aplicó en el desarrollo del proyecto.
Complementa (no reemplaza) los documentos de prompts de las Evaluaciones 1 y 2.

## 1. Punto de partida

**Prompt utilizado (resumen):** se adjuntó la pauta de la Evaluación 3
(`Eva_Sumativa_3.pdf`) y el proyecto completo de la Evaluación 2
(`eval2.zip`), pidiendo entender qué cambios nuevos exigía la pauta sobre el
proyecto ya existente.

**Respuesta obtenida / aplicación:** Claude leyó la pauta completa y el
código de la Evaluación 2 (modelos, vistas, urls, templates, `settings.py`),
identificó los requisitos nuevos (eliminar Django Admin como mecanismo de
operación, autenticación, 3 perfiles de usuario con permisos diferenciados,
recuperación de contraseña por correo, dashboards por perfil, 2 mantenedores
CRUD completos y 1 transacción) y propuso un plan concreto: usar
`Delegaciones` y `Categorías` como mantenedores, y `Registrar Actividad`
(que ya relaciona Delegación + Categoría) como la transacción operacional.

## 2. Sistema de autenticación y perfiles (grupos)

**Prompt utilizado (resumen):** se pidió implementar inicio/cierre de
sesión, protección de vistas, y 3 perfiles de usuario con permisos
diferenciados (Administrador, Supervisor, Administrativo), usando el
sistema de autenticación propio de Django.

**Respuesta obtenida:** Claude propuso usar directamente
`django.contrib.auth` (modelo `User` y `Group`, sin modelos propios), con
dos decoradores personalizados (`grupo_requerido`, `permiso_requerido` en
`cuentas/decorators.py`) para proteger vistas por perfil o por permiso
específico, y un comando de gestión (`crear_grupos`) que asigna a cada
grupo un conjunto distinto de permisos Django (`add_x`/`change_x`/
`delete_x`/`view_x`, generados automáticamente por cada modelo).

**Aplicación:** implementado en la nueva app `cuentas` (`views.py`,
`forms.py`, `decorators.py`, `urls.py`), aplicando los decoradores a las
vistas existentes de `delegaciones` y `gestion`. Se verificó mediante un
script de pruebas automatizado (usando `django.test.Client`) que un usuario
del grupo "Administrativo" no puede acceder a vistas reservadas para
"Administrador" (es redirigido con un mensaje de error) y sí puede acceder
a las que su perfil permite.

## 3. Recuperación de contraseña por correo electrónico

**Prompt utilizado (resumen):** se pidió un flujo completo de recuperación
de contraseña que enviara un correo real (no solo un mensaje en la
terminal), para poder mostrar la "recepción del correo" como evidencia.

**Respuesta obtenida:** Claude explicó las opciones disponibles (backend de
consola vs. SMTP real) y recomendó usar una cuenta de Gmail con
"contraseña de aplicación" como remitente, reutilizando las vistas que ya
trae Django (`PasswordResetView` y las 3 que completan el flujo), solo
personalizando sus plantillas HTML y el texto del correo para mantener el
estilo del sitio.

**Aplicación:** implementado en `cuentas/urls.py` (vistas de Django
reutilizadas) y las plantillas `cuentas/templates/cuentas/password_reset_*`.
Se probó el flujo completo de forma automatizada (solicitud → generación de
token → enlace → validación → cambio de contraseña → confirmación),
confirmando que la nueva contraseña queda activa.

## 4. Mantenedores (Delegaciones y Categorías) y la transacción (Actividades)

**Prompt utilizado (resumen):** se pidió reemplazar las pantallas "en
construcción" de la Evaluación 2 por formularios reales (Django Forms) que
efectivamente creen, modifiquen y eliminen registros, agregando además un
mantenedor completo para Categorías (que antes solo existía en Django
Admin).

**Respuesta obtenida:** Claude implementó `DelegacionForm`, `CategoriaForm`
y `ActividadForm` (con validaciones: código único normalizado, selects para
las relaciones), reescribió las vistas `crear`/`editar`/`eliminar` de ambas
apps usando esos formularios, y agregó manejo explícito de la relación
protegida (`on_delete=PROTECT`) entre Categoría y Actividad, mostrando un
mensaje claro en vez de un error técnico si se intenta eliminar una
categoría con actividades asociadas.

**Aplicación:** implementado en `delegaciones/forms.py`/`views.py` y
`gestion/forms.py`/`views.py`, con sus templates nuevos
(`form.html`, `eliminar.html`, `categoria_*.html`, `actividad_*.html`).
Se verificó de forma automatizada que los formularios efectivamente guardan
los registros en la base de datos.

## 5. Verificación general del proyecto

**Prompt utilizado:** se pidió validar que todo el proyecto funcionara
correctamente antes de entregarlo (sin errores de configuración, rutas
rotas, o vistas que no respetaran los permisos).

**Respuesta obtenida y aplicación:** Claude ejecutó `python manage.py
check`, aplicó las migraciones en una base de datos de prueba, generó
usuarios de prueba para cada perfil, y corrió un script automatizado que
recorre las rutas principales del sistema verificando: páginas públicas
accesibles sin sesión, vistas protegidas que redirigen si falta sesión o
permiso, y que las operaciones de los 3 formularios (delegación, actividad,
usuario) efectivamente persisten en la base de datos.

## 6. Integración del trabajo en equipo (Cargos y Metas)

**Prompt utilizado (resumen):** se compartió con Claude el avance que
había desarrollado por su cuenta el compañero de curso Ignacio Sepúlveda
(un proyecto Django independiente, con los modelos `CargoFuncion` y
`MetaProyecto`, y vistas de solo lectura sobre MySQL), pidiendo fusionarlo
con el proyecto propio para que la entrega final fuera un trabajo
conjunto.

**Respuesta obtenida:** Claude revisó ambos proyectos y explicó que no
convenía fusionar literalmente los dos códigos completos, porque el
proyecto de Ignacio todavía estaba en una etapa equivalente a la
Evaluación 2 (sin autenticación, sin perfiles, sin recuperación de clave,
botones de editar/eliminar simulados) y además definía sus propios
modelos `Delegacion`/`Actividad`, que habrían chocado con los que ya
existían en este proyecto. La propuesta fue: mantener como base este
proyecto (que ya cumplía todos los puntos de la pauta) y portar la parte
de Ignacio que sí era nueva y no se repetía —los **Cargos y Metas**
institucionales— como una **tercera app (`cargos`)**, con CRUD completo,
conectada al mismo sistema de login, perfiles y permisos que ya existía
(algo que el módulo original todavía no tenía).

**Aplicación:** se crearon los modelos `CargoFuncion` y `MetaProyecto`
(`cargos/models.py`, basados en los de Ignacio), formularios, vistas
protegidas con `permiso_requerido`, plantillas con el mismo estilo visual
del resto del sistema, rutas (`/cargos/`), un comando de carga de datos
de ejemplo (`cargar_cargos`, a partir de los datos que trajo Ignacio) y
se extendieron `crear_grupos` y los 3 dashboards para incluir el nuevo
mantenedor. Se agregó como tercer mantenedor, superando el mínimo de 2
que pide la pauta. Se volvió a correr el script de verificación
automatizada (ver punto 5) agregando casos para Cargos, confirmando que
el CRUD funciona y que los permisos por perfil se respetan igual que en
el resto del sistema.

---

*Este documento fue redactado a partir del trabajo real realizado junto a
Claude durante esta etapa; se recomienda completar con capturas de pantalla
propias (login, recuperación de contraseña, los 3 dashboards, mantenedores,
transacción, AWS, GitHub) para el Documento Técnico final.*
