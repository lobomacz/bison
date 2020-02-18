from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
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
	
	if request.method == "GET":
		
		form = LoginForm()
		return render(request, 'login.html', {'form':form})
	
	else:

		form = LoginForm(request.POST)

		if form.is_valid():
			
			uname = form.username
			password = form.password
			user = authenticate(request, 'username'=uname, 'password'=password)
			
			if user is not None:
				if user.usuario.activo == True and user.usuario.empleado != None:
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
def lista_empleados(request, page, todos=False):
	
	empleados = None

	limite = settings.LIMITE_FILAS
	
	if todos:
		empleados = models.Empleado.objects.all()
	
	else:
		empleados = models.Empleado.objects.filter(activo=True)

	if empleados != None and empleados.count() > limite:

		paginador = Paginator(empleados, limite)

		empleados = paginador.get_page(page)

	empresa = getNombreEmpresa()

	c = {'empresa':empresa, 'seccion':'Empleados', 'titulo':'listado de empleados', 'empleados':empleados, 'todos':todos}
	return render(request, 'lista_empleados.html', c)



@login_required
@permission_required('core.view_empleado')
def ver_empleado(request, _id):
		
	empleado = get_object_or_404(models.Empleado, pk=_id)
	empresa = getNombreEmpresa()
	c = {'empresa':empresa, 'seccion':'Empleados', 'titulo':'datos de empleado', 'empleado':empleado}
	return render(request, 'ver_empleado.html', c)



@login_required
@permission_required('core.add_empleado')
def nuevo_empleado(request):
	
	if request.method == "GET":
		
		form = forms.EmpleadoForm()

		empresa = getNombreEmpresa()

		c = {'empresa':empresa, 'seccion':'Empleados', 'titulo':'nuevo empleado', 'form':form, 'ruta':'vNuevoEmpleado'}
		
		return render(request, 'forms/form_template.html', c)
	
	else if request.method == "POST":
		
		form = forms.EmpleadoForm(request.POST)
		
		if form.is_valid():

			form.save()
			
			return redirect('lista_empleados')
		


@login_required
@permission_required(('core.add_empleado', 'core.add_usuario', 'core.asignar_usuario'))
def nuevo_empleado_usuario(request):
	
	if request.method == "GET":
		
		form = forms.EmpleadoUsuarioForm()

		empresa = getNombreEmpresa()

		c = {'empresa':empresa, 'seccion':'Empleados', 'titulo':'registro de empleado con usuario', 'form':form, 'ruta':'vNuevoEmpleadoUsuario'}
		
		return render(request, 'forms/form_template.html', c)
	
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

		c = {'empresa':empresa, 'seccion':'Empleados', 'titulo':'edición de datos de empleado', 'form':form, 'ruta':'vEditarEmpleado', 'id':_id}
		
		return render(request, 'core/form_template.html', c)
	
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

		usuario = empleado.usuario

		if usuario != None:
			usuario.usuario.delete()

		empleado.delete()
		
		return redirect('lista_empleados')


@login_required
@permission_required('core.desactivar_empleado')
def desactivar_empleado(request, _id):

	if request.method == "POST":

		empleado = models.Empleado.objects.get(pk=_id)
		usuario = empleado.usuario
		empleado.activo = False
		usuario.activo = False
		empleado.save()
		usuario.save()
		
		return redirect('lista_empleados')


@login_required
@permission_required('core.asignar_usuario')
def asignar_usuario(request, _id):
		
	if request.method == "GET":
		empleado = get_object_or_404(models.Empleado, pk=_id)
		form = forms.AsignaUsuarioForm()
		empresa = getNombreEmpresa()
		c = {'empresa':empresa, 'titulo':'Asignación de Usuario', 'seccion':'Usuarios y Emmpleados', 'empleado':empleado, 'form':form, 'ruta':'vAsignarUsuario', 'id':_id}
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
def lista_usuarios(request, page, todos=None):

	usuarios = None
	limite = settings.LIMITE_FILAS
	empresa = getNombreEmpresa()

	if todos is None:
		usuarios = models.Usuario.objects.filter(usuario__is_active = True)
	else:
		usuarios = models.Usuario.objects.all()

	if usuarios != None and usuarios.count() > limite:
		
		paginador = Paginator(limite)

		usuarios = paginador.get_page(page)

	return render(request, 'lista_usuarios.html', {'titulo':'Lista de Usuarios', 'seccion':'Usuarios', 'usuarios':usuarios, 'todos':todos})


