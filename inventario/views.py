from django.shortcuts import render

# Create your views here.





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

