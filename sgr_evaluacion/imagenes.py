"""
Validaciones compartidas para las imágenes que suben los usuarios
(fotos de evidencia de actividades, seguimientos y solicitudes vecinales).

Se usa FileField + estas validaciones en vez de ImageField, para no
depender de la librería Pillow.
"""
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

EXTENSIONES_IMAGEN = ['jpg', 'jpeg', 'png', 'webp', 'gif']
TAMANO_MAXIMO_MB = 5

validar_extension_imagen = FileExtensionValidator(
    EXTENSIONES_IMAGEN,
    message='Solo se permiten imágenes JPG, PNG, WEBP o GIF.',
)


def validar_tamano_imagen(archivo):
    if archivo and archivo.size > TAMANO_MAXIMO_MB * 1024 * 1024:
        raise ValidationError(f'La imagen no puede pesar más de {TAMANO_MAXIMO_MB} MB.')


VALIDADORES_IMAGEN = [validar_extension_imagen, validar_tamano_imagen]
