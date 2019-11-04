from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied, BadRequest
from django.http import Http404
from django.conf import settings
from django.apps import apps
from django.forms import formset_factory, modelformset_factory
from . import forms, models

# Create your views here.

@login_required
def index(request):
	empresa = settings.NOMBRE_EMPRESA
	groups = request.user.groups
	empleado = None
	usuario = get_object_or_404(models.Usuario, usuario__id=request.user.id)
	empleado = usuario.empleado
	c = {
	'empresa':empresa, 
	'seccion':'inicio', 
	'titulo':'página de inicio', 
	'groups':groups, 
	'empleado':empleado, 
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
@permission_required('core.administrar_empleados')
def lista_empleados(request, todos=False):
	
	empleados = None
	
	if todos:
		empleados = models.Empleado.objects.all()
	
	else:
		empleados = models.Empleado.objects.filter(activo=True)

	if not empleados:
		raise Http404('No se encontraron registros en la base de datos.')

	empresa = settings.NOMBRE_EMPRESA
	c = {'empresa':empresa, 'seccion':'Empleados', 'titulo':'listado de empleados', 'empleados':empleados, 'todos':todos}
	return render(request, 'lista_empleados.html', c)


@login_required
@permission_required('core.view_empleado')
def ver_empleado(request, id_emp):
	
	if id_emp is not None:
		
		empleado = get_object_or_404(models.Empleado, pk=id_emp)
		empresa = settings.NOMBRE_EMPRESA
		c = {'empresa':empresa, 'seccion':'Empleados', 'titulo':'datos de empleado', 'empleado':empleado}
		return render(request, 'detalle_empleado.html', c)
	
	else:
		c = {'titulo':'Id Incorrecto', 'mensaje':'El id de empleado no pertenece a ningún registro.', 'view':'vListaEmpleados'}
		return render(request, 'error.html', c)


@login_required
@permission_required('core.add_empleado')
def nuevo_empleado(request):
	
	if request.method == "GET":
		
		form = forms.EmpleadoForm()
		empresa = settings.NOMBRE_EMPRESA
		c = {'empresa':empresa, 'seccion':'Empleados', 'titulo':'registro de empleados', 'form':form, 'view':'vNuevoEmpleado'}
		
		return render(request, 'form_template.html', c)
	
	else if request.method == "POST":
		
		form = forms.EmpleadoForm(request.POST)
		
		if form.is_valid():
			form.save()
			
			return redirect('vEmpleados', {'mensaje':'El registro de aplicó con éxito.'})
		else:
			c = {'titulo':'Error de Datos', 'mensaje':'Los datos ingresados no son válidos.', 'view':'vListaEmpleados'}
			
			return render(request, 'error.html', c)


@login_required
@permission_required(('core.add_empleado', 'core.administrar_usuarios', 'core.asignar_usuario'))
def nuevo_empleado_usuario(request):
	
	if request.method == "GET":
		
		form = forms.EmpleadoUsuarioForm()
		empresa = settings.NOMBRE_EMPRESA
		c = {'empresa':empresa, 'seccion':'Empleados con Usuario', 'titulo':'registro de empleado con usuario', 'form':form, 'view':'vNuevoEmpleadoUsuario'}
		
		return render(request, 'form_template.html', c)
	
	elif request.method == "POST":
		
		datos = request.POST
		user = User.objects.create_user(datos['correo'], datos['correo'], datos['password'], first_name=datos['nombre'], last_name=datos['apellido'])
		user.save()
		user = User.objects.get(username=datos['correo'])
		empleado = models.Empleado(datos)
		empleado.usuario = user
		empleado.save()
		
		return redirect('lista_empleados')


@login_required
@permission_required('core.administrar_empleados')
def editar_empleado(request, id_emp):
	
	if id_emp == None:
		return render(request, 'error.html', {'titulo':'Error de Registro', 'mensaje':'El ID no corresponde a ningún registro.', 'view':'vListaEmpleados'})
	
	else:
		
		if request.method == "GET":
			
			empleado = get_object_or_404(models.Empleado, pk=id_emp)
			form = forms.EmpleadoForm(empleado)
			empresa = settings.NOMBRE_EMPRESA
			action = 
			c = {'empresa':empresa, 'seccion':'Empleados', 'titulo':'actualización de empleados', 'form':form, 'view':'vEditarEmpleado', 'id':id_emp}
			
			return render(request, 'form_template.html', c)
		
		elif request.method == "POST":
			
			empleado = models.Empleado.objects.get(pk=id_emp)
			formEmpleado = forms.EmpleadoForm(request.POST, instance=empleado)
			formEmpleado.save()
			return redirect('ver_empleado', {'id_emp':id_emp})


@login_required
@permission_required('core.administrar_empleados')
def eliminar_empleado(request, _id):
	if _id == None:
		return render(request, 'error.html', {'titulo':'Error de Registro', 'mensaje':'El ID no corresponde a ningún registro.'})
	else:
		if request.method == "GET":
			empresa = settings.NOMBRE_EMPRESA
			c = {'empresa':empresa, 'seccion':'Empleados', 'titulo':'Eliminar Empleado', 'mensaje':'Se va a eliminar un registro de la base de datos.', 'view':'vElimnarEmpleado', 'id':_id}
			return render(request, 'warning_template.html', c)
		
		elif request.method == "POST":
			empleado = models.Empleado.objects.get(pk=_id)
			empleado.delete()
			return redirect('lista_empleados')


@login_required
@permission_required('core.administrar_usuarios')
def desactivar_empleado(request, _id):

	if _id == None:

		return render(request, 'error.html', {'titulo':'Error de Acceso', 'mensaje':'El ID no es válido. Verifique y vuelva a intentarlo.'})

	if request.method == "GET":

		empresa = settings.NOMBRE_EMPRESA

		c = {'titulo':'Desactivar Usuario', 'seccion':'Usuarios', 'mensaje':'Se desactivará el usuario y no tendrá acceso.', 'empresa':empresa, 'view':'vDesactivarEmpleado', 'id':_id}
		
		return render(request, 'warning_template.html', c)
	
	elif request.method == "POST":

		empleado = models.Empleado.objects.get(pk=_id)
		empleado.activo = False
		empleado.save()
		
		return redirect('lista_empleados')


@login_required
@permission_required('core.asignar_usuario')
def asignar_usuario(request, id_emp):
	
	if id_emp == None:
		
		return render(request, 'error.html', {'titulo':'Error de Registro', 'mensaje':'El ID no corresponde a ningún registro.'})
	
	else:
		
		if request.method == "GET":
			empleado = get_object_or_404(models.Empleado, pk=id_emp)
			form = forms.AsignaUsuarioForm()
			empresa = settings.NOMBRE_EMPRESA
			c = {'empresa':empresa, 'titulo':'Asignación de Usuario', 'seccion':'Usuarios y Emmpleados', 'empleado':empleado, 'form':form, 'view':'vAsignarUsuario'}
			return render(request, 'asignar_usuario.html', c)

		elif request.method == "POST":
			empleado = get_object_or_404(models.Empleado, pk=id_emp)
			usuario = get_object_or_404(models.Usuario, pk=request.POST['id_usuario'])
			empleado.usuario = usuario
			empleado.save()
			return redirect('lista_empleados')


@login_required
@permission_required(['core.view_usuario', 'core.administrar_usuarios'])
def lista_usuarios(request, todos=None):

	usuarios = None
	empresa = settings.NOMBRE_EMPRESA

	if todos is None:
		usuarios = models.Usuario.objects.filter(usuario__is_active = True)
	else:
		usuarios = models.Usuario.objects.all()

	if not usuarios:
		raise Http404('No se encontraron registros en la base de datos.')

	return render(request, 'lista_usuarios.html', {'titulo':'Lista de Usuarios', 'seccion':'Usuarios', 'usuarios':usuarios, 'todos':todos})


@login_required
@permission_required(['core.administrar_usuarios', 'core.add_usuario'])
def nuevo_usuario(request):
	if request.method == 'GET':
		empresa = settings.NOMBRE_EMPRESA
		form = forms.UsuarioForm()
		c = {'empresa':empresa, 'titulo':'Ingreso de Usuarios', 'seccion':'Usuarios', 'form':form, 'view':'vNuevoUsuario'}
		return render(request, 'form_template.html', c)
	elif request.method == 'POST':
		user_form = forms.UsuarioForm(request.POST)
		if user_form.is_valid():
			user = user_form.save(commit=False)
			user.username = user.email
			user.save()
			user = get_object_or_404(User, username=user.username)
			usuario = models.Usuario()
			usuario.usuario = user
			usuario.save()
			return redirect('lista_usuarios')
		else:
			return render(request, 'error.html', {'titulo':'Error de Validación', 'mensaje':'Los datos presentan inconsistencia. Por favor, vuelva a intentarlo más tarde.', 'view':'vListaUsuarios'})


@login_required
@permission_required('core.view_usuario')
def ver_usuario(request, id_usuario):
	if not request.user.id == id_usuario:
		return render(request, 'error.html', {'titulo':'Error de Acceso', 'mensaje':'El ID no corresponde a su ID de usuario. Verifique y vuelva a intentarlo.', 'view':'vListaUsuarios'})
	else:
		empleado = models.Empleado.objects.filter(usuario__usuario__id=id_usuario)
		empresa = settings.NOMBRE_EMPRESA
		contexto = {'empresa':empresa, 'titulo':'Usuario', 'seccion':'Detalles de Usuario', 'empleado':empleado}
		return render(request, 'detalle_usuario.html', )


@login_required
@permission_required('core.cambiar_contrasena')
def password_user_change(request, id_usuario):
	if not request.user.id == id_usuario:
		return render(request, 'error.html', {'titulo':'Error de Acceso', 'mensaje':'El ID no corresponde a su ID de usuario. Verifique y vuelva a intentarlo.', 'view':'vListaUsuarios'})
	else:
		if request.method == "GET":
			empresa = settings.NOMBRE_EMPRESA
			form = forms.PasswordChangeForm()
			c = {'empresa':empresa, 'titulo':'Cambio de Contraseña', 'seccion':'Contraseña de Usuario', 'form':form, 'view':'vCambiarPassword', 'id':id_usuario}
			return render(request, 'form_template.html', c)
		elif request.method == "POST":
			datos = request.POST
			user = authenticate(username=datos['username'], password=datos['old_password'])
			if user is not None:
				if not datos['password'] == datos['confirm_password']:
					return render(request, 'error.html', {'titulo':'Contraseña no coincide', 'mensaje':'Las contraseñas no coinciden. Revise y vuelva a intentarlo.', 'view':'vListaUsuarios'})
				else:
					user.set_password(request.POST['password'])
					user.save()
					return redirect('bison_logout')
			else:
				return render(request, 'error.html', {'titulo':'Error de Validación', 'mensaje':'Los datos de usuario/contraseña no son correctos. Verifique y vuelva a intentarlo.', 'view':'vListaUsuarios'})


@login_required
@permission_required(['core.delete_usuario', 'core.administrar_usuarios'])
def eliminar_usuario(request, _id):
	if _id == None:
		return render(request, 'error.html', {'titulo':'Error de Acceso', 'mensaje':'El ID no corresponde a un ID de usuario. Verifique y vuelva a intentarlo.', 'view':'vListaUsuarios'})
	else:
		if request.method == "GET":
			empresa = settings.NOMBRE_EMPRESA
			c = {'titulo':'Eliminar registro de Usuario', 'seccion':'Usuarios', 'empresa':empresa, 'view':'vEliminarUsuario', 'id':_id, 'mensaje':'Se eliminará el registro de la base de datos.'}
			return render(request, 'warning_template.html', c)
		elif request.method == "POST":
			usuario = get_object_or_404(models.Usuario, pk=_id)
			user = usuario.usuario
			user.delete()
			
			return redirect('lista_usuarios')


@login_required
@permission_required('core.administrar_usuarios')
def desactivar_usuario(request, _id):
	if _id == None:
		return render(request, 'error.html', {'titulo':'Error de Acceso', 'mensaje':'El ID no corresponde a un ID de usuario. Verifique y vuelva a intentarlo.'})

	if request.method == "GET":
		empresa = settings.NOMBRE_EMPRESA
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
@permission_required('core.administrar_categorias')
def lista_categorias(request):
	empresa = settings.NOMBRE_EMPRESA
	categorias = models.Categoria.objects.all()
	c = {'titulo':'Maestro de Categorias', 'seccion':'Categorias', 'empresa':empresa, 'categorias':categorias}
	return render(request, 'lista_categorias.html', c)


@login_required
@permission_required('core.administrar_categorias')
def nueva_categoria(request):
	CategoriaFormSet = modelformset_factory(models.Categoria, form=forms.CategoriaForm, extra=3)
	if request.method == "GET":
		empresa = settings.NOMBRE_EMPRESA
		formset = CategoriaFormSet()
		c = {'titulo':'Ingreso de Categorias', 'seccion':'Categorias', 'empresa':empresa, 'formset':formset}
		return render(request, 'formset_template.html', c)
	elif request.method == "POST":
		categoriaset = CategoriaFormSet(request.POST)
		if categoriaset.is_valid():
			categorias = categoriaset.save(commit=False)
			for categoria in categorias:
				categoria.save()

			return redirect('lista_categorias')
		else:
			return render(request, 'error.html', {'titulo':'Error de Validación', 'mensaje':'Los datos ingresados no son correctos. Verifique y vuelva a intentarlo.'})


@login_required
@permission_required('core.administrar_categorias')
def editar_categoria(request, _id):
	if request.method == "GET":
		categoria = get_object_or_404(models.Categoria, pk=_id)
		form = forms.CategoriaForm(categoria)
		empresa = settings.NOMBRE_EMPRESA
		c = {'titulo':'Edición de Categoría', 'seccion':'Categorías', 'form':form, 'empresa':empresa, 'view':'vEditarCategoria', 'id':_id}
		return render(request, 'form_template.html', c)
	elif request.method == "POST":
		old_cat = get_object_or_404(models.Categoria, pk=_id)
		form = forms.CategoriaForm(request.POST, instance=old_cat)
		if form.is_valid():
			form.save()
			return redirect('lista_categorias')
		else:
			return render(request, 'error.html', {'titulo':'Error de Validación', 'mensaje':'Los datos ingresados no son correctos. Verifique y vuelva a intentarlo.', 'view':'vListaCategorias'})



@login_required
@permission_required('core.administrar_categorias')
def eliminar_categoria(request, _id):
	if request.method == "GET":
		c = {'titulo':'Eliminar registro de Categoria', 'seccion':'Categorías', 'empresa':empresa, 'view':'vEliminarCategoria', 'id':_id, 'mensaje':'Se eliminará el registro de la base de datos.'}
		return render(request, 'warning_template.html', c)
	elif request.method == "POST":
		categoria = get_object_or_404(models.Categoria, pk=_id)
		categoria.delete()
		return redirect('lista_categorias')

# ADMINISTRAR UNIDADES DE MEDIDA

@login_required
@permission_required('core.administrar_unidad')
def lista_medidas(request):
	empresa = settings.NOMBRE_EMPRESA
	unidades = get_list_or_404(models.Unidad)
	c = {'titulo':'Maestro de Unidad de Medida', 'seccion':'Unidades de Medida', 'empresa':empresa, 'unidades':unidades}
	return render(request, 'lista_unidades.html', c)

@login_required
@permission_required(['core.administrar_unidad'])
def nueva_medida(request):
	UnidadFormSet = modelformset_factory(models.Unidad, form=forms.UnidadForm, extra=3)
	if request.method == "GET":
		empresa = settings.NOMBRE_EMPRESA
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
		empresa = settings.NOMBRE_EMPRESA
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



