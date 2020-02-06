from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.conf import settings
from django.http import HttpResponseRedirect
from django.forms import formset_factory, modelformset_factory, inlineformset_factory
from django.contrib.auth import login_required, permission_required
from bison.core.models import Empleado
from . import models, forms
import datetime, calendar



# Create your views here.

@login_required
@permission_required(['facturacion.view_ordenruta', 'facturacion.view_factura'])
def index(request):

	empresa = settings.NOMBRE_EMPRESA

	periodo = models.Periodo.objects.get(activo=True)

	c = {'titulo':'Menú de Ventas', 'seccion':'Facturación', 'empresa':empresa, 'periodo':periodo}
	
	return render(request, 'indice.html', c)


@login_required
@permission_required('facturacion.view_factura')
def ventas_periodo(request):

	periodo = models.Periodo.objects.get(activo=True)

	facturas = models.Factura.objects.filter(fecha__gte=periodo.fecha_inicio, fecha__lte=periodo.fecha_final)

	empresa = settings.NOMBRE_EMPRESA

	c = {'empresa':empresa, 'facturas':facturas, 'periodo':periodos, 'seccion':'Facturación', 'titulo':'Ventas del período '}

	return render(request, 'ventas_periodo.html', c)



@login_required
@permission_required('facturacion.view_factura')
def ventas_rango(request, inicio, final):

	facturas = get_list_or_404(models.Factura, fecha__gte=inicio, fecha__lte=final)

	empresa = settings.NOMBRE_EMPRESA

	c = {'empresa':empresa, 'titulo':'Ventas por Rango de Fechas', 'seccion':'Facturación', 'facturas':facturas}

	return render(request, 'ventas_rango.html', c)


@login_required
@permission_required('facturacion.view_proforma')
def lista_proformas(request, todas=None):

	today = datetime.datetime.now()

	expire = today - datetime.timedelta(days=15)
	
	empresa = settings.NOMBRE_EMPRESA

	proformas = get_list_or_404(models.Proforma, anulado=False, fecha__gte=expire.strftime('%Y-%m-%d'))

	if todas != None:
		
		proformas = get_list_or_404(models.Proforma)

	c = {'titulo':'Listado de Proformas', 'seccion':'Facturación', 'empresa':empresa, 'proformas':proformas}

	return render(request, 'lista_proformas.html', c)


@login_required
@permission_required('facturacion.view_proforma')
def lista_proformas_rango(request, inicio, final):
	
	empresa = settings.NOMBRE_EMPRESA

	proformas = get_list_or_404(models.Proforma, fecha__gte=inicio, fecha__lte=final)

	c = {'titulo':'Listado de Proformas', 'seccion':'Facturación', 'empresa':empresa, 'proformas':proformas}

	return render(request, 'lista_proformas.html', c)



@login_required
@permission_required('facturacion.view_proforma')
def ver_proforma(request, _id):

	proforma = get_object_or_404(models.Proforma, pk=_id)

	empresa = settings.NOMBRE_EMPRESA

	return render(request, 'ver_proforma.html', {'titulo':'Detalle de Proforma', 'seccion':'Facturación', 'proforma':proforma})



@login_required
@permission_required('facturacion.add_detalleproforma')
def detalle_proforma(request, _id):

	proforma = get_object_or_404(models.Proforma, pk=_id)

	extra_row = 4 if proforma.detalleproforma_set.all() != None else 10

	DetalleFormset = inlineformset_factory(models.Proforma, models.DetalleProforma, form=forms.fDetalleProforma, extra=extra_row)

	if request.method == "GET":

		empresa = settings.NOMBRE_EMPRESA

		formset = DetalleFormset(instance=proforma)

		c = {'titulo':'Detalle de Proforma', 'seccion':'Facturación', 'empresa':empresa, 'formset':formset, 'id':_id}

		return render(request, 'detalle_proforma.html', c)

	elif request.method == "POST":

		formset = DetalleFormset(request.POST, request.FILES, instance=proforma)

		if formset.is_valid():

			subtotal = 0.00

			for form in formset.forms:

				detalle = form.save(commit=False)

				if not detalle.precio_unit > 0.00:
					
					detalle.precio_unit = detalle.producto.precio_unit

				#Mejorar con conversión de unidad de medida para el cálculo del total
				detalle.total = detalle.cantidad * detalle.precio_unit

				subtotal += detalle.total

				detalle.save()

			proforma.subtotal = subtotal

			monto_iva = settings.MONTO_IVA

			proforma.iva = subtotal * monto_iva

			proforma.total = proforma.subtotal + proforma.iva

			proforma.save()

			return redirect('ver_proforma', {'_id':_id})

		else:

			return render(request, 'error.html', {'titulo':'Error de Validación', 'mensaje':'Los datos ingresados no son válidos. Revise y vuelva a intentarlo.', 'view':'vVerProforma', 'id':_id})



