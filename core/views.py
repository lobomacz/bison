from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied, BadRequest
from django.http import Http404
from django.conf import settings
#from django.apps import apps
from django.forms import formset_factory, modelformset_factory
from . import forms, models

# Create your views here.


def getNombreEmpresa():
	return settings.NOMBRE_EMPRESA


@login_required
def index(request):

	empresa = getNombreEmpresa()

	c = {
	'empresa':empresa, 
	'seccion':'inicio', 
	'titulo':'página de inicio', 

	}

	return render(request, 'indice.html', c)


def bison_login(request):
	
	form = None
	
	if request.method == "GET":
		
		form = LoginForm()
		return render(request, 'login.html', {'form':form})
	
	else:
		try:
		nonlocal form 
		form = LoginForm(request.POST)
		except FieldError:
			c = {'titulo':'Error de Datos', 'mensaje':'Los datos ingresados no son válidos.', 'view':'Index'}
			return render(request, 'error.html', c)
		except Exception as ex:
			c = {'titulo':'Error', 'mensaje':ex, 'view':'Index'}
			return render(request, 'error.html', c)

		if form is not None and form.is_valid():
			
			cred = request.POST
			uname = form.username
			password = form.password
			user = authenticate(request, 'username'=uname, 'password'=password)
			
			if user is not None:
				login(request, user)
				return redirect('index')
			
			else:
				'''Personalizar el mensaje de error por login incorrecto'''
				raise PermissionDenied



@login_required
def bison_logout(request):
	logout(request)
	return redirect('bison_login')



@login_required
@permission_required('core.administrar_empleado')
def lista_empleados(request, todos=False):
	
	empleados = None
	
	if todos:
		empleados = models.Empleado.objects.all()
	
	else:
		empleados = models.Empleado.objects.filter(activo=True)

	if not empleados:
		raise Http404('No se encontraron registros en la base de datos.')

	empresa = getNombreEmpresa()
	c = {'empresa':empresa, 'seccion':'Empleados', 'titulo':'listado de empleados', 'empleados':empleados, 'todos':todos}
	return render(request, 'lista_empleados.html', c)



@login_required
@permission_required('core.view_empleado')
def ver_empleado(request, _id):
		
	empleado = get_object_or_404(models.Empleado, pk=_id)
	empresa = getNombreEmpresa()
	c = {'empresa':empresa, 'seccion':'Empleados', 'titulo':'datos de empleado', 'empleado':empleado}
	return render(request, 'detalle_empleado.html', c)



@login_required
@permission_required('core.add_empleado')
def nuevo_empleado(request):
	
	if request.method == "GET":
		
		form = forms.EmpleadoForm()
		empresa = getNombreEmpresa()
		c = {'empresa':empresa, 'seccion':'Empleados', 'titulo':'registro de empleados', 'form':form, 'view':'vNuevoEmpleado'}
		
		return render(request, 'form_template.html', c)
	
	else if request.method == "POST":
		
		form = forms.EmpleadoForm(request.POST)
		
		if form.is_valid():
			form.save()
			
			return redirect('vEmpleados', {'mensaje':'El registro de aplicó con éxito.'})
		


@login_required
@permission_required(('core.add_empleado', 'core.add_usuario', 'core.asignar_usuario'))
def nuevo_empleado_usuario(request):
	
	if request.method == "GET":
		
		form = forms.EmpleadoUsuarioForm()

		empresa = getNombreEmpresa()

		c = {'empresa':empresa, 'seccion':'Empleados con Usuario', 'titulo':'registro de empleado con usuario', 'form':form, 'view':'vNuevoEmpleadoUsuario'}
		
		return render(request, 'form_template.html', c)
	
	elif request.method == "POST":

		form = forms.EmpleadoUsuarioForm(request.POST)

		if form.is_valid():
		
			datos = request.POST

			user = User.objects.create_user(datos['correo'], datos['correo'], datos['password'], first_name=datos['nombre'], last_name=datos['apellido'])
			
			user.save()

			#user = User.objects.get(username=datos['correo'])
			usuario = models.Usuario()

			usuario.usuario = user

			usuario.save()

			empleado = models.Empleado(datos)

			empleado.usuario = usuario

			empleado.save()
			
			return redirect('lista_empleados')


@login_required
@permission_required('core.change_empleado')
def editar_empleado(request, _id):
		
	if request.method == "GET":
		
		empleado = get_object_or_404(models.Empleado, pk=_id)

		form = forms.EmpleadoForm(empleado)

		empresa = getNombreEmpresa()

		c = {'empresa':empresa, 'seccion':'Empleados', 'titulo':'actualización de empleados', 'form':form, 'view':'vEditarEmpleado', 'id':_id}
		
		return render(request, 'form_template.html', c)
	
	elif request.method == "POST":
		
		empleado = models.Empleado.objects.get(pk=_id)

		form = forms.EmpleadoForm(request.POST, instance=empleado)

		if form.is_valid():

			form.save()

			return redirect('ver_empleado', {'_id':_id})



