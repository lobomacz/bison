from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'core'

urlpatterns = [
	path('', views.index, name='bisonIndex'),
	path('login/', views.bison_login, name='bisonLogin'),
	path('logout/', views.bison_logout, name='bisonLogout'),
	path('empleados/', include([
		path('page/<int:page>/', views.lista_empleados, name='vListaEmpleados'),
		path('page/<int:page>/todos/', views.lista_empleados, {'todos':True}, name='vTodosEmpleados'),
		path('<str:_id>/ver/', views.ver_empleado, name='vVerEmpleado'),
		path('nuevo/', views.nuevo_empleado, name='vNuevoEmpleado'),
		path('nuevo/usuario/', views.nuevo_empleado_usuario, name='vNuevoEmpleadoUsuario'),
		path('<str:_id>/editar/', views.editar_empleado, name='vEditarEmpleado'),
		path('<str:_id>/eliminar/', views.eliminar_empleado, name='vEliminarEmpleado'),
		path('<str:_id>/desactivar/', views.desactiva_empleado, name='vDesactivarEmpleado'),
		path('<str:_id>/asignar-usuario/', views.asignar_usuario, name='vAsignarUsuario'),
		])),
	path('usuarios/', include([
		path('page/<int:page>/', views.lista_usuarios, name='vListaUsuarios'),
		path('nuevo/', views.nuevo_usuario, name = 'vNuevoUsuario'),
		path('<int:_id>/editar/', views.editar_usuario, name='vEditarUsuario'),
		path('password/change/', views.password_user_change, name='vCambiarPassword'),
		path('<int:_id>/eliminar/', views.eliminar_usuario, name='vEliminarUsuario'),
		path('<int:_id>/desactivar/', views.desactivar_usuario, name='vDesactivaUsuario'),
		])),
	path('categorias/', include([
		path('page/<int:page>/', views.lista_categorias, name='vListaCategorias'),
		path('nuevo/', views.nueva_categoria, name='vNuevaCategoria'),
		path('<int:_id>/editar/', views.editar_categoria, name='vEditarCategoria'),
		path('<int:_id>/eliminar/', views.eliminar_categoria, name='vEliminarCategoria'),
		])),
	path('medidas/', include([
		path('page/<int:page>/', views.lista_medidas, name='vListaMedidas'),
		path('nuevo/', views.nueva_medida, name='vNuevaMedida'),
		path('<int:_id>/editar/', views.editar_medida, name='vEditarMedida'),
		path('<int:_id>/eliminar/', views.eliminar_medida, name='vEliminarMedida'),
		])),
	path('camiones/', include([
		path('', views.lista_camiones, name='vListaCamiones'),
		path('nuevo/', views.nuevo_camion, name='vNuevoCamion'),
		path('<int:_id>/ver/', views.ver_camion, name='vVerCamion'),
		path('<int:_id>/editar/', views.editar_camion, name='vEditarCamion'),
		path('<int:_id>/eliminar/', views.eliminar_camion, name='vEliminarCamion'),
		])),
	#path('error/', views.error, name='vError'),
]