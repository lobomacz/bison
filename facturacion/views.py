from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.urls import reverse
from django.conf import settings
from django.forms import formset_factory, modelformset_factory, inlineformset_factory
from django.contrib import messages
from django.contrib.auth import login_required, permission_required
from django.db.models imort Q, Sum
from bison.core.models import Empleado
from bison.contabilidad.models import Cuenta, Asiento, DetalleAsiento
from bison.inventario.models import Producto
from . import models, forms
import datetime, calendar, logging



# Create your views here.

# La página inicial de la sección llevará a las páginas de facturas y ordenes de ruta

@login_required
@permission_required(['facturacion.view_ordenruta', 'facturacion.view_factura'])
def index(request):

	empresa = settings.NOMBRE_EMPRESA

	periodo = models.Periodo.objects.get(activo=True)

	c = {'titulo':'Menú de Ventas', 'seccion':'Facturación', 'empresa':empresa, 'periodo':periodo}
	
	return render(request, 'indice.html', c)


@login_required
@permission_required('facturacion.view_factura')
def lista_facturas(request, page=1, inicio=None, final=None):

	facturas = None

	empresa = settings.NOMBRE_EMPRESA

	c = {'empresa':empresa, 'seccion':'Facturación', 'titulo':'Lista de Facturas', 'page':page}

	limite = settings.LIMITE_FILAS

	if inicio == None and final == None:
		
		periodo = models.Periodo.objects.get(activo=True)

		facturas = models.Factura.objects.filter(fecha__gte=periodo.fecha_inicio, fecha__lte=periodo.fecha_final)

		c['periodo'] = periodo

	else:

		facturas = models.Factura.objects.filter(fecha__gte=inicio, fecha__lte=final)

	if facturas.count() > limite:
		
		paginador = Paginator(facturas, limite)

		facturas = paginador.get_page(page)

		c['fecha_inicio'] = inicio
		c['fecha_final'] = final

	
	c['facturas'] = facturas

	return render(request, 'facturacion/lista_facturas.html', c)




@login_required
@permission_required('facturacion.view_proforma')
def lista_proformas(request, page=1, inicio=None, final=None):

	dias_vigencia = settings.VIGENCIA_PROFORMA

	today = datetime.date.today()

	tiempo_vigencia = datetime.timedelta(days=dias_vigencia)

	expire = today - tiempo_vigencia
	
	empresa = settings.NOMBRE_EMPRESA

	limite = settings.LIMITE_FILAS

	proformas = None

	c = {'titulo':'Listado de Proformas', 'seccion':'Facturación', 'empresa':empresa, 'page':page}

	validas = models.Proforma.objects.filter(valida=True)

	if validas.count() > 0:
		
		for proforma in validas:

			if proforma.fecha < expire:
				
				proforma.valida = False

				proforma.save()

	if inicio == None and final == None:
		
		proformas = get_list_or_404(models.Proforma, anulado=False, fecha__lte=expire.strftime('%Y-%m-%d'))

	else:

		proformas = get_list_or_404(models.Proforma, fecha__gte=inicio, fecha__lte=final)

		c['inicio'] = inicio
		c['final'] = final

	if proformas.count() > limite:
		
		paginador = Paginator(proformas, limite)

		proformas = paginador.get_page(page)

	c['proformas'] = proformas

	return render(request, 'facturacion/lista_proformas.html', c)




@login_required
@permission_required('facturacion.view_proforma')
def ver_proforma(request, _id):

	proforma = get_object_or_404(models.Proforma, pk=_id)

	empresa = settings.NOMBRE_EMPRESA

	ruta_edit = reverse('vEditarProforma', {'_id':_id})

	ruta_anular = reverse('vAnularProforma', {'_id':_id})

	ruta_reemitir = reverse('vReemitirProforma', {'_id':_id})

	c = {'titulo':'Detalle de Proforma', 'seccion':'Facturación', 'proforma':proforma, 'ruta_edit':ruta_edit, 'ruta_anular':ruta_anular, 'ruta_reemitir':ruta_reemitir}

	return render(request, 'facturacion/ver_proforma.html', c)



