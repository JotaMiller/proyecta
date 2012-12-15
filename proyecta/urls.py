from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout
from django.contrib import admin

import os

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

admin.autodiscover()

urlpatterns = patterns('',
    (r'^grappelli/', include('grappelli.urls')),
    # Examples:
    # url(r'^$', 'proyecta.views.home', name='home'),
    # url(r'^proyecta/', include('proyecta.foo.urls')),
    url(r'^chat/', include('minichat.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # Get productos por sucursal
    url(r'^get_productos/(?P<id_sucursal>\d+)/$','proyeccion.views.get_productos'),
    
    # Enlace para portada del sitio
    
    url(r'^$', 'proyeccion.views.index'),
    # Enlaces para la aplicacion proyecta
    url(r'^proyeccion/$', 'proyeccion.views.index'),
    # Gestion de usuarios
    url(r'^usuarios/$', 'proyeccion.views.usuarios'),
    url(r'^usuario/(?P<id_usuario>\d+)/$', 'proyeccion.views.usuario'),
    # Gestion de empresas
    url(r'^empresas/$', 'proyeccion.views.empresas'),
    url(r'^empresa/(?P<id_empresa>\d+)/$', 'proyeccion.views.empresa'),
    # Exportar a PDF
    url(r'^reporte_pdf/$','proyeccion.views.reporte_pdf'),
    # Ver estadisticas
    url(r'^estadistica/$','proyeccion.views.estadistica'),
#    url(r'^proyeccion/contact/$', 'proyeccion.views.contact'),
#    url(r'^proyeccion/(?P<proyeccion_id>\d+)/results/$', 'proyeccion.views.results'),
    url(r'^accounts/login/$',  login),
    url(r'^logout/$', logout,{'next_page': '/'}),#(request[, next_page, template_name, redirect_field_name])
    url(r'^assets/(?P<path>.*)$', 'django.views.static.serve',{'document_root': os.path.join(PROJECT_PATH, 'assets') }),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',{'document_root': os.path.join(PROJECT_PATH, 'static') }),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': os.path.join(PROJECT_PATH, 'media') }),

)