@login_required
@permission_required('core.add_usuario')
def nuevo_usuario(request):

	if request.method == 'GET':

		empresa = getNombreEmpresa()
		form = forms.UsuarioForm()

		c = {'empresa':empresa, 'titulo':'Ingreso de Usuarios', 'seccion':'Usuarios', 'form':form, 'ruta':'vNuevoUsuario'}
		
		return render(request, 'forms/form_template.html', c)

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
def editar_usuario(request, _id):

	usuario = get_object_or_404(models.User, pk=_id)

	if request.method == "GET":
		
		form = forms.UsuarioForm(usuario)
		empresa = getNombreEmpresa()

		c = {'empresa':getNombreEmpresa(), 'titulo':'Usuario', 'seccion':'Perfil de Usuario', 'form':form, 'ruta':'vEditarUsuario', 'id':_id}
		
		return render(request, 'forms/form_template.html', c)

	elif request.method == "POST":

		form = forms.UsuarioForm(request.POST, instance=usuario)

		if form.is_valid():

			user = form.save(commit=False)
			user.username = user.email

			user.save()

			return redirect('index')


@login_required
@permission_required('core.password_usuario')
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
		
		usuario.usuario.delete()
		
		return redirect('lista_empleados')


@login_required
@permission_required('core.change_usuario')
def desactivar_usuario(request, _id):
	
	usuario = get_object_or_404(models.Usuario, pk=_id)
	user = usuario.usuario

	user.is_valid = False
	usuario.activo = False

	user.save()
	usuario.save()

	return redirect('lista_usuarios')

# ADMINISTRAR CATEGORIAS DE PRODUCTOS

@login_required
@permission_required('core.administrar_categoria')
def lista_categorias(request):

	empresa = getNombreEmpresa()
	categorias = models.Categoria.objects.all()


	c = {'titulo':'Maestro de Categorias', 'seccion':'Categorias', 'empresa':empresa, 'categorias':categorias}

	return render(request, 'lista_categorias.html', c)


@login_required
@permission_required('core.add_categoria')
def nueva_categoria(request):

	CategoriaFormSet = modelformset_factory(models.Categoria, form=forms.CategoriaForm, extra=3)

	if request.method == "GET":

		empresa = getNombreEmpresa()
		formset = CategoriaFormSet()

		c = {'titulo':'Ingreso de Categorias', 'seccion':'Categorias', 'empresa':empresa, 'formset':formset, 'ruta':'vNuavaCategoria'}
		
		return render(request, 'formset_template.html', c)

	elif request.method == "POST":

		formset = CategoriaFormSet(request.POST)

		if formset.is_valid():
			
			formset.save()

			return redirect('lista_categorias', {'page':1})
		


@login_required
@permission_required('core.change_categoria')
def editar_categorias(request):

	categorias = models.Categoria.objects.all()
	extra_fields = 4 if categorias.count() > 0 else 3

	CategoriaFormSet = modelformset_factory(models.Categoria, form=forms.CategoriaForm, extra=extra_fields)

	if request.method == "GET":

		formset = CategoriaFormSet(initial=categorias)
		empresa = getNombreEmpresa()

		c = {'titulo':'Edición de Categorías', 'seccion':'Categorías', 'formset':formset, 'empresa':empresa, 'ruta':'vEditarCategorias'}
		
		return render(request, 'formset_template.html', c)

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

		formset = UnidadFormSet(request.POST)

		if formset.is_valid():

			unidades = formset.save()

			return redirect('lista_medidas')
		

@login_required
@permission_required('core.administrar_unidad')
def editar_medida(request, _id):

	unidades = models.Unidad.objects.all()
	extra_fields = 4 if unidades.count() > 0 else 3

	UnidadFormSet = modelformset_factory(models.Unidad, form=forms.UnidadForm, extra=extra_fields)

	if request.method == "GET":

		formset = UnidadFormSet(initial=unidades)
		empresa = getNombreEmpresa()

		c = {'titulo':'Edición de Unidad de Medida', 'seccion':'Unidades de Medida', 'formset':formset, 'empresa':empresa, 'ruta':'vEditarMedida'}
		
		return render(request, 'formset_template.html', c)

	elif request.method == "POST":

		formset = UnidadFormSet(request.POST, initial=unidades)

		if formset.is_valid():

			formset.save()

			return redirect('lista_medidas')
		

@login_required
@permission_required('core.administrar_unidad')
def eliminar_medida(request, _id):
	
	if request.method == "POST":

		unidad = get_object_or_404(models.Unidad, pk=_id)

		unidad.delete()

		return redirect('lista_medidas')



