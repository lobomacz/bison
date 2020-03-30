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
	# cedula = forms.CharField(max_length=16, min_length=16, validators=[RegexValidator('^[0-9]{3}-[0-9]{6}-[0-9]{3}[0-9A-Z]{2}$')])
	# nombre = forms.CharField(label='Primer Nombre', max_length=15)
	# segundo_nombre = forms.CharField(label='Segundo Nombre', max_length=15)
	# apellido = forms.CharField(label='Primer Apellido', max_length=15)
	# segundo_apellido = forms.CharField(label='Segundo Apellido', max_length=15)
	# direccion = forms.CharField(max_length=200, widget=forms.TextArea)
	# correo = forms.EmailField(label='Email')
	# activo = forms.BooleanField()
	
	nombre_usuario = forms.CharField(label='Nombre de Usuario', max_length=150)
	contrasena = forms.CharField(min_length=8, max_length=25, widget=forms.PasswordInput)
	contrasena_conf = forms.CharField(min_length=8, max_length=25, widget=forms.PasswordInput)

	class Meta:
		model = models.Empleado
		exclude ['usuario', 'activo', 'notificar']

	def clean(self):

		cleaned_data = super().clean()
		password = cleaned_data.get('contrasena')
		password_conf = cleaned_data.get('contrasena_conf')

		if password and password_conf:
			if not (password == password_conf):
				raise forms.ValidationError("Las contraseñas no coinciden.")


class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = models.Empleado
        exclude = ['usuario', 'activo', 'notificar']

class EditEmpleadoForm(forms.ModelForm):
    class Meta:
        model = models.Empleado
        exclude = ['usuario', 'activo', 'notificar']
        widgets = {'cedula':forms.TextInput(attrs={'readonly':True})}
    
		

class UsuarioForm(forms.Form):
	"""Formulario UsuarioForm"""
	nombre = forms.CharField(max_length=25)
	apellido = forms.CharField(max_length=25)
	correo = forms.EmailField()
	contrasena = forms.CharField(label='Contraseña', min_length=8, widget=forms.PasswordInput)
	contrasena_conf = forms.CharField(label='Confirmar Contraseña', min_length=8, widget=forms.PasswordInput)

	def clean(self):

		cleaned_data = super().clean()
		password = cleaned_data.get('contrasena')
		conf_password = cleaned_data.get('contrasena_conf')

		if password and conf_password:
			if not (password == conf_password):
				raise forms.ValidationError("Las contraseñas no coinciden.")


class UserForm(forms.ModelForm):
	"""docstring for UserForm"""

	class Meta:
		model = User
		widgets = {
		'id':forms.HiddenInput,
		'username':forms.TextInput(attrs={'readonly':True}),
		}


class AsignaUsuarioForm(forms.Form):

	id_empleado = forms.CharField(widget=forms.HiddenInput, max_length=16)
	id_usuario = forms.ChoiceField(choices=User.objects.filter(empleado__is_null=True))



class PasswordChangeForm(forms.Form):
	"""Formulario para cambio de password"""
	username = forms.CharField(label="Nombre de Usuario", min_length=8)
	old_password = forms.CharField(label='Password Anterior', widget=forms.PasswordInput, max_length=15, min_length=8)
	password = forms.CharField(label='Nuevo Password', widget=forms.PasswordInput, max_length=15, min_length=8)
	confirm_password = forms.CharField(label='Confirmar Password', widget=forms.PasswordInput, max_length=15, min_length=8)

	def clean(self):

		cleaned_data = super().clean()
		contrasena = cleaned_data.get('password')
		conf_contrasena = cleaned_data.get('confirm_password')

		if contrasena and conf_contrasena:
			if not (contrasena == conf_contrasena):
				raise forms.ValidationError("Las contraseñas no coinciden.")


class CategoriaForm(forms.ModelForm):
	"""Formulario de Categoria"""
	class Meta:
		model = models.Categoria
		exclude = ['id']

class EditCategoriaForm(forms.ModelForm):
	"""Formulario de Categoria"""
	class Meta:
		model = models.Categoria
		fields = '__all__'
		widgets = {'id':forms.HiddenInput}


class UnidadForm(forms.ModelForm):
	"""Formulario para UnidadMedida"""
	class Meta:
		model = models.Unidad
		exclude = ['id']


class EditUnidadForm(forms.ModelForm):
	"""Formulario para UnidadMedida"""
	class Meta:
		model = models.Unidad
		fields = '__all__'
		widgets = {
			'id':forms.HiddenInput
		}
		
		
		
		