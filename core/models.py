from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


# Create your models here.


class Empleado(models.Model):

	"""Modelo de datos para Empleados"""
	cedula = models.CharField(primary_key=True, max_length=16)
	nombre = models.CharField(max_length=15)
	segundo_nombre  = models.CharField(max_length=15, null=True)
	apellido = models.CharField(max_length=15)
	segundo_apellido = models.CharField(max_length=15, null=True)
	fecha_nacimiento = models.DateField("Fecha de nacimiento")
	sexo = models.CharField(max_length=1, choices=[('m', 'Masculino'), ('f', 'Femenino')])
	direccion = models.CharField(max_length=200)
	correo = models.EmailField('Email', unique=True)
	usuario = models.OneToOneField(User, null=True, on_delete=models.SET_NULL, default=None)
	notificar = models.CharField(max_length=2, choices=[('n', 'nada'), ('a', 'anulaciones'), ('o', 'orden de ruta'), ('p', 'proformas'), ('f', 'facturas'), ('t', 'todo')], default='n')
	activo = models.BooleanField(default=True)


	class Meta:
		ordering = ['apellido', 'nombre']
		permissions = [
			('desactivar_empleado', 'Puede desactivar un empleado.'),
			('asignar_empleado', 'Puede asignar un usuario al empleado.'),
		]
		indexes = [
			models.Index(fields=['correo', 'nombre', 'apellido'])
		]

	def __str__(self):
		return '{0} {1}'.format(self.nombre, self.apellido)

	def get_absolute_url(self):
		return reverse('vVerEmpleado', {'_id':self.cedula})



class Categoria(models.Model):

	nombre = models.CharField(max_length=45)

	class Meta:
		permissions = [
			('administrar_categoria', 'Puede administrar categorias de productos.'),
		]

	def __str__(self):
		return self.nombre



class Unidad(models.Model):

	nombre = models.CharField(max_length=25)
	simbolo = models.CharField(max_length=8)
	unidad_base = models.BooleanField()

	class Meta:
		ordering = ['nombre']
		verbose_name = "Unidad de Medida"
		verbose_name_plural = "Unidades de Medida"
		permissions = [
			('administrar_unidad', 'Puede administrar las unidades de medida.'),
		]

	def __str__(self):

		return self.nombre



class Conversion(object):
	"""docstring for Conversion"""
	
	origen = models.ForeignKey(Unidad)
	destino = models.ForeignKey(Unidad)
	relacion_directa = models.DecimalField()
	relacion_inversa = models.DecimalField()

	class Meta:
		ordering = ['origen']
		verbose_name = 'Conversión de Unidades'
		verbose_name_plural = 'Conversiones de Unidades'
		






		