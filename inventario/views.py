from django.core.paginator import Paginator 
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.urls import reverse
from django.conf import settings
from django.forms import formset_factory, modelformset_factory, inlineformset_factory
from django.contrib import messages
from django.contrib.auth import login_required, permission_required
from django.db import transaction
from django.db.models import Q, Sum
from bison.core.models import Empleado 
from bison.contabilidad.models import Asiento
from bison.facturacion.models import OrdenRuta
from . import forms, models
import datetime



# Create your views here.

@login_required
def index(request):
	if not request.user.groups.filter(name='Inventario').count() > 0:
		
		messages.warning(request, "No tiene acceso a esta sección.")

		return redirect(reverse('core:bisonIndex'))

	empresa = settings.NOMBRE_EMPRESA

	c = {'titulo':'Panel de Inventario', 'empresa':empresa, 'seccion':'Inventario'}

	return render(request, 'inventario/index.html', c)


@login_required
@permission_required('facturacion.change_ordenruta')
def entregar_orden_ruta(request, _id):
	
	orden = get_object_or_404(models.OrdenRuta, pk=_id)

	if not orden.autorizado:

		return render(request, 'error.html', {'titulo':'Error!', 'seccion':'Facturación', 'mensaje':'La orden no ha sido autorizada.', 'view':'vListaOrdenesRuta'})

	else:

		if request.method == 'GET':
			
			empresa = settings.NOMBRE_EMPRESA

			c = {'titulo':'Entregar Orden de Ruta', 'seccion':'Facturación', 'empresa':empresa, 'view':'vEntregarOrdenRuta', 'id':orden.id}

			return render(request, 'entregar_orden_ruta.html', c)

		elif request.method == 'POST':
			
			empleado = request.user.usuario.empleado if request.user.usuario != None else None

			orden.entregado = True

			orden.entregado_por = empleado



@login_required
@permission_required(['facturacion.change_ordenruta', 'facturacion.change_detalleordenruta'])
def liquidar_orden_ruta(request, _id):
	
	orden = get_object_or_404(models.OrdenRuta, pk=_id)

	if orden.anulado or orden.liquidado:
		
		return render(request, 'error.html', {'titulo':'Error de Acceso', 'seccion':'Facturación', 'empresa':settings.NOMBRE_EMPRESA, 'mensaje':'La orden de ruta no puede ser modificada.', 'view':'vListaOrdenesRuta'})

	DetalleFormset = inlineformset_factory(models.OrdenRuta, models.DetalleOrdenRuta, form=forms.fLiquidaDetalleOrdenRuta)

	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		formset = DetalleFormset(instance=orden)

		c = {'titulo':'Liquidación de Orden de Ruta', 'seccion':'Facturación', 'empresa':empresa, 'formset':formset, 'view':'vLiquidarOrdenRuta', 'id':orden.id}

		return render(request, 'form_orden_ruta.html', c)

	elif request.method == "POST":
		
		formset = DetalleFormset(request.POST, request.FILES, instance=orden)

		if formset.is_valid():
			
			for form in formset.forms:

				detalle = form.save(commit=False)

				costo_producto = detalle.producto.costo_unit

				detalle.costo_vendido = detalle.cantidad_vendida * costo_producto

				detalle.costo_faltante = (detalle.cantidad_entregada - (detalle.cantidad_vendida + detalle.cantidad_recibida)) * costo_producto if detalle.cantidad_entregada > (detalle.cantidad_vendida + detalle.cantidad_recibida) else 0.00

				detalle.save()


			if not orden.detalleordenruta_set.all().aggregate(Sum('costo_faltante')) > 0.00:
				
				empleado = request.user.usuario.empleado if request.user.usuario != None else None

				orden.liquidado = True

				orden.liquidado_por = empleado

			return redirect('ver_orden_ruta', {'_id':orden.id})

		else:

			return render(request, 'error.html', {'titulo':'Error!', 'seccion':'Facturación', 'mensaje':'Los datos no son válidos.', 'view':'vVerOrdenRuta', 'id':_id})





