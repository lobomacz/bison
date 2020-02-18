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
		path('<int:page>/todos/', views.lista_empleados, {'todos':True}, name='vTodosEmpleados'),
		path('ver/<str:_id>/', views.ver_empleado, name='vVerEmpleado'),
		path('nuevo/', views.nuevo_empleado, name='vNuevoEmpleado'),
		path('nuevo/usuario/', views.nuevo_empleado_usuario, name='vNuevoEmpleadoUsuario'),
		path('editar/<str:_id>/', views.editar_empleado, name='vEditarEmpleado'),
		path('eliminar/<str:_id>/', views.eliminar_empleado, name='vEliminarEmpleado'),
		path('desactivar/<str:_id>/', views.desactiva_empleado, name='vDesactivarEmpleado'),
		path('<str:id_emp>/asignar-usuario/', views.asignar_usuario, name='vAsignarUsuario'),
		])),
	path('usuarios/', include([
		path('page/<int:page>/', views.lista_usuarios, name='vListaUsuarios'),
		path('<int:page>/todos/', views.lista_usuarios, {'todos':True}, name='vTodosUsuarios'),
		path('nuevo/', views.nuevo_usuario, name = 'vNuevoUsuario'),
		path('<int:_id>/editar/', views.editar_usuario, name='vEditarUsuario'),
		path('password/change/<int:_id>/', views.password_user_change, name='vCambiarPassword'),
		path('eliminar/<int:_id>/', views.eliminar_usuario, name='vEliminarUsuario'),
		path('desactivar/<int:_id>/', views.desactivar_usuario, name='vDesactivaUsuario'),
		])),
	path('categorias/', include([
		path('', views.lista_categorias, name='vListaCategorias'),
		path('nuevo/', views.nueva_categoria, name='vNuevaCategoria'),
		path('editar/', views.editar_categorias, name='vEditarCategorias'),
		path('eliminar/<int:_id>/', views.eliminar_categoria, name='vEliminarCategoria'),
		])),
	path('medidas/', include([
		path('', views.lista_medidas, name='vListaMedidas'),
		path('nuevo/', views.nueva_medida, name='vNuevaMedida'),
		path('editar/', views.editar_medida, name='vEditarMedida'),
		path('eliminar/<int:_id>/', views.eliminar_medida, name='vEliminarMedida'),
		])),
]