@login_required
@permission_required('core.delete_empleado')
def eliminar_empleado(request, _id):

	if request.method == "POST":

		empleado = models.Empleado.objects.get(pk=_id)

		empleado.delete()
		
		return redirect('lista_empleados')


@login_required
@permission_required('core.desactivar_empleado')
def desactivar_empleado(request, _id):

	if request.method == "POST":

		empleado = models.Empleado.objects.get(pk=_id)
		empleado.activo = False
		empleado.save()
		
		return redirect('lista_empleados')


@login_required
@permission_required('core.asignar_usuario')
def asignar_usuario(request, _id):
	
		
	if request.method == "GET":
		empleado = get_object_or_404(models.Empleado, pk=_id)
		form = forms.AsignaUsuarioForm()
		empresa = getNombreEmpresa()
		c = {'empresa':empresa, 'titulo':'Asignación de Usuario', 'seccion':'Usuarios y Emmpleados', 'empleado':empleado, 'form':form, 'view':'vAsignarUsuario', 'id':_id}
		return render(request, 'asignar_usuario.html', c)

	elif request.method == "POST":
		form = forms.AsignaUsuarioForm(request.POST)
		if form.is_valid():
			empleado = get_object_or_404(models.Empleado, pk=_id)
			usuario = get_object_or_404(models.Usuario, pk=request.POST['id_usuario'])
			empleado.usuario = usuario
			empleado.save()
			return redirect('lista_empleados')


@login_required
@permission_required('core.view_usuario')
def lista_usuarios(request, todos=None):

	usuarios = None
	empresa = getNombreEmpresa()

	if todos is None:
		usuarios = models.Usuario.objects.filter(usuario__is_active = True)
	else:
		usuarios = models.Usuario.objects.all()

	return render(request, 'lista_usuarios.html', {'titulo':'Lista de Usuarios', 'seccion':'Usuarios', 'usuarios':usuarios, 'todos':todos})