@login_required
@permission_required('inventario.view_almacen')
def almacenes(request, page=1):

	empresa = settings.NOMBRE_EMPRESA

	limite = settings.LIMITE_FILAS

	almacenes = models.Almacen.objects.all()

	if almacenes.count() > 0:
		
		paginador = Paginator(almacenes, limite)

		almacenes = paginador.get_page(page)

	c = {'titulo':'Lista de Almacenes', 'seccion':'Almacenes', 'empresa':empresa, 'almacenes':almacenes, 'page':page}

	return render(request, 'inventario/almacenes.html', c)



@login_required
@permission_required('inventario.view_almacen')
def almacen(request, _id):

	almacen = get_object_or_404(models.Almacen, pk=_id)

	empresa = settings.NOMBRE_EMPRESA

	params = {'_id':_id}

	ruta_edit = reverse('vEditarAlmacen', kwargs=params)

	ruta_delete = reverse('vEliminarAlmacen', kwargs=params)

	c = {'titulo':'Datos de Almacen', 'seccion':'Almacenes', 'almacen':almacen, 'empresa':empresa, 'ruta_edit':ruta_edit, 'ruta_delete':ruta_delete}

	return render(request, 'inventario/ver_almacen.html')



@login_required
@permission_required('inventario.add_almacen')
def nuevo_almacen(request):

	if request.method == "GET":
	
		empresa = settings.NOMBRE_EMPRESA

		ruta = reverse('vNuevoAlmacen')

		form = forms.fAlmacen()

		c = {'titulo':'Ingreso de Almacen', 'seccion':'Almacenes', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":

		form = forms.fAlmacen(request.POST)

		if form.is_valid():
			
			almacen = form.save(commit=False)

			almacen.save()

			messages.success(request, "El registro se ingresó con éxito.")

			return redirect('ver_almacen', {'_id':almacen.id})




@login_required
@permission_required('inventario.change_almacen')
def editar_almacen(request, _id):

	almacen = get_object_or_404(models.Almacen, pk=_id)
	
	if request.method == "GET":

		entradas = almacen.entrada_set.count()

		salidas = almacen.salida_set.count()

		if entradas > 0 or salidas > 0:
			
			messages.warning(request, "El almacen ya tiene movimientos. No se puede editar.")

			return redirect(reverse('vDetalleAlmacen', kwargs={'_id':_id}))

		form = forms.fEditarAlmacen(almacen)

		empresa = settings.NOMBRE_EMPRESA

		ruta = reverse('vEditarAlmacen', kwargs={'_id':_id})

		c = {'titulo':'Editar datos de almacen', 'seccion':'Almacenes', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":
		
		form = forms.fEditarAlmacen(request.POST, instance=almacen)

		if form.is_valid():
			
			almacen = form.save(commit=False)

			almacen.save()

			messages.success(request, "Los datos se actualizaron con éxito.")

			return redirect('ver_almacen', {'_id':_id})



@login_required
@permission_required('inventario.delete_almacen')
def elimina_almacen(request, _id):

	almacen = get_object_or_404(models.Almacen, pk=_id)

	if request.method == "POST":

		entradas = almacen.entrada_set.count()

		salidas = almacen.salida_set.count()

		if entradas > 0 or salidas > 0:
			
			messages.warning(request, "El almacen ya tiene movimientos. No se puede eliminar.")

			return redirect(reverse('vDetalleAlmacen', kwargs={'_id':_id}))

		almacen.delete()

		messages.success(request, "El registro se eliminó con éxito.")

		return redirect('almacenes')




@login_required
@permission_required('inventario.view_entrada')
def entradas(request, page=1):

	limite = settings.LIMITE_FILAS

	empresa = settings.NOMBRE_EMPRESA

	almacen = None

	entradas = None

	if '_id' in request.GET:
		
		almacen = get_object_or_404(models.Almacen, pk=request.GET.get('_id'))

		entradas = almacen.entrada_set.all()

	else:

		entradas = models.Entrada.objects.all()


	if entradas.count() > limite:
		
		paginador = Paginator(entradas, limite)

		entradas = paginador.get_page(page)


	c = {'titulo':'Listado de Entradas de Almacen', 'seccion':'Entradas de Almacen', 'empresa':empresa, 'entradas':entradas, 'page':page}

	if almacen != None:
		
		c['almacen'] = almacen

	return render(request, 'inventario/entradas.html', c)




@login_required
@permission_required('inventario.view_entrada')
def entrada(request, _id):

	entrada = get_object_or_404(models.Entrada, pk=_id)

	params = {'_id':_id}

	ruta_edit = reverse('vEditarEntrada', kwargs=params)

	ruta_delete = reverse('vEliminarEntrada', kwargs=params)

	empresa = settings.NOMBRE_EMPRESA

	c = {'titulo':'Entrada', 'seccion':'Entradas de Almacen', 'empresa':empresa, 'entrada':entrada, 'ruta_edit':ruta_edit, 'ruta_delete':ruta_delete}

	return render(request, 'inventario/ver_entrada.html', c)




@login_required
@permission_required('inventario.add_detalleentrada')
def detalle_entrada(request, _id):

	ruta = reverse('vDetalleEntrada', kwargs={'_id':_id})

	entrada = get_object_or_404(models.Entrada, pk=_id)

	extra_row = 4 if entrada.detalleentrada_set.count() > 0 else 10

	DetalleFormset = inlineformset_factory(models.Entrada, models.DetalleEntrada, form=forms.fDetalleEntrada, extra=extra_row)

	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		formset = DetalleFormset(instance=entrada)

		c = {'titulo':'Detalle de Entrada', 'seccion':'Entradas de Almacen', 'empresa':empresa, 'formset':formset, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/inline_formset_template.html', c)

	elif request.method == "POST":
		
		formset = DetalleFormset(request.POST, request.FILES, instance=entrada)

		if formset.is_valid():
			
			try:
				with transaction.atomic():

					for form in formset.forms:
						
						detalle = form.save(commit=False)

						if not detalle.costo_unit > 0:
							
							detalle.costo_unit = detalle.producto.costo_unit

						detalle.total = detalle.cantidad * detalle.costo_unit

						detalle.save()

			except DatabaseError:
				
				messages.error(request, "Ocurrió un error al registrar los datos.")

				return redirect(ruta)


			messages.success(request, "Los datos se registraron con éxito.")

			return redirect('entrada', {'_id':_id})
	



@login_required
@permission_required('inventario.add_entrada')
def form_entrada(request, _id=None):

	entrada = get_object_or_404(models.Entrada, pk=_id) if _id != None else None

	if request.method == "GET":

		if entrada != None and entrada.asiento != None:
			
			if entrada.asiento.contabilizado:
				
				messages.error(request, "El asiento del registro está contabilizado. No se puede modificar.")

				return redirect('entrada', {'_id':_id})
		
		form = forms.fEntrada() if _id == None else forms.fEntrada(entrada)

		params = {'_id':_id} if _id != None else {}

		ruta = reverse('vNuevaEntrada', kwargs=params) 

		empresa = settings.NOMBRE_EMPRESA

		c = {'titulo':'Nueva Entrada de Almacen', 'seccion':'Entradas de Almacen', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":
		
		form = forms.fEntrada(request.POST) if entrada == None else forms.fEntrada(request.POST, instance=entrada)

		if form. is_valid():

			entrada = form.save(commit=False)

			entrada.save()

			if entrada == None:

				messages.success(request, "La entrada se registró con éxito.")

				messages.info(request, "A continuación ingresar detalle de la entrada.")

			else:

				messages.success(request, "La entrada se actualizó con éxito.")

				messages.info(request, "A continuación editar el detalle de la entrada.")

			return redirect('detalle_entrada', {'_id':entrada.id})




@login_required
@permission_required('inventario.view_salida')
def salidas(request, page=1):
	
	limite = settings.LIMITE_FILAS

	empresa = settings.NOMBRE_EMPRESA

	almacen = None

	salidas = None

	if '_id' in request.GET:
		
		almacen = get_object_or_404(models.Almacen, pk=request.GET.get('_id'))

		salidas = almacen.salida_set.all()

	else:

		salidas = models.Salida.objects.all()


	if salidas.count() > limite:
		
		paginador = Paginator(salidas, limite)

		salidas = paginador.get_page(page)


	c = {'titulo':'Lista de Salidas', 'seccion':'Salidas de Almacen', 'empresa':empresa, 'salidas':salidas, 'page':page}

	
	if almacen != None:
		
		c['almacen'] = almacen

	return render(request, 'inventario/salidas.html', c)




@login_required
@permission_required('inventario.view_salida')
def salida(request, _id):

	salida = get_object_or_404(models.Salida, pk=_id)

	params = {'_id':_id}

	ruta_edit = reverse('vEditarSalida', kwargs=params)

	ruta_delete = reverse('vEliminarSalida', kwargs=params)

	empresa = settings.NOMBRE_EMPRESA

	c = {'titulo':'Salida', 'seccion':'Salidas de Almacen', 'empresa':empresa, 'salida':salida, 'ruta_edit':ruta_edit, 'ruta_delete':ruta_delete}

	return render(request, 'inventario/ver_salida.html', c)




@login_required
@permission_required('inventario.add_salida')
def detalle_salida(request, _id):
	
	salida = get_object_or_404(models.Salida, pk=_id)

	extra_row = 4 if salida.detallesalida_set.count() > 0 else 10

	DetalleFormset = inlineformset_factory(models.Salida, models.DetalleSalida, form=forms.fDetalleSalida, extra=extra_row)

	ruta = reverse('vDetalleSalida', kwargs={'_id':_id})

	if request.method == "GET":
		
		formset = DetalleFormset(instance=salida)

		empresa = settings.NOMBRE_EMPRESA

		c = {'titulo':'Detalle de Salida', 'seccion':'Salidas de Almacen', 'empresa':empresa, 'formset':formset, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/inline_formset_template.html', c)

	elif request.method == "POST":
		
		formset = DetalleFormset(request.POST, request.FILES, instance=salida)

		if formset.is_valid():
			
			try:
				with transaction.atomic():

					for form in formset.forms:
						
						detalle = form.save(commit=False)

						if not detalle.costo_unit > 0:
							
							detalle.costo_unit = detalle.producto.costo_unit

						detalle.total = detalle.cantidad * detalle.costo_unit

						detalle.save()


			except DatabaseError:
				
				messages.error(request, "Ocurrió un error al registrar los datos. Intentelo de nuevo.")

				return redirect(ruta)

			messages.success(request, "Los datos se registraron con éxito.")

			return redirect('salida', {'_id':_id})



@login_required
@permission_required('inventario.add_salida')
def form_salida(request, _id=None):

	salida = get_object_or_404(models.Salida, pk=_id) if _id != None else None

	if request.method == "GET":
		
		form = forms.fSalida() if salida == None else forms.fSalida(salida)

		empresa = settings.NOMBRE_EMPRESA

		ruta = reverse('vNuevaSalida')

		c = {'titulo':'Nueva Salida', 'seccion':'Salidas de Almacen', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/form_template.html', c)


	elif request.method == "POST":
		
		form = forms.fSalida(request.POST) if salida == None else forms.fSalida(request.POST, instance=salida)

		if form.is_valid():
			
			salida = form.save(commit=False)

			salida.save()

			if salida == None:
				
				messages.success(request, "La salida se registró con éxito.")

				messages.info(request, "A continuación, registrar el detalle de la salida.")

			else:
				
				messages.success(request, "La salida se actualizó con éxito.")

				messages.info(request, "A continuación, editar el detalle de la salida.")


			return redirect('detalle_salida', {'_id':salida.id})






























