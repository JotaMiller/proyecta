from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'proyecta.views.home', name='home'),
    # url(r'^proyecta/', include('proyecta.foo.urls')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    
    # Enlaces para la aplicacion proyecta
    url(r'^proyeccion/$', 'proyeccion.views.index'),
    url(r'^proyeccion/(?P<proyeccion_id>\d+)/results/$', 'proyeccion.views.results'),
)
