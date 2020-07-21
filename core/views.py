from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.urls import reverse
from django.contrib import messages
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
import logging

# Create your views here.


@login_required
def index(request):

	empresa = settings.NOMBRE_EMPRESA

	c = {
	'empresa':empresa, 
	'seccion':'inicio', 
	'titulo':'página de inicio', 

	}

	return render(request, 'core/indice.html', c)


def bison_login(request):
	
	if request.method == "GET":
		
		form = LoginForm()

		return render(request, 'core/login.html', {'form':form})
	
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

'''
@login_required
def error(request):

	return render(request, 'core/error.html')
'''


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

	empresa = settings.NOMBRE_EMPRESA

	c = {'empresa':empresa, 'seccion':'Empleados', 'titulo':'listado de empleados', 'empleados':empleados, 'todos':todos}
	
	return render(request, 'core/lista_empleados.html', c)



@login_required
@permission_required('core.view_empleado')
def ver_empleado(request, _id):
		
	empleado = get_object_or_404(models.Empleado, pk=_id)

	empresa = settings.NOMBRE_EMPRESA

	ruta_delete = reverse('vEliminarEmpleado', {'_id':empleado.cedula})

	ruta_edit = reverse('vEditarEmpleado', {'_id':empleado.cedula})

	c = {'empresa':empresa, 'seccion':'Empleados', 'titulo':'datos de empleado', 'empleado':empleado, 'ruta_edit':ruta_edit, 'ruta_delete':ruta_delete}
	
	return render(request, 'core/ver_empleado.html', c)



@login_required
@permission_required('core.add_empleado')
def nuevo_empleado(request):
	
	if request.method == "GET":
		
		form = forms.EmpleadoForm()

		ruta = reverse('vNuevoEmpleado')

		empresa = settings.NOMBRE_EMPRESA

		c = {'empresa':empresa, 'seccion':'Empleados', 'titulo':'nuevo empleado', 'form':form, 'ruta':ruta}

		messages.info(request, 'Los campos con * son obligatorios')
		
		return render(request, 'core/forms/form_template.html', c)
	
	else if request.method == "POST": 
		
		form = forms.EmpleadoForm(request.POST)

		empleado = None
		
		if form.is_valid():

			try:
				
				empleado = form.save(commit=False)

				empleado.save()

			except Exception as e:
				
				messages.error(request,"Excepción al registrar empleado.")

				logging.error(e)

				return redirect('lista_empleados')
			
			messages.success(request,"Empleado ingresado con éxito")

			return redirect('ver_empleado', {'_id':empleado.cedula})

		


@login_required
@permission_required(('core.add_empleado', 'core.add_usuario', 'core.asignar_usuario'))
def nuevo_empleado_usuario(request):
	
	if request.method == "GET":
		
		form = forms.EmpleadoUsuarioForm()

		ruta = reverse('vNuevoEmpleadoUsuario')

		empresa = settings.NOMBRE_EMPRESA

		c = {'empresa':empresa, 'seccion':'Empleados', 'titulo':'registro de empleado con usuario', 'form':form, 'ruta':ruta}

		messages.info(request, 'Los campos con * son obligatorios')
		
		return render(request, 'core/forms/form_template.html', c)
	
	elif request.method == "POST":

		form = forms.EmpleadoUsuarioForm(request.POST)

		if form.is_valid(): 
		
			datos = form.cleaned_data #request.POST

			user = None

			empleado = None

			try:
			
				user = User.objects.create_user(datos['correo'], datos['correo'].upper().strip(), datos['password'], first_name=datos['nombre'].upper().strip(), last_name=datos['apellido'].upper().strip())

				empleado = form.save(commit=False) # models.Empleado(datos)

				empleado.usuario = user

				empleado.save()

			except Exception as e:
				
				messages.error(request,"Excepción al registrar empleado.")

				logging.error(e)

				return redirect(reverse('vError'))

			messages.success(request,"Empleado registrado con éxito")

			return redirect('ver_empleado', {'_id':empleado.cedula})

			


