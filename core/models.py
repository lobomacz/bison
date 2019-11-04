from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Usuario(models.Model):
	"""Modelo de datos para Usuario"""
	usuario = models.ForeignKey(User, on_delete=models.CASCADE)

	class Meta:
		permissions = [
			('administrar_usuarios', 'Administrar los usuarios.'),
			('cambiar_contrasena', 'Cambiar la contraseña de usuario.'),
			('asignar_usuario', 'Puede asignar usuarios a empleados.'),
		]

class Empleado(models.Model):
	"""Modelo de datos para Empleados"""
	cedula = models.CharField(primary_key=True, max_length=16)
	nombre = models.CharField(max_length=15)
	segundo_nombre  = models.CharField(max_length=15, null=True)
	apellido = models.CharField(max_length=15)
	segundo_apellido = models.CharField(max_length=15, null=True)
	direccion = models.CharField(max_length=200)
	correo = models.EmailField('Email', unique=True)
	usuario = models.OneToOneField(Usuario, null=True, on_delete=models.SET_NULL, default=None)
	activo = models.BooleanField(default=True)

	class Meta:
		permissions = [
			('administrar_empleados', 'Puede administrar empleados.'),
			('desactivar_empleado', 'Puede desactivar un empleado.'),
		]

class Categoria(models.Model):
	nombre = models.CharField(max_length=45)

	class Meta:
		permissions = [
			('administrar_categorias', 'Puede administrar categorias de productos.'),
		]

class Unidad(models.Model):
	nombre = models.CharField(max_length=25)
	simbolo = models.CharField(max_length=8)

	class Meta:
		verbose_name = "Unidad de Medida"
		verbose_name_plural = "Unidades de Medida"
		permissions = [
			('administrar_unidad', 'Puede administrar las unidades de medida.'),
		]