@login_required
@permission_required('core.add_usuario')
def nuevo_usuario(request):
	if request.method == 'GET':
		empresa = getNombreEmpresa()
		form = forms.UsuarioForm()
		c = {'empresa':empresa, 'titulo':'Ingreso de Usuarios', 'seccion':'Usuarios', 'form':form, 'view':'vNuevoUsuario'}
		return render(request, 'form_template.html', c)
	elif request.method == 'POST':
		form = forms.UsuarioForm(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			user.username = user.email
			user.save()
			usuario = models.Usuario()
			usuario.usuario = user
			usuario.save()
			return redirect('lista_usuarios')
		


@login_required
@permission_required('core.view_usuario')
def ver_usuario(request, _id):
	usuario = get_object_or_404(models.Usuario, pk=_id)
	empresa = getNombreEmpresa()
	c = {'empresa':getNombreEmpresa(), 'titulo':'Usuario', 'seccion':'Perfil de Usuario', 'usuario':usuario}
	return render(request, 'perfil_usuario.html', )


@login_required
@permission_required('core.cambiar_contrasena')
def password_user_change(request, _id):
	if request.method == "GET":
		empresa = getNombreEmpresa()
		form = forms.PasswordChangeForm()
		c = {'empresa':empresa, 'titulo':'Cambio de Contraseña', 'seccion':'Contraseña de Usuario', 'form':form, 'view':'vCambiarPassword', 'id':_id}
		return render(request, 'form_template.html', c)
	elif request.method == "POST":
		form = forms.PasswordChangeForm(request.POST)
		if form.is_valid():
			
			datos = request.POST
			
			if not (datos['password'] == datos['confirm_password']):
				return render(request, 'error.html', {'titulo':'Contraseña no coincide', 'mensaje':'Las contraseñas no coinciden. Revise y vuelva a intentarlo.', 'view':'vListaUsuarios', 'seccion':'Perfil de usuario'})
			else:
				user.set_password(request.POST['password'])
				user.save()
				return redirect('bison_logout')
			

@login_required
@permission_required('core.delete_usuario')
def eliminar_usuario(request, _id):
	
	if request.method == "POST":
		usuario = get_object_or_404(models.Usuario, pk=_id)
		user = usuario.usuario
		user.delete()
		usuario.delete()
		
		return redirect('lista_empleados')


@login_required
@permission_required('core.change_usuario')
def desactivar_usuario(request, _id):
	
	if request.method == "GET":
		empresa = getNombreEmpresa()
		c = {'titulo':'Desactivar Usuario', 'seccion':'Usuarios', 'empresa':empresa, 'view':'vDesactivarUsuario', 'id':_id, 'mensaje':'Se desactivará el usuario y no tendrá acceso al sistema.'}
		return render(request, 'warning_template.html', c)
	elif request.method == "POST":
		usuario = models.Usuario.objects.get(pk=_id)
		user = usuario.usuario
		user.is_valid = False
		user.save()
		return redirect('lista_usuarios')

# ADMINISTRAR CATEGORIAS DE PRODUCTOS

@login_required
@permission_required('core.view_categoria')
def lista_categorias(request):
	empresa = getNombreEmpresa()
	categorias = models.Categoria.objects.all()
	c = {'titulo':'Maestro de Categorias', 'seccion':'Categorias', 'empresa':empresa, 'categorias':categorias}
	return render(request, 'lista_categorias.html', c)


@login_required
@permission_required('core.change_categoria')
def nueva_categoria(request):
	CategoriaFormSet = modelformset_factory(models.Categoria, form=forms.CategoriaForm, extra=3)
	if request.method == "GET":
		empresa = getNombreEmpresa()
		formset = CategoriaFormSet()
		c = {'titulo':'Ingreso de Categorias', 'seccion':'Categorias', 'empresa':empresa, 'formset':formset}
		return render(request, 'formset_template.html', c)
	elif request.method == "POST":
		formset = CategoriaFormSet(request.POST)
		if formset.is_valid():
			formset.save()

			return redirect('lista_categorias')
		


@login_required
@permission_required('core.change_categoria')
def editar_categorias(request, _id):
	categorias = models.Categoria.objects.all()
	extra_fields = categorias.count()
	CategoriaFormSet = modelformset_factory(models.Categoria, form=forms.CategoriaForm, extra=extra_fields)
	if request.method == "GET":
		formset = CategoriaFormSet(initial=categorias)
		empresa = getNombreEmpresa()
		c = {'titulo':'Edición de Categorías', 'seccion':'Categorías', 'formset':formset, 'empresa':empresa, 'view':'vEditarCategorias'}
		return render(request, 'form_template.html', c)
	elif request.method == "POST":

		formset = CategoriaFormset(request.POST, initial=categorias)
		if formset.is_valid():
			formset.save()
			return redirect('lista_categorias')
		


@login_required
@permission_required('core.delete_categoria')
def eliminar_categoria(request, _id):
	if request.method == "POST":
		categoria = get_object_or_404(models.Categoria, pk=_id)
		categoria.delete()
		return redirect('lista_categorias')

# ADMINISTRAR UNIDADES DE MEDIDA

@login_required
@permission_required('core.administrar_unidad')
def lista_medidas(request):
	empresa = getNombreEmpresa()
	unidades = get_list_or_404(models.Unidad)
	c = {'titulo':'Maestro de Unidad de Medida', 'seccion':'Unidades de Medida', 'empresa':empresa, 'unidades':unidades}
	return render(request, 'lista_unidades.html', c)

@login_required
@permission_required(['core.administrar_unidad'])
def nueva_medida(request):
	UnidadFormSet = modelformset_factory(models.Unidad, form=forms.UnidadForm, extra=3)
	if request.method == "GET":
		empresa = getNombreEmpresa()
		formset = UnidadFormSet()
		c = {'titulo':'Ingreso de Unidad de Medida', 'seccion':'Unidades de Medida', 'empresa':empresa, 'formset':formset}
		return render(request, 'formset_template.html', c)
	elif request.method == "POST":
		unidadset = UnidadFormSet(request.POST)
		if unidadset.is_valid():
			unidades = unidadset.save(commit=False)
			for unidad in unidades:
				unidad.save()

			return redirect('lista_medidas')
		else:
			return render(request, 'error.html', {'titulo':'Error de Validación', 'mensaje':'Los datos ingresados no son correctos. Verifique y vuelva a intentarlo.', 'view':'vListaMedidas'})


@login_required
@permission_required('core.administrar_unidad')
def editar_medida(request, _id):
	if request.method == "GET":
		unidad = get_object_or_404(models.Unidad, pk=_id)
		form = forms.UnidadForm(unidad)
		empresa = getNombreEmpresa()
		c = {'titulo':'Edición de Unidad de Medida', 'seccion':'Unidades de Medida', 'form':form, 'empresa':empresa, 'view':'vEditarMedida', 'id':_id}
		return render(request, 'form_template.html', c)
	elif request.method == "POST":
		old_und = get_object_or_404(models.Unidad, pk=_id)
		form = forms.CategoriaForm(request.POST, instance=old_und)
		if form.is_valid():
			form.save()
			return redirect('lista_medidas')
		else:
			return render(request, 'error.html', {'titulo':'Error de Validación', 'mensaje':'Los datos ingresados no son correctos. Verifique y vuelva a intentarlo.', 'view':'vListaMedidas'})


@login_required
@permission_required('core.administrar_unidad')
def eliminar_medida(request, _id):
	if request.method == "GET":
		c = {'titulo':'Eliminar registro de Unidad de Medida', 'seccion':'Unidades de Medida', 'empresa':empresa, 'view':'vEliminarMedida', 'id':_id, 'mensaje':'Se eliminará el registro de la base de datos.'}
		return render(request, 'warning_template.html', c)
	elif request.method == "POST":
		unidad = get_object_or_404(models.Unidad, pk=_id)
		unidad.delete()
		return redirect('lista_medidas')