@login_required
@permission_required('facturacion.add_proforma')
def nueva_proforma(request):

	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		form = forms.fProforma()

		c = {'titulo':'Ingreso de Proforma', 'seccion':'Facturación', 'empresa':empresa, 'form':form}

		return render(request, 'form_proforma.html', c)

	elif request.method == "POST":
		
		if request.POST:
			
			form = forms.fProforma(request.POST)

			if form.is_valid():

				empleado = request.user.usuario.empleado if request.user.usuario != None else None
				
				proforma = form.save(commit=False)

				proforma.vendedor = empleado

				proforma.save()

				return redirect('detalle_proforma', {'_id':proforma.id})

			else:

				return render(request, 'error.html', {'mensaje':'No se validaron los datos de Proforma. Revise y vuelva a intentarlo.', 'titulo':'Error de Validación', 'view':'vNuevaProforma'})

		else:

			return render(request, 'error.html', {'mensaje':'No se recibieron datos de Proforma. Revise y vuelva a intentarlo.', 'titulo':'Error de Datos', 'view':'vNuevaProforma'})



#REDEFINIR LA LOGICA DE EDICION DE PROFORMA
@login_required
@permission_required('facturacion.change_proforma')
def editar_proforma(request, _id):

	proforma = get_object_or_404(models.Proforma, pk=_id)

	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		form = forms.fProforma(proforma)

		c = {'titulo':'Editar Proforma', 'seccion':'Facturación', 'empresa':empresa, 'form':form, 'id':_id}

		return render(request, 'form_proforma.html', c)

	elif request.method == "POST":
		
		form = forms.fProforma(request.POST, instance=proforma)

		if form.is_valid():
			
			form.save()

			return redirect('detalle_proforma', {'_id':proforma.id})

		else:

			return render(request, 'error.html', {'mensaje':'No se validaron los datos de Proforma. Revise y vuelva a intentarlo.', 'titulo':'Error de Validación', 'view':'vListaProformas'})


@login_required
@permission_required(['facturacion.add_proforma', 'facturacion.change_proforma'])
def reemitir_proforma(request, _id):

	proforma = get_object_or_404(models.Proforma, pk=_id)

	hoy = datetime.datetime.today()

	diferencia = abs(hoy - proforma.fecha)

	if diferencia.days > 1:
		
		return render(request, 'error.html', {'mensaje':'La Proforma aún se encuentra vigente. No es posible reemitirla.', 'titulo':'Proforma Vigente', 'view':'vListaProformas'})

	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		c = {'titulo':'Reemitir Proforma', 'view':'vReemitirProforma', 'id':_id, 'seccion':'Facturación', 'empresa':empresa, 'mensaje':'Confirme que desea reemitir la proforma, por favor.'}

		return render(request, 'warning_template.html', c)

	elif request.method == POST:

		proforma = get_object_or_404(models.Proforma, pk=_id)

		detalle = proforma.detalleproforma_set.all()

		empleado = request.user.usuario.empleado if request.user.usuario != None else None

		proforma.id = None

		proforma.fecha = hoy

		proforma.vendedor = empleado

		proforma = proforma.save()

		for linea in detalle:

			linea.id = None

			linea.proforma = proforma

			linea.save()

		return redirect('lista_proformas')