@login_required
@permission_required('core.change_empleado')
def editar_empleado(request, _id):
		
	if request.method == "GET":
		
		empleado = get_object_or_404(models.Empleado, pk=_id)

		ruta = reverse('vEditarEmpleado', kwargs={'_id':empleado.cedula})

		form = forms.EditEmpleadoForm(empleado)

		empresa = settings.NOMBRE_EMPRESA

		c = {'empresa':empresa, 'seccion':'Empleados', 'titulo':'edición de datos de empleado', 'form':form, 'ruta':ruta}

		messages.info(request, 'Los campos con * son obligatorios')
		
		return render(request, 'core/forms/form_template.html', c)
	
	elif request.method == "POST": 
		
		empleado = models.Empleado.objects.get(pk=_id)

		form = forms.EditEmpleadoForm(request.POST, instance=empleado)

		if form.is_valid():

			try:
				
				form.save()

			except Exception as e:
				
				messages.error(request,"Excepción al actualizar registro de empleado")

				logging.error(e)

				return redirect(reverse('vError'))
			
			messages.success(request, "El registro se actualizó con éxito")

			return redirect('ver_empleado', {'_id':_id})



@login_required
@permission_required('core.delete_empleado')
def eliminar_empleado(request, _id):

	if request.method == "POST": # Pendiente de mejorar con bloque try/except

		empleado = models.Empleado.objects.get(pk=_id)

		usuario = empleado.usuario

		try:
		
			if usuario != None:
				usuario.delete()

				empleado.delete()

		except Exception as e:
			
			messages.error(request,"Excepción al eliminar empleado.")

			logging.error(e)

			return redirect(reverse('vError'))

		messages.success(request, 'Registro eliminado con éxito')
		
		return redirect('lista_empleados', {'page':1})


@login_required
@permission_required('core.desactivar_empleado')
def desactivar_empleado(request, _id):

	if request.method == "POST":

		empleado = models.Empleado.objects.get(pk=_id)

		usuario = empleado.usuario

		empleado.activo = False

		try:
			
			if usuario != None:
			
				usuario.is_active = False
				usuario.save()

			empleado.save()

		except Exception as e:
			
			messages.error(request,"Excepción al desactivar empleado.")

			logging.error(e)

			return redirect(reverse('vError'))
		
		messages.success(request,'El empleado ha sido desactivado con éxito')
		
		return redirect('lista_empleados', {'page':1})

@login_required
@permission_required('view.user')
def lista_usuarios(request):

	empresa = settings.NOMBRE_EMPRESA

	usuarios = User.objects.filter(is_superuser=False)

	c = {'seccion':'Usuarios', 'titulo':'Lista de Usuarios', 'empresa':empresa, 'usuarios':'usuarios'}

	return render(request, 'core/lista_usuarios.html', c)


@login_required
@permission_required('add.user')
def nuevo_usuario(request):

	if request.method == 'GET':
		
		empresa = settings.NOMBRE_EMPRESA

		form = forms.UsuarioForm()

		ruta = reverse('vNuevoUsuario')

		c = {'seccion':'Usuarios', 'titulo':'Ingreso de Usuario', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, 'Los campos con * son obligatorios')

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == 'POST':
		
		form = forms.UsuarioForm(request.POST)

		if form.is_valid():
			
			datos = form.cleaned_data

			usuario = None

			try:
				
				usuario = User.objects.create_user(datos['correo'], datos['correo'], datos['contrasena'], first_name=datos['nombre'], last_name=datos['apellido'])
			
			except Exception as e:
				
				messages.error(request,"Excepción al crear usuario")

				logging.error(e)

				return redirect(reverse('vError'))

			return redirect('lista_usuarios', {'page':1})



@login_required
@permission_required('change_user')
def editar_usuario(request, _id):

	usuario = get_object_or_404(User, pk=_id)

	if request.method == 'GET':
		
		empresa = settings.NOMBRE_EMPRESA

		form = forms.UserForm(usuario)

		ruta = reverse('vEditarUsuario', kwargs={'_id':_id})

		c = {'seccion':'Usuarios', 'titulo':'Editar Usuario', 'empresa':empresa, 'ruta':ruta, 'form':form}

		messages.info(request, 'Los campos con * son obligatorios')

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == 'POST':
		
		form = forms.UserForm(request.POST, instance=usuario)

		if form.is_valid():
			
			try:
				
				form.save()

			except Exception as e:
				
				messages.error(request,"Excepción al crear usuario")

				logging.error(e)

				return redirect(reverse('vError'))

			messages.success(request, 'El usuario se actualizó con éxito')

			return redirect('lista_usuarios', {'page':1})



