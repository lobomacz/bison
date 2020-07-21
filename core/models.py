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



class Categoria(models.Model):

	nombre = models.CharField(max_length=45)

	class Meta:
		permissions = [
			('administrar_categoria', 'Puede administrar categorias de productos.'),
		]

	def __str__(self):
		return self.nombre

		

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
		


class Camion(models.Model):
	"""Modelo de datos para Camion"""
	descripcion = models.CharField(max_length=45, verbose_name='descripción')
	tonelaje = models.IntegerField(default=2)
	anno = models.CharField(verbose_name='año', max_length=4, min_length=4)
	seguro_hasta = models.DateField(verbose_name='seguro vence')
	placa = models.CharField(max_length=10)
	cuenta = models.ForeignKey(Cuenta, on_delete=models.PROTECT, on_update=models.CASCADE)
	habilitado = models.BooleanField()

	def __str__(self):

		return '{0} {1} Placa: {2}'.format(self.descripcion, self.anno, self.placa)




		