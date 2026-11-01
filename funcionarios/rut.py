"""
Utilidades para el RUT chileno: cálculo del dígito verificador (módulo 11),
validación y formato estándar "12.345.678-5".
"""
from django.core.exceptions import ValidationError


def limpiar_rut(valor):
    """Quita puntos, guion y espacios, y deja la K en mayúscula."""
    return (valor or '').replace('.', '').replace('-', '').replace(' ', '').upper()


def calcular_dv(numero):
    """Dígito verificador de un RUT (algoritmo módulo 11)."""
    suma = 0
    multiplicador = 2
    for digito in reversed(str(numero)):
        suma += int(digito) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1
    resto = 11 - (suma % 11)
    if resto == 11:
        return '0'
    if resto == 10:
        return 'K'
    return str(resto)


def formatear_rut(numero, dv):
    return f'{int(numero):,}'.replace(',', '.') + f'-{dv}'


def validar_rut(valor):
    """Valida un RUT y lo devuelve normalizado ("12.345.678-5").
    Lanza ValidationError si no es válido."""
    rut = limpiar_rut(valor)
    if len(rut) < 2 or not rut[:-1].isdigit():
        raise ValidationError('Formato de RUT inválido. Ejemplo: 12.345.678-5')
    numero, dv = rut[:-1], rut[-1]
    if not 1_000_000 <= int(numero) <= 99_999_999:
        raise ValidationError('El número del RUT no es válido.')
    if calcular_dv(numero) != dv:
        raise ValidationError('El dígito verificador del RUT no es correcto.')
    return formatear_rut(numero, dv)
