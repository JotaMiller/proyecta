from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'proyecta.views.home', name='home'),
    # url(r'^proyecta/', include('proyecta.foo.urls')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    
    # Enlace para portada del sitio
    
#    url(r'^/', 'proyeccion.views.index'),
    # Enlaces para la aplicacion proyecta
    url(r'^proyeccion/$', 'proyeccion.views.index'),
#    url(r'^proyeccion/contact/$', 'proyeccion.views.contact'),
#    url(r'^proyeccion/(?P<proyeccion_id>\d+)/results/$', 'proyeccion.views.results'),
    url(r'^accounts/login/$',  login),
    url(r'^accounts/logout/$', logout),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': '/home/henux/Trabajos/proyecta/assets'}),

)
