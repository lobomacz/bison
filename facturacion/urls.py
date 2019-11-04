from django.urls import path, include
from . import views

app_name = 'facturacion'

urlpatterns = [
	path('', views.index, name = 'vIndexFacturacion'),
	path('ventas/', include([
		path('mes/', views.ventasMes, name='vVentasMes'),
		path('periodo/<int:id>/', views.ventasPeriodo, name='vVentasPeriodo'),
		path('rango/<str:inicio>/<str:final>/', views.ventasRango, name='vVentasRango'),
		])),
	path('proformas/', include([
		path('', views.listaProformas, name='vListaProformas'),
		path('nueva/', views.nuevaProforma, name='vNuevaProforma'),
		path('ingresar/', views.ingresarProforma, name='vIngresarProforma'),
		path('anular/', views.anularProforma, name='vAnularProforma'),
		])),
	path('facturas/', include([
		path('nueva/', views.nuevaFactura, name='vNuevaFactura'),
		path('ver/<int:id>/', views.verFactura, name='vVerFactura'),
		path('imprimir/<int:id>/', views.imprimirFactura, name='vImprimirFactura'),
		path('liquidar/<int:vendedor>/<str:fecha>', views.liquidarFactura, name='vLiquidarFactura'),
		path('editar/<int:id>/', views.editarFactura, name='vEditarFactura'),
		path('cancelar/<int:id>/', views.cancelarFactura, name='vCancelarFactura'),
		path('anular/<int:id>/', views.anularFactura, name='vAnularFactura'),
		path('entregar/<int:id>/', views.entregarFactura, name='vEntregarFactura'),
		path('pendientes/', views.listaFacturasPendientes, name='vListaFacturasPendientes'),
		])),
	path('clientes/', include([
		path('', views.listaClientes, name='vListaClientes'),
		path('ver/<str:id>/', views.verCliente, name='vVerCliente'),
		path('nuevo/', views.nuevoCliente, name='vNuevoCliente'),
		path('editar/<str:id>/', views.editarCliente, name='vEditarCliente'),
		])),
	path('vendedores/', include([
		path('', views.listaVendedores, name='vListaVendedores'),
		path('ver/<int:id>/', views.verVendedor, name='vVerVendedor'),
		path('buscar/<str:cedula>/', views.buscarVendedor, name='vBuscarVendedor'),
		path('nuevo/', views.nuevoVendedor, name='vNuevoVendedor'),
		path('editar/<int:id>/', views.editarVendedor, name='vEditarVendedor'),
		path('desactivar/<int:id>/', views.desactivarVendedor, name='vDesactivarVendedor'),
		])),
	path('camiones/', include([
		path('', views.listaCamiones, name='vListaCamiones'),
		path('nuevo/', views.nuevoCamion, name='vNuevoCamion'),
		path('editar/<int:id>/', views.editarCamion, name='vEditarCamion'),
		path('eliminar/<int:id>/', views.eliminarCamion, name='vEliminarCamion'),
		])),
	path('ordenes-ruta/', include([
		path('', views.listaOrdenesRuta, name='vListaOrdenesRuta'),
		path('nueva/', views.nuevaOrdenRuta, name='vNuevaOrdenRuta'),
		path('ver/<int:id>/', views.verOrdenRuta, name='vVerOrdenRuta'),
		path('editar/<int:id>/', views.editarOrdenRuta, name='vEditarOrdenRuta'),
		path('eliminar/<int:id>/', views.eliminarOrdenRuta, name='vEliminarOrdenRuta'),
		path('entregar/<int:id>/', views.entregarOrdenRuta, name='vEntregarOrdenRuta'),
		path('anular/<int:id>/', views.anularOrdenRuta, name='vAnularOrdenRuta'),
		path('liquidar/<int:id>/', views.liquidarOrdenRuta, name='vLiquidarOrdenRuta'),
		path('buscar/<str:fecha>/', views.buscarOrdenRuta, name='vBuscarOrdenRuta'),
		path('detalle/<int:id>/editar/', views.editarDetalleOrdenRuta, name='vEditarDetalleOrdenRuta'),
		path('detalle/<int:id>/eliminar/', views.eliminarDetalleOrdenRuta, name='vEliminarDetalleOrdenRuta'),
		path('facturas/', views.verFacturasOrdenRuta, name='vVerFacturasOrdenRuta'),
		path('facturas/nueva/', views.nuevaFacturaOrdenRuta, name='vNuevaFacturaOrenRuta'),
		])),
]