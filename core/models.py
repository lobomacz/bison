from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from bison.contabilidad.models import Cuenta


# Create your models here.


class Empleado(models.Model):

	"""Modelo de datos para Empleados"""
	cedula = models.CharField(primary_key=True, max_length=16)
	nombre = models.CharField(max_length=15)
	segundo_nombre  = models.CharField(max_length=15, null=True)
	apellido = models.CharField(max_length=15)
	segundo_apellido = models.CharField(max_length=15, null=True)
	fecha_nacimiento = models.DateField(verbose_name="Fecha de nacimiento")
	sexo = models.CharField(max_length=1, choices=[('m', 'Masculino'), ('f', 'Femenino')])
	direccion = models.CharField(max_length=200)
	correo = models.EmailField(verbose_name='Email', unique=True)
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


		

class Producto(models.Model):
	"""Modelo para registro de productos"""
	codigo = models.CharField(max_length=50, unique=True)
	nombre = models.CharField(max_length=200)
	categoria = models.ForeignKey(Categoria)
	unidad_base = models.ForeignKey(UnidadMedida)
	costo_unit = models.DecimalField('Costo', max_digits=6, decimal_places=2)
	precio_unit = models.DecimalField('Precio', max_digits=6, decimal_places=2)
	minimo = models.DecimalField(max_digits=6, decimal_places=2)
	maximo = models.DecimalField(max_digits=6, decimal_places=2)
	existencia = models.DecimalField(max_digits=6, decimal_places=2)

	class Meta:
		ordering = ['categoria','nombre']


	def __str__(self):

		return self.nombre.upper()



class Conversion(object):
	"""docstring for Conversion"""
	
	origen = models.ForeignKey('TablaDetalle')
	destino = models.ForeignKey('TablaDetalle')
	relacion_directa = models.DecimalField(max_digits=8, decimal_places=4)
	relacion_inversa = models.DecimalField(max_digits=8, decimal_places=4)

	class Meta:
		ordering = ['origen']
		verbose_name = 'Conversión de Unidades'
		verbose_name_plural = 'Conversiones de Unidades'
		


class Tabla(models.Model):
	"""Modelo de tablas generales"""
	tabla = models.CharField(max_length=100)

	class Meta:
		ordering = ['tabla']

	def __str__(self):
		return self.tabla.upper() + 'S'



class DetalleTabla(models.Model):
	"""Modelo de detalle de tablas generales"""
	tabla = models.ForeignKey(Tabla, on_delete=models.CASCADE)
	elemento = models.CharField(max_length=150)
	codigo_equivalencia = models.CharField(max_length=25)

	class Meta:
		ordering = ['tabla', 'elemento']


		