@login_required
@permission_required('facturacion.change_proforma')
def anular_proforma(request, _id):

	if request.method == "GET":
		
		empresa = settings.NOMBRE_EMPRESA

		c = {'empresa':empresa, 'id':_id, 'view':'vAnularProforma', 'titulo':'Anular Proforma', 'mensaje':'Se anulará la proforma.', 'seccion':'Facturación'}

		return render(request, 'warning_template.html', c)

	elif request.method == "POST":

		proforma = get_object_or_404(models.Proforma, pk=_id)

		empleado = request.user.usuario.empleado if request.user.usuario != None else None

		proforma.anulado = True

		proforma.anulado_por = empleado

		proforma.save()

		return redirect('lista_proformas')



@login_required
@permission_required('facturacion.view_factura')
def ver_factura(request, _id):

	factura = get_object_or_404(forms.Factura, pk=_id)

	empresa = settings.NOMBRE_EMPRESA

	c = {'titulo':'Factura', 'seccion':'Facturación', 'factura':factura, 'empresa':empresa}

	return render(request, 'ver_factura.html', c)




@login_required
@permission_required(['facturacion.change_detallefactura', 'facturacion.add_detallefactura'])
def detalle_factura(request, _id):

	factura = get_object_or_404(models.Factura, pk=_id)

	extra_row = 4 if factura.detallefactura_set.all() != None else 10
	
	DetalleFormset = inlineformset_factory(models.Factura, models.DetalleFactura, form=forms.fDetalleFactura, extra=extra_row)

	if request.method == "GET":

		formset = DetalleFormset(instance=factura)

		empresa = settings.NOMBRE_EMPRESA

		c = {'titulo':'Detalle de Factura', 'seccion':'Facturación', 'empresa':empresa, 'formset':formset, 'id':_id}

		return render(request, 'detalle_factura.html', c)

	elif request.method == "POST":
		
		formset = DetalleFormset(request.POST, request.FILES, instance=factura)

		if formset.is_valid():

			subtotal = 0.00

			for form in formset.forms:

				detalle = form.save(commit=False)

				if not detalle.precio_unit > 0.00:

					detalle.precio_unit = detalle.producto.precio_unit

				detalle.total = detalle.cantidad * detalle.precio_unit

				subtotal += detalle.total

				detalle.save()

			monto_iva = settings.MONTO_IVA

			factura.subtotal = subtotal

			factura.iva = factura.subtotal * monto_iva

			factura.total = factura.iva + factura.subtotal

			factura.save()

			return redirect('ver_factura', {'_id':factura.id})

		else:

			return render(request, 'error.html', {'titulo':'Error de Validación', 'mensaje':'Los datos ingresados no son válidos. Revise y vuelva a intentarlo.', 'view':'vVerFactura', 'id':_id})



@login_required
@permission_required('facturacion.add_factura')
def nueva_factura(request):

	if request.method == "GET":
		
		form = forms.fFactura()

		empresa = settings.NOMBRE_EMPRESA

		c = {'titulo':'Nueva Factura', 'seccion':'Facturación', 'empresa':empresa, 'form':form}

		return render(request, 'form_factura.html', c)

	elif request.method == "POST":

		form = forms.fFactura(request.POST)

		if form.is_valid():

			empleado = request.user.usuario.empleado if request.user.usuario != None else None
			
			factura = form.save(commit=False)

			factura.vendedor = empleado

			factura.save()

			return redirect('detalle_factura', {'_id':factura.id})

		else:

			return render(request, 'error.html', {'titulo':'Error de Validación', 'mensaje':'Los datos ingresados no son válidos. Revise y vuelva a intentarlo.', 'view':'vIndexFacturacion'})




@login_required
@permission_required('facturacion.change_factura')
def editar_factura(request, _id):

	factura = get_object_or_404(models.Factura, pk=_id)

	if request.method == "GET":

		form = forms.fFacturaEditar(factura)

		empresa = settings.NOMBRE_EMPRESA

		c = {'titulo':'Edición de Factura', 'seccion':'Facturación', 'empresa':empresa, 'form':form}

		return render(request, 'form_factura.html', c)

	elif request.method == "POST":
		
		form = forms.fFacturaEditar(request.POST, instance=factura)

		if form.is_valid():
			
			form.save()

			return redirect('detalle_factura', {'_id':_id})

		else:

			return render(request, 'error.html', {'titulo':'Error de Validación', 'mensaje':'Los datos ingresados no son válidos. Revise y vuelva a intentarlo.', 'view':'vIndexFacturacion'})



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





























