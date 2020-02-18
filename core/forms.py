from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from . import models

class LoginForm(forms.Form):
	"""Formulario de Ingreso LoginForm"""
	username = forms.CharField(label='Nombre de Usuario', min_length=8, max_length=150)
	password = forms.CharField(label='Contraseña', widget=forms.PasswordInput, min_length=8, max_length=15)

class EmpleadoUsuarioForm(forms.Form):
	"""Formulario de ingreso de EmpleadoUsuarioForm"""
	cedula = forms.CharField(max_length=16, min_length=16, validators=[RegexValidator('^[0-9]{3}-[0-9]{6}-[0-9]{3}[0-9A-Z]{2}$')])
	nombre = forms.CharField(label='Primer Nombre', max_length=15)
	segundo_nombre = forms.CharField(label='Segundo Nombre', max_length=15)
	apellido = forms.CharField(label='Primer Apellido', max_length=15)
	segundo_apellido = forms.CharField(label='Segundo Apellido', max_length=15)
	direccion = forms.CharField(max_length=200, widget=forms.TextArea)
	correo = forms.EmailField(label='Email')
	nombre_usuario = forms.CharField(label='Nombre de Usuario', max_length=150)
	password = forms.CharField(min_length=8, max_length=25, widget=forms.PasswordInput)
	activo = forms.BooleanField()


class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = models.Empleado
        exclude = ['usuario']
    
		
class AsignaUsuarioForm(forms.Form):

	usuarios = models.Usuario.objects.filter(empleado__isnull=True)
	id_usuario = forms.CharField(choices=usuarios, label='Usuario')

class UsuarioForm(forms.ModelForm):
	"""Formulario UsuarioForm"""
	class Meta:
		model = User
		exclude = ['id',]

class PasswordChangeForm(forms.Form):
	"""Formulario para cambio de password"""
	username = forms.CharField(label="Nombre de Usuario", min_length=8)
	old_password = forms.CharField(label='Password Anterior', widget=forms.PasswordInput, max_length=15, min_length=8)
	password = forms.CharField(label='Nuevo Password', widget=forms.PasswordInput, max_length=15, min_length=8)
	confirm_password = forms.CharField(label='Confirmar Password', widget=forms.PasswordInput, max_length=15, min_length=8)

class CategoriaForm(forms.ModelForm):
	"""Formulario de Categoria"""
	class Meta:
		model = models.Categoria
		exclude = ['id']

class UnidadForm(forms.ModelForm):
	"""Formulario para UnidadMedida"""
	class Meta:
		model = models.Unidad
		exclude = ['id']
		
		
		
		