@login_required
@permission_required('core.change_empleado')
def asignar_usuario(request, _id):

	empleado = get_object_or_404(models.Empleado, pk=_id)
		
	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		form = forms.AsignaUsuarioForm(initial={'id_empleado':empleado.cedula})

		ruta = reverse('vAsignarUsuario', kwargs={'_id':empleado.cedula})

		c = {'empresa':empresa, 'titulo':'Asignación de Usuario', 'seccion':'Empleados', 'empleado':empleado, 'ruta':ruta, 'form':form}
		
		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":

		form = forms.AsignaUsuarioForm(request.POST)

		if form.is_valid(): 

			try:
				
				datos = form.cleaned_data

				usuario = get_object_or_404(User, pk=datos['id_usuario'])

				empleado.usuario = usuario

				empleado.save()

			except Exception as e:
				
				messages.error(request,"Excepción al asignar usuario al empleado. %s" % (empleado.cedula))

				logging.error(e)

				return redirect(reverse('vError'))

			messages.success(request, 'El usuario se asignó con éxito')

			return redirect('ver_empleado', {'_id':_id})
		
		


@login_required
def password_user_change(request):

	user = request.user

	if request.method == "GET":

		empresa = settings.NOMBRE_EMPRESA

		empleado = user.empleado

		form = forms.PasswordChangeForm()

		ruta = reverse('vCambiarPassword', kwargs={'_id':_id})

		c = {'empresa':empresa, 'titulo':'Cambio de Contraseña', 'seccion':'Contraseña de Usuario', 'form':form, 'ruta':ruta, 'empleado':empleado}
		
		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST": 

		form = forms.PasswordChangeForm(request.POST)

		if form.is_valid():

			try:
				
				datos = form.cleaned_data #request.POST

				user.set_password(datos['password'])

				user.save()

			except Exception as e:
				
				messages.error(request,"Excepción al cambiar contaseña de usuario.")

				logging.error(e)

				return redirect(reverse('vError'))
			
			messages.success(request, 'La contraseña se cambió con éxito. Ingrese con su nueva contraseña.')

			return redirect('bison_logout')



@login_required
@permission_required('change_user')
def desactivar_usuario(request, _id):

	#user = None

	if request.method == "POST": 

		user = get_object_or_404(User, pk=_id)

			if not (user.empleado is None):

				try:
			
					user.is_valid = False

					user.save()

				except Exception as e:
					
					messages.error(request,"Excepción al cambiar contaseña de usuario.")

					logging.error(e)

					return redirect(reverse('vError'))
			
				messages.success(request, 'Usuario desactivado con éxito')

				return redirect('ver_empleado', {'_id':user.empleado.cedula})

			else:

				messages.error(request, 'El usuario no ha sido asignado')

				return redirect('lista_usuarios')

		


# ADMINISTRAR CATEGORIAS DE PRODUCTOS

@login_required
@permission_required('core.view_categoria')
def lista_categorias(request, page):

	empresa = settings.NOMBRE_EMPRESA

	limite = settings.LIMITE_FILAS

	categorias = models.Categoria.objects.all()

	if categorias.count() > limite:

		paginador = Paginator(categorias, limite)

		categorias = paginador.get_page(page)

	c = {'titulo':'Maestro de Categorias', 'seccion':'Categorias', 'empresa':empresa, 'categorias':categorias}

	return render(request, 'core/lista_categorias.html', c)


@login_required
@permission_required('core.add_categoria')
def nueva_categoria(request):

	CategoriaFormSet = modelformset_factory(models.Categoria, form=forms.CategoriaForm, extra=3)

	if request.method == "GET":

		empresa = settings.NOMBRE_EMPRESA

		formset = CategoriaFormSet()

		ruta = reverse('vNuavaCategoria')

		c = {'titulo':'Ingreso de Categorias', 'seccion':'Categorias', 'empresa':empresa, 'formset':formset, 'ruta':ruta}

		messages.info(request, 'Los campos con * son obligatorios')
		
		return render(request, 'core/forms/formset_template.html', c)

	elif request.method == "POST": # Pendiente de mejorar con bloque try/except

		formset = CategoriaFormSet(request.POST)

		if formset.is_valid():

			try:
				
				formset.save()

			except Exception as e:
				
				messages.error(request,"Excepción al ingresar categorias")

				logging.error(e)

				return redirect(reverse('vError'))
			
			messages.success(request, 'Los datos se ingresaron con éxito')

			return redirect('lista_categorias', {'page':1})
		