@login_required
@permission_required(['facturacion.add_proforma', 'facturacion.change_proforma', 'facturacion.add_detalleproforma', 'facturacion.change_detalleproforma'])
def detalle_proforma(request, _id):

	proforma = get_object_or_404(models.Proforma, pk=_id)

	extra_row = 4 if proforma.detalleproforma_set.all() != None else 10

	DetalleFormset = inlineformset_factory(models.Proforma, models.DetalleProforma, form=forms.fDetalleProforma, extra=extra_row)

	if request.method == "GET":

		empresa = settings.NOMBRE_EMPRESA

		formset = DetalleFormset(instance=proforma)

		ruta = reverse('vDetalleProforma', {'_id':_id})

		c = {'titulo':'Detalle de Proforma', 'seccion':'Facturación', 'empresa':empresa, 'proforma':proforma, 'formset':formset, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/formset_template.html', c)

	elif request.method == "POST":

		formset = DetalleFormset(request.POST, request.FILES, instance=proforma)

		if formset.is_valid():

			subtotal = 0.00

			for form in formset.forms:

				detalle = form.save(commit=False)

				if detalle.precio_unit <= 0.00:
					
					detalle.precio_unit = detalle.producto.precio_unit

				# Mejorar con conversión de unidad de medida para el cálculo del total

				detalle.total = detalle.cantidad * detalle.precio_unit

				subtotal += detalle.total

				detalle.save()

			proforma.subtotal = subtotal

			monto_iva = settings.MONTO_IVA

			proforma.iva = subtotal * monto_iva

			proforma.total = proforma.subtotal + proforma.iva

			proforma.save()

			messages.success(request, 'Los datos se registraron con éxito.')

			return redirect('ver_proforma', {'_id':_id})

		


@login_required
@permission_required('facturacion.add_proforma')
def nueva_proforma(request):

	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		hoy = datetime.date.today()

		proforma = models.Proforma()

		proforma.fecha = hoy

		form = forms.fProforma(proforma)

		ruta = reverse('vNuevaProforma')

		c = {'titulo':'Ingreso de Proforma', 'seccion':'Facturación', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":

		form = forms.fProforma(request.POST)

		if form.is_valid():

			empleado = request.user.usuario.empleado if request.user.usuario != None else None
			
			proforma = form.save(commit=False)

			proforma.vendedor = empleado

			proforma.save()

			messages.success(request, 'Datos registrados con éxito.')

			messages.info(request, 'Ingrese el detalle de la proforma.')

			return redirect('detalle_proforma', {'_id':proforma.id})
		
		


#REDEFINIR LA LOGICA DE EDICION DE PROFORMA
@login_required
@permission_required('facturacion.change_proforma')
def editar_proforma(request, _id):

	proforma = get_object_or_404(models.Proforma, pk=_id)

	if proforma.anulado == True or proforma.valida == False:
		
		messages.error(request, 'La proforma fue anulada o no es válida. No es posible editar.')

		return redirect('ver_proforma', {'_id':_id})

	dias_vigencia = settings.VIGENCIA_PROFORMA

	today = datetime.date.today()

	tiempo_vigencia = datetime.timedelta(days=dias_vigencia)

	expire = today - tiempo_vigencia

	if proforma.fecha <= expire:
		
		messages.error(request, 'La proforma pasó el período de vigencia. No se puede modificar.')

		return redirect('ver_proforma', {'_id':_id})


	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		form = forms.fProforma(proforma)

		ruta = reverse('vEditarProforma', {'_id':_id})

		c = {'titulo':'Editar Proforma', 'seccion':'Facturación', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":
		
		form = forms.fProforma(request.POST, instance=proforma)

		if form.is_valid():
			
			form.save()

			messages.success(request, 'Los datos se actualizaron con éxito.')

			messages.info(request, 'A continuación, actualizar el detalle de la proforma.')

			return redirect('detalle_proforma', {'_id':_id})

		


@login_required
@permission_required(['facturacion.add_proforma', 'facturacion.change_proforma'])
def reemitir_proforma(request, _id):

	proforma = get_object_or_404(models.Proforma, pk=_id)

	hoy = datetime.datetime.today()

	proforma.fecha = hoy

	proforma.pk = None

	proforma = proforma.save()

	messages.success(request, 'La proforma se ha reemitido con éxito.')

	return redirect('ver_proforma', {'_id':proforma.pk})




@login_required
@permission_required('facturacion.anular_proforma')
def anular_proforma(request, _id):

	if request.method == "POST":

		proforma = get_object_or_404(models.Proforma, pk=_id)

		empleado = request.user.usuario.empleado if request.user.usuario != None else None

		proforma.anulado = True

		proforma.anulado_por = empleado

		proforma.save()

		return redirect('ver_proforma', {'_id':_id})



@login_required
@permission_required('facturacion.view_factura')
def ver_factura(request, _id):

	factura = get_object_or_404(forms.Factura, pk=_id)

	empresa = settings.NOMBRE_EMPRESA

	params = {'_id':_id}

	ruta_edit = reverse('vEditarFactura', params)

	ruta_cancelar = reverse('vCancelarFactura', params)

	ruta_anular = reverse('vAnularFactura', params)

	ruta_entregar = reverse('vEntregarFactura', params)

	c = {'titulo':'Factura', 'seccion':'Facturación', 'factura':factura, 'empresa':empresa, 'ruta_edit':ruta_edit, 'ruta_cancelar':ruta_cancelar, 'ruta_entregar':ruta_entregar, 'ruta_anular':ruta_anular}

	return render(request, 'facturacion/ver_factura.html', c)




@login_required
@permission_required(['facturacion.change_factura', 'facturacion.change_detallefactura', 'facturacion.add_detallefactura'])
def detalle_factura(request, _id):

	factura = get_object_or_404(models.Factura, pk=_id)

	extra_row = 4 if factura.detallefactura_set.all() != None else 10
	
	DetalleFormset = inlineformset_factory(models.Factura, models.DetalleFactura, form=forms.fDetalleFactura, extra=extra_row)

	if request.method == "GET":

		formset = DetalleFormset(instance=factura)

		empresa = settings.NOMBRE_EMPRESA

		ruta = reverse('vDetalleFactura', {'_id':_id})

		messages.info(request, "Los campos con '*' son obligatorios.")

		c = {'titulo':'Detalle de Factura', 'seccion':'Facturación', 'empresa':empresa, 'formset':formset, 'factura':factura, 'ruta':ruta}

		return render(request, 'core/forms/formset_template.html', c)

	elif request.method == "POST":
		
		formset = DetalleFormset(request.POST, request.FILES, instance=factura)

		if formset.is_valid():

			subtotal = 0.00

			for form in formset.forms:

				detalle = form.save(commit=False)

				if not detalle.precio_unit > 0.00:

					detalle.precio_unit = detalle.producto.precio_unit

				# Mejorar con la conversión de unidad de medida para calcular el total.

				detalle.total = detalle.cantidad * detalle.precio_unit

				subtotal += detalle.total

				detalle.save()

			monto_iva = settings.MONTO_IVA

			factura.subtotal = subtotal

			factura.iva = factura.subtotal * monto_iva

			factura.total = factura.iva + factura.subtotal

			factura.save()

			messages.success(request, 'Los datos se registraron con éxito.')

			return redirect('ver_factura', {'_id':_id})

		


@login_required
@permission_required('facturacion.add_factura')
def nueva_factura(request):

	if request.method == "GET":

		hoy = datetime.date.today()

		factura = models.Factura()

		factura.fecha = hoy
		
		form = forms.fFactura(factura)

		empresa = settings.NOMBRE_EMPRESA

		ruta = reverse('vNuevaFactura')

		c = {'titulo':'Nueva Factura', 'seccion':'Facturación', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":

		form = forms.fFactura(request.POST)

		if form.is_valid():

			empleado = request.user.usuario.empleado if request.user.usuario != None else None
			
			factura = form.save(commit=False)

			factura.vendedor = empleado

			factura.save()

			messages.success(request, 'Los datos se registraron con éxito.')

			messages.info(request, 'Se registrará el detalle de la factura.')
			
			return redirect('detalle_factura', {'_id':factura.id})		



@login_required
@permission_required('facturacion.change_factura')
def editar_factura(request, _id):

	factura = get_object_or_404(models.Factura, pk=_id)

	if factura.cancelada == True or factura.anulada == True:
		
		messages.error(request, "No puede editar datos del registro.")

		return redirect('ver_factura', {'_id':_id})

	if request.method == "GET":

		form = forms.fFacturaEditar(factura)

		empresa = settings.NOMBRE_EMPRESA

		ruta = reverse('vEditarFactura', {'_id':_id})

		c = {'titulo':'Edición de Factura', 'seccion':'Facturación', 'empresa':empresa, 'form':form, 'ruta':ruta}

		messages.info(request, "Los campos con '*' son obligatorios.")

		return render(request, 'core/forms/form_template.html', c)

	elif request.method == "POST":
		
		form = forms.fFacturaEditar(request.POST, instance=factura)

		if form.is_valid():
			
			form.save()

			messages.success(request, "El registro se actualizó con éxito.")

			messages.info(request, "A continuación, actualizar el detalle de la factura.")

			return redirect('detalle_factura', {'_id':_id})



@login_required
@permission_required('facturacion.cancelar_factura')
def detalle_asiento_factura(request, _id, _ida):
	
	factura = get_object_or_404(models.Factura, pk=_id)

	asiento = get_object_or_404(models.Asiento, pk=_ida)



@login_required
@permission_required('facturacion.cancelar_factura')
def asiento_factura(request, _id):
	
	factura = get_object_or_404(models.Factura, pk=_id)

	if request.method == 'GET':
		pass
	elif request.method == 'POST':
		pass




@login_required
@permission_required('facturacion.imprimir_factura')
def cancelar_factura(request, _id):

	factura = get_object_or_404(models.Factura, pk=_id)

	factura.cancelada = True

	factura.save()

	messages.success(request, "La factura se registró como cancelada.")

	return redirect('asiento_factura', {'_id':_id})



		


@login_required
@permission_required('facturacion.view_ordenruta')
def lista_ordenes_ruta(request):
	
	ordenes = get_list_or_404(models.OrdenRuta, liquidado=False, anulado=False)

	empresa = settings.NOMBRE_EMPRESA

	c = {'titulo':'Indice de Ordenes de Ruta', 'seccion':'Facturación', 'empresa':empresa, 'ordenes':ordenes}

	return render(request, 'lista_ordenes_ruta.html', c)
	


@login_required
@permission_required('facturacion.view_ordenruta')
def ver_orden_ruta(request, _id):

	orden = get_object_or_404(models.OrdenRuta, pk=_id)

	empresa = settings.NOMBRE_EMPRESA

	c = {'titulo':'Orden de Ruta', 'seccion':'Facturación', 'empresa':empresa, 'orden':orden}

	return render(request, 'ver_orden_ruta.html', c)



@login_required
@permission_required(['facturacion.add_detalleordenruta', 'facturacion.change_detalleordenruta'])
def detalle_orden_ruta(request, _id):
	
	orden = get_object_or_404(models.OrdenRuta, pk=_id)

	if orden.anulado or orden.liquidado:
		
		return render(request, 'error.html', {'titulo':'Error de Acceso', 'seccion':'Facturación', 'empresa':settings.NOMBRE_EMPRESA, 'mensaje':'La orden de ruta no puede ser modificada.', 'view':'vListaOrdenesRuta'})

	extra_row = 4 if orden.detalleordenruta_set.all() != None else 10

	DetalleFormset = inlineformset_factory(models.OrdenRuta, models.DetalleOrdenRuta, form=forms.fDetalleOrdenRuta, extra=extra_row)

	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		formset = DetalleFormset(instance=orden)

		c = {'titulo':'Detalle de Orden de Ruta', 'seccion':'Facturación', 'empresa':empresa, 'formset':formset, 'id':_id}

		return render(request, 'detalle_orden_ruta.html', c)

	elif request.method == "POST":
		
		formset = DetalleFormset(request.POST, request.FILES, instance=orden)

		if formset.is_valid():

			for form in formset.forms:
				
				detalle = form.save(commit=False)

				detalle.total = detalle.producto.precio_unit * detalle.cantidad_entregada

				detalle.save()
			

			return redirect('ver_orden_ruta', {'_id':orden.id})

		else:

			return render(request, 'error.html', {'titulo':'Error de Validación', 'mensaje':'Los datos ingresados no son válidos. Revise y vuelva a intentarlo.', 'view':'vListaOrdenesRuta'})




@login_required
@permission_required('facturacion.add_ordenruta')
def nueva_orden_ruta(request):

	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		form = forms.fOrdenRuta()

		c = {'titulo':'Nueva Orden de Ruta', 'seccion':'Facturación', 'empresa':empresa, 'form':form}

		return render(request, 'form_orden_ruta.html', c)

	elif request.method == "POST":
		
		form = forms.fOrdenRuta(request.POST)

		if form.is_valid():

			empleado = request.user.usuario.empleado if request.user.usuario != None else None
			
			orden = form.save(commit=False)

			orden.digitador = empleado

			orden.save()

			return redirect('detalle_orden_ruta', {'_id':orden.id})

		else:

			return render(request, 'error.html', {'titulo':'Error de Validación', 'mensaje':'Los datos ingresados no son válidos. Revise y vuelva a intentarlo.', 'view':'vIndexFacturacion'})



@login_required
@permission_required('facturacion.change_ordenruta')
def editar_orden_ruta(request, _id):

	orden = get_object_or_404(models.OrdenRuta, pk=_id)

	if request.method == "GET":

		form = forms.fOrdenRuta(orden)

		empresa = settings.NOMBRE_EMPRESA

		c = {'titulo':'Editar Orden de Ruta', 'seccion':'Facturación', 'empresa':empresa, 'form':form, 'id':orden.id}

		return render(request, 'form_orden_ruta.html', c)

	elif request.method == "POST":
		
		form = forms.fOrdenRuta(request.POST, instance=orden)

		if form.is_valid():
			
			form.save()

			return redirect('detalle_orden_ruta', {'_id':orden.id})

		else:

			return render(request, 'error.html', {'titulo':'Error de Validación', 'mensaje':'Los datos ingresados no son válidos. Revise y vuelva a intentarlo.', 'view':'vListaOrdenesRuta'})



@login_required
@permission_required('facturacion.change_ordenruta')
def autorizar_orden_ruta(request, _id):
	
	orden = get_object_or_404(models.OrdenRuta, pk=_id)

	if not orden.autorizado:

		if request.method == "GET":
		
			empresa = settings.NOMBRE_EMPRESA

			c = {'titulo':'Autorizar Orden de Ruta', 'seccion':'Facturación', 'empresa':empresa, 'mensaje':'Se autorizará la orden de ruta.', 'view':'vAutorizarOrdenRuta', 'id':orden.id, 'empleado':empleado}

			return render(request, 'warning_template.html', c)

		elif request.method == "POST":

			empleado = request.user.usuario.empleado if request.user.usuario != None else None

			orden.autorizado = True

			orden.autorizado_por = empleado

			orden.save()

			return redirect('lista_ordenes_ruta')

	else:

		return render(request, 'error.html', {'titulo':'Error!', 'seccion':'Facturación', 'mensaje':'La orden ya fue autorizada.', 'view':'vListaOrdenesRuta'})


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
@permission_required('facturacion.delete_ordenruta')
def eliminar_orden_ruta(request, _id):
	
	orden = get_object_or_404(models.OrdenRuta, pk=_id)

	if orden.autorizado and orden.entregado:
		
		return render(request, 'error.html', {'titulo':'Error!', 'seccion':'Facturación', 'mensaje':'La orden fue autorizada y entregada. No se puede eliminar.', 'view':'vListaOrdenesRuta'})

	else:

		if request.method == "GET":
			
			empresa = settings.NOMBRE_EMPRESA

			c = {'titulo':'Eliminar Orden de Ruta', 'seccion':'Facturación', 'empresa':empresa, 'mensaje':'Se eliminará la orden de ruta.', 'view':'vEliminarOrdenRuta', 'id':orden.id}

			return render(request, 'warning_template.html', c)

		elif request.method == "POST":
			
			orden.delete()

			return redirect('lista_ordenes_ruta')


@login_required
@permission_required('facturacion.delete_detalleordenruta')
def eliminar_detalle_orden_ruta(request, _id):
	
	orden = get_object_or_404(models.DetalleOrdenRuta, pk=_id).orden

	if orden.autorizado or orden.anulado:
		
		return render(request, 'error.html', {'titulo':'Error!', 'seccion':'Facturación', 'mensaje':'No se puede eliminar la línea de detalle.', 'view':'vListaOrdenesRuta'})

	else:

		if request.method == "GET":
			
			empresa = settings.NOMBRE_EMPRESA

			c = {'titulo':'Eliminar Detalle de Orden de Ruta', 'seccion':'Facturación', 'empresa':empresa, 'mensaje':'Se eliminará la línea de detalle de la orden de ruta.', 'view':'vEliminarDetalleOrdenRuta', 'id':orden.id, 'idd':'_idd'}

			return render(request, 'warning_template.html', c)

		elif request.method == "POST":
			
			detalle = orden.detalleordenruta_set.filter(_idd)

			detalle.delete()

			return redirect('ver_orden_ruta', {'_id':orden.id})


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
def error(request):

	return render(request, 'core/error.html')
























