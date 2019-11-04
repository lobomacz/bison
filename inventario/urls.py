from django.urls import path, include
from . import views

app_name = 'inventario'

urlspatterns = [
	path('', views.index, name='vIndexInventario'),
	path('productos/', include([
		path('', views.listaProductos, name='vListaProductos'),
		path('ver/<int:id>/', views.detalleProducto, name='vDetalleProducto'),
		path('nuevo/', views.nuevoProducto, name='vNuevoProducto'),
		path('editar/<int:id>/', views.editarProducto, name='vEditarProducto'),
		path('eliminar/<int:id>/', views.eliminarProducto, name='vEliminarProducto'),
		])),
	path('almacen/', include([
		path('', views.listaAlmacenes, name='vListaAlmacen'),
		path('ver/<int:id>/', views.detalleAlmacen, name='vDetalleAlmacen'),
		path('nuevo/', views.nuevoAlmacen, name='vNuevoAlmacen'),
		path('editar/<int:id>/', views.editarAlmacen, name='vEditarAlmacen'),
		path('eliminar/<int:id>/', views.eliminarAlmacen, name='vEliminarAlmacen'),
		])),
	path('entradas/', include([
		path('', views.indiceEntradasAlmacen, name='vIndiceEntradasAlmacen'),
		path('almacen/<int:id>/ver/<int:eid>/', views.listaEntradasAlmacen, name='vListaEntradasAlmacen'),
		path('almacen/<int:id>/nueva/', views.nuevaEntradaAlmacen, name='vNuevaEntradaAlmacen'),
		path('almacen/<int:id>/orden/<int:oid>/nueva/', views.nuevaEntradaConOrden, name='vNuevaEntradaConOrden'),
		path('almacen/<int:id>/editar/<int:eid>/', views.editarEntradaAlmacen, name='vEditarEntradaAlmacen'),
		path('almacen/<int:id>/eliminar/<int:eid>/', views.eliminarEntradaAlmacen, name='vEliminarEntradaAlmacen'),
		path('almacen/<int:id>/<str:fecha>/', views.entradasAlmacenFecha, name='vEntradaAlmacenFecha'),
		path('almacen/<int:id>/<str:inicio>/<str:final>/', views.entradasAlmacenRango, name='vEntradasAlmacenRango'),
		])),
	path('detalle-entrada/', include([
		path('entrada/<int:eid>/nuevo/', views.nuevoDetalleEntrada, name='vNuevoDetalleEntrada'),
		path('entrada/<int:eid>/editar/<int:id>/', views.editarDetalleEntrada, name='vEditarDetalleEntrada'),
		path('entrada/<int:eid>/eliminar/<int:id>/' views.eliminarDetalleEntrada, name='vEliminarDetalleEntrada'),
		])),
	path('salidas/', include([
		path('', views.indiceSalidasAlmacen, name='vIndiceSalidasAlmacen'),
		path('almacen/<int:id>/ver/<int:sid>/', views.listaSalidasAlmacen, name='vListaSalidasAlmacen'),
		path('almacen/<int:id>/nueva/', views.nuevaSalidaAlmacen, name='vNuevaSalidaAlmacen'),
		path('almacen/<int:id>/orden/<int:oid>/nueva', views.nuevaSalidaConOrden, name='vNuevaSalidaConOrden'),
		path('almacen/<int:id>/editar/<int:sid>/', views.editarSalidaAlmacen, name='vEditarSalidaAlmacen'),
		path('almacen/<int:id>/eliminar/<int:sid>/', views.eliminarSalidaAlmacen, name='vEliminarSalidaAlmacen'),
		path('almacen/<int:id>/<str:fecha>/', views.salidasAlmacenFecha, name='vSalidasAlmacenFecha'),
		path('almacen/<int:id>/<str:inicio>/<str:final>/', views.salidasAlmacenRango, name='vSalidasAlmacenRango'),
		])),
	path('detalle-salida/', include([
		path('salida/<int:sid>/nuevo/', views.nuevoDetalleSalida, name='vNuevoDetalleSalida'),
		path('salida/<int:sid>/editar/<int:id>/', views.editarDetalleSalida, name='vEditarDetalleSalida'),
		path('salida/<int:sid>/eliminar/<int:id>/' views.eliminarDetalleSalida, name='vEliminarDetalleSalida'),
		])),
	path('orden-salida/', include([
		path('', views.indiceOrdenesSalida, name='vIndiceOrdenesSalida'),
		path('almacen/<int:id>/ver/<int:oid>/', views.listaOrdenesSalida, name='vListaOrdenesSalida'),
		path('almacen/<int:id>/nueva/', views.nuevaOrdenSalida, name='vNuevaOrdenSalida'),
		path('almacen/<int:id>/editar/<int:oid>/', views.editarOrdenSalida, name='vEditarOrdenSalida'),
		path('almacen/<int:id>/eliminar/<int:oid>', views.eliminarOrdenSalida, name='vEliminarOrdenSalida'),
		])),
	path('detalle-orden-salida/', include([
		path('orden/<int:id>/nuevo/', views.nuevoDetalleOrdenSalida, name='vNuevoDetalleOrdenSalida'),
		path('orden/<int:id>/editar/<int:did>/', views.editarDetalleOrdenSalida, name='vEditarDetalleOrdenSalida'),
		path('orden/<int:id>/eliminar/<int:did>/', views.eliminarDetalleOrdenSalida, name='vEliminarDetalleOrdenSalida'),
		])),
	path('orden-entrada/', include([
		path('', views.indiceOrdenesEntrada, name='vIndiceOrdenesEntrada'),
		path('almacen/<int:id>/ver/<int:oid>/', views.listaOrdenesEntrada, name='vListaOrdenesEntrada'),
		path('almacen/<int:id>/nueva/', views.nuevaOrdenEntrada, name='vNuevaOrdenEntrada'),
		path('almacen/<int:id>/editar/<int:oid>/', views.editarOrdenEntrada, name='vEditarOrdenEntrada'),
		path('almacen/<int:id>/eliminar/<int:oid>', views.eliminarOrdenEntrada, name='vEliminarOrdenEntrada'),
		])),
	path('detalle-orden-entrada/', include([
		path('orden/<int:id>/nuevo/', views.nuevoDetalleOrdenEntrada, name='vNuevoDetalleOrdenEntrada'),
		path('orden/<int:id>/editar/<int:did>/', views.editarDetalleOrdenEntrada, name='vEditarDetalleOrdenEntrada'),
		path('orden/<int:id>/eliminar/<int:did>/', views.eliminarDetalleOrdenEntrada, name='vEliminarDetalleOrdenEntrada'),
		])),
]