@login_required
@permission_required('core.change_categoria')
def editar_categoria(request, _id):

	categoria = get_object_or_404(models.Categoria, pk=_id)

	if request.method == "GET":

		form = forms.EditCategoriaForm(categoria)

		empresa = settings.NOMBRE_EMPRESA

		ruta = reverse('vEditarCategoria', kwargs={'_id':_id})

		c = {'titulo':'Edición de Categorías', 'seccion':'Categorías', 'form':form, 'empresa':empresa, 'ruta':ruta}

		messages.info(request, 'Los campos con * son obligatorios')
		
		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST": # Pendiente de mejorar con bloque try/except

		form = forms.EditCategoriaForm(request.POST, instance=categoria)

		if form.is_valid():

			try:
				
				form.save()

			except Exception as e:
				
				messages.error(request,"Excepción al actualizar categoria")

				logging.error(e)

				return redirect(reverse('vError'))
			
			messages.success(request, 'El registro se actualizó con éxito')

			return redirect('lista_categorias', {'page':1})
		


@login_required
@permission_required('core.delete_categoria')
def eliminar_categoria(request, _id):

	if request.method == "POST": # Pendiente de mejorar con bloque try/except

		categoria = get_object_or_404(models.Categoria, pk=_id)

		categoria.delete()

		return redirect('lista_categorias', {'page':1})


# ADMINISTRAR UNIDADES DE MEDIDA

@login_required
@permission_required('core.view_unidad')
def lista_medidas(request, page=1):

	empresa = settings.NOMBRE_EMPRESA

	limite = settings.LIMITE_FILAS

	unidades = models.Unidad.objects.all() #get_list_or_404(models.Unidad)

	if unidades.count() > limite:

		paginador = Paginator(unidades, limite)

		unidades = paginador.get_page(page)

	c = {'titulo':'Maestro de Unidad de Medida', 'seccion':'Unidades de Medida', 'empresa':empresa, 'unidades':unidades}
	
	return render(request, 'core/lista_unidades.html', c)


@login_required
@permission_required(['core.add_unidad'])
def nueva_medida(request):

	UnidadFormSet = modelformset_factory(models.Unidad, form=forms.UnidadForm, extra=3)

	if request.method == "GET":

		empresa = settings.NOMBRE_EMPRESA

		formset = UnidadFormSet()

		ruta = reverse('vNuevaMedida')

		c = {'titulo':'Ingreso de Unidad de Medida', 'seccion':'Unidades de Medida', 'empresa':empresa, 'formset':formset, 'ruta':ruta}

		messages.info(request, 'Los campos con * son obligatorios')
		
		return render(request, 'core/forms/formset_template.html', c)

	elif request.method == "POST": # Pendiente de mejorar con bloque try/except

		formset = UnidadFormSet(request.POST)

		if formset.is_valid():

			try:
				
				formset.save()

			except Exception as e:
				
				messages.error(request,"Excepción al ingresar categorias")

				logging.error(e)

				return redirect(reverse('vError'))
			
			messages.success(request, 'Los datos se ingresaron con éxito')

			return redirect('lista_medidas', {'page':1})

			
		

@login_required
@permission_required('core.change_unidad')
def editar_medida(request, _id):

	unidad = get_object_or_404(models.Unidad, pk=_id)

	if request.method == "GET":

		form = forms.EditUnidadForm(unidad)

		empresa = settings.NOMBRE_EMPRESA

		ruta = reverse('vEditarMedida', kwargs={'_id':_id})

		c = {'titulo':'Edición de Unidad de Medida', 'seccion':'Unidades de Medida', 'form':form, 'empresa':empresa, 'ruta':ruta}

		messages.info(request, 'Los campos con * son obligatorios')
		
		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST": # Pendiente de mejorar con bloque try/except

		form = forms.EditUnidadForm(request.POST, instance=unidad)

		if form.is_valid():

			try:
				
				form.save()

			except Exception as e:
				
				messages.error(request,"Excepción al actualizar categoria")

				logging.error(e)

				return redirect(reverse('vError'))
			
			messages.success(request, 'El registro se actualizó con éxito')

			return redirect('lista_medidas', {'page':1})


		

@login_required
@permission_required('core.delete_unidad')
def eliminar_medida(request, _id):
	
	if request.method == "POST": # Pendiente de mejorar con bloque try/except

		unidad = get_object_or_404(models.Unidad, pk=_id)

		unidad.delete()

		return redirect('lista_medidas', {'page':1})


@login_required
@permission_required('core.view_producto')
def lista_productos(request, page=1):

	limite = settings.LIMITE_FILAS

	productos = models.Producto.objects.all()

	if productos.count() > limite:
		
		paginador = Paginator(productos, limite)

		productos = paginador.get_page(page)

	empresa = settings.NOMBRE_EMPRESA

	c = {'titulo':'Lista de Productos', 'seccion':'Productos', 'empresa':empresa, 'productos':productos, 'page':page}

	return render(request, 'core/lista_productos.html', c)


@login_required
@permission_required('core.view_producto')
def ver_producto(request, _id):

	producto = get_object_or_404(models.Producto, pk=_id)

	empresa = settings.NOMBRE_EMPRESA

	params = {'_id':_id}

	ruta_edit = reverse('vEditarProducto', kwargs=params)

	ruta_delete = reverse('vEliminarProducto', kwargs=params)

	c = {'titulo':'Datos del Producto', 'seccion':'Productos', 'empresa':empresa,}



@login_required
@permission_required('core.add_producto')
def nuevo_producto(request):

	if request.method == "GET":

		empresa = settings.NOMBRE_EMPRESA

		form = forms.fProducto()

		ruta = reverse('vNuevoProducto')

		c = {'titulo':'Registro de Producto', 'seccion':'Productos', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":
		
		form = forms.fProducto(request.POST)

		if form.is_valid():

			producto = form.save(commit=False)

			producto.save()

			messages.success(request, "El producto se registró con éxito.")

			return redirect('ver_producto', {'_id':producto.id})



@login_required
@permission_required('core.change_producto')
def editar_producto(request, _id):
	
	producto = get_object_or_404(models.Producto, pk=_id)

	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		ruta = reverse('vEditarProducto', kwargs={'_id':_id})

		form = forms.fProducto(producto)

		c = {'titulo':'Editar datos de Producto', 'seccion':'Productos', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":
		
		form = forms.fProducto(request.POST, instance=producto)

		if form.is_valid():
			
			form.save()

			messages.success(request, "Los datos se actualizaron con éxito.")

			return redirect('ver_producto', {'_id':_id})



@login_required
@permission_required('core.delete_producto')
def eliminar_producto(request, _id):

	producto = get_object_or_404(models.Producto, pk=_id)

	producto.delete()

	messages.success(request, "El registro ha sido eliminado.")

	return redirect('lista_productos')
	


@login_required
@permission_required('core.view_camion')
def lista_camiones(request):

	camiones = models.Camion.objects.all()

	empresa = settings.NOMBRE_EMPRESA

	c = {'titulo':'Lista de Camiones', 'seccion':'Camiones' 'empresa':empresa, 'camiones':camiones}

	return render(request, 'core/lista_camiones.html', c)



@login_required
@permission_required('core.view_camion')
def ver_camion(request, _id):

	camion = get_object_or_404(models.Camion, pk=_id)

	empresa = settings.NOMBRE_EMPRESA

	params = {'_id':_id}

	ruta_edit = reverse('vEditarCamion', kwargs=params)

	ruta_delete = reverse('vEliminarCamion', kwargs=params)

	c = {'titulo':'Datos de Camión', 'seccion':'Camiones', 'empresa':empresa, 'camion':camion, 'ruta_edit':ruta_edit, 'ruta_delete':ruta_delete}

	return render(request, 'ver_camion.html', c)


@login_required
@permission_required('core.add_camion')
def nuevo_camion(request):

	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		form = forms.fCamion()

		ruta = reverse('vNuevoCamion')

		c = {'titulo':'Ingreso de Camion', 'seccion':'Camiones', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":
		
		form = forms.fCamion(request.POST)

		if form.is_valid():
			
			camion = form.save(commit=False)

			camion.save()

			messages.success(request, "Los datos se registraron con éxito.")

			return redirect('ver_camion', {'_id':camion.id})


@login_required
@permission_required('core.change_camion')
def editar_camion(request, _id):

	camion = get_object_or_404(models.Camion, pk=_id)

	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		form = forms.fCamion(camion)

		ruta = reverse('vEditarCamion', kwargs={'_id':_id})

		c = {'titulo':'Editar Datos de Camion', 'seccion':'Camiones', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":
		
		form = forms.fCamion(request.POST, instance=camion)

		if form.is_valid():
			
			form.save()

			messages.success(request, "Los datos se actualizaron con éxito.")

			return redirect('ver_camion', {'_id':_id})



@login_required
@permission_required('core.delete_camion')
def eliminar_camion(request, _id):

	if request.method == "POST":
		
		camion = get_object_or_404(models.Camion, pk=_id)

		camion.delete()

		messages.success(request, "El registro se eliminó con éxito.")

		return redirect('lista_camiones')









