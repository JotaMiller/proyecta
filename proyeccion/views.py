# Se realizan los calculos y se envian los datos a los templates(vistas)
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response 
from django.http import HttpResponse
from django.contrib import messages

from django.conf import settings
from django.contrib.auth.decorators import login_required
from forms import UserForm

from datetime import datetime

from rpy2 import robjects
from rpy2.robjects.packages import importr
#from rpy2.robjects.lib import forecast

from proyeccion.models import Venta
from proyeccion.models import Producto
from proyeccion.models import Sucursal
from proyeccion.models import Empresa
from proyeccion.models import User

import random
import time
import os
@login_required
def index(request):
    """
    Index - Portada de la aplicacion
    """
    #PROJECT_PATH = os.path.relpath(os.path.dirname(__file__),'../../')

    user = request.user
    if user.empresa:
        empresa = Empresa.objects.get(id=user.empresa.id)
    else:
        empresa = ({"logo":"logos/sin_empresa.png"})
    
    # se listan solo las sucursales asociadas a la empresa del usuario
    sucursales = Sucursal.objects.filter( empresa_id = user.empresa.id )
    
    ids_sucursales = []
    for sucursal in sucursales:
        ids_sucursales.append(sucursal.id)
    
    # se listan solo las ventas realizadas en las sucursal
    # con sus productos relacionados
    ventas = Venta.objects.filter( sucursal__in = ids_sucursales )
    
    id_venta = []
    for venta in ventas:
        id_venta.append(venta.id)
    
    # productos relacionados con las ventas de cada sucursal
    productos = Producto.objects.filter( venta_id__in = id_venta )
    
    
    
    grdevices = importr('grDevices')
    forecast = importr('forecast')
    r = robjects.r
    
    grafico = False
    
    
    #form = ConsultaForm(initial={'fecha_inicio': '14-11-1986','fecha_termino': '20-02-2012'})
    
    query = request.POST.get('id_sucursal', '')
    
    t_ventas= 1,
    
    if request.method == 'POST':
         #Se obtienen los datos para realizar los calculos 
        id_producto     =   request.POST['producto']
        id_sucursal     =   request.POST['sucursal']
        fecha_inicio    =   request.POST['fecha_inicio']
        fecha_termino   =   request.POST['fecha_termino']
        #t_ventas = total_ventas(id_producto)
        
        # se envia el nombre a la plantilla para ser mostrada
        # se utiliza el nombre de usuario y la fecha actual en formato unix
        grafico = user.username+'_' + str(time.time()) + '.png'
        
        # Se genera la ruta en la cual se guardara el grafico
        span = settings.PROJECT_PATH + '/media/graficos/' + grafico
    
        ventas = (72,79,77,59,61,80,72,53,60,67,60,63,
              67,68,67,72,54,74,59,69,80,56,77,78,
              54,59,51,62,76,60,68,62,67,78,67,58,
              69,55,73,78,80,73,76,75,63,74,63,65,
              74,53,73,52,51,67,77,73,63,71,74,64)

        salida = convert_ts(ventas, 2008, 1,12)
        r('''
        calcular <- function(ventas,span, verbose=FALSE){
            gasdem <- ts(data=ventas,start=2006, frequency=12)
            yfit <- window(gasdem, end=c(2010,12))
        
            m2 <- HoltWinters(yfit)
            p2 <- predict(m2, n.ahead = 36)
            
            path <- paste(span)
            
            png(path, width=600, height=600)
            
            plot(gasdem, col="black", ylim = range(c(gasdem, p2)), lwd =1, pch = 20, type ="o", xlab="Periodo", ylab="Cantidad de productos", main="Proyeccion de ventas")
            lines(fitted(m2)[,1], col = "blue", lwd =2)
            lines(p2, col="red", lwd=2)
            grid()
            
            abline(v=(2010+11/12), col="red")
            dev.off()
        }
        
        ''')
        
        calcular_ventas = r['calcular']
        res             = calcular_ventas(salida,span)
#        dato = request.POST['sucursal']
#       
       
#        
#        datos_ventas = Venta.objects.filter(productos= id_producto, fecha__range=('1990-01-01', '2020-01-01'))
#        
#        venta_uni = Venta.objects.dates('fecha', 'year')
##        for venta in datos_ventas:
##            venta_uni += (Venta.objects.dates('fecha','day'), )
#        
##        for item in datos_ventas:
##            item_producto = item.productos.all()
##            datos_productos.append(item_producto.all().values('precio', 'stock'))
#            #productos.append(item.productos.all())  
    

    REPORTES = (
        (1, 'Torta',),
        (2, 'Barra',),
        (3, 'otro',),
    )
    
    
    t = loader.get_template('proyeccion/index.html')
    c = RequestContext(request, {
        'reportes': REPORTES,
        'ventas': ventas,
        'productos': productos,
        'sucursales': sucursales,
        'grafico': grafico,
        't_ventas': t_ventas,
        'empresa': empresa,
        'usuario': request.user,
        'id_ventas': id_venta,
        'ids_sucursales': ids_sucursales
#        'datos_ventas': datos_ventas,
#        'datos_productos': datos_productos,
#        'venta_uni': venta_uni,
#        'salida': salida,
    })
    return render_to_response('proyeccion/index.html',c)
    
def total_ventas(producto):
    producto = Producto.objects.get(2)
    producto.venta.all()
    return producto

def convert_ts(time_series, start_year=2000, start_pd=1, freq=12):
     """
     Convierte una serie de datos dentro de un objeto rpy2
     los transforma a un objeto de tipo 'ts'
     """
     r_ts = robjects.r.ts(robjects.FloatVector(time_series),
                          start=robjects.r.c(start_year,start_pd), frequency=freq)
     return r_ts
 
@login_required
def usuarios(request):
    user        =   request.user
    usuarios    =   User.objects.all()
    empresa     =   Empresa.objects.get( id = user.empresa.id )
    
    c = RequestContext(request, {
        'user': user,
        'usuarios': usuarios,
        'empresa': empresa
    })
    return render_to_response('proyeccion/usuarios.html',c)

@login_required
def usuario(request, id_usuario):
    user    =   request.user
    usuario =   User.objects.get( id=id_usuario )
    if user.empresa:
        empresa = Empresa.objects.get(id=user.empresa.id)
    else:
        empresa = ({"logo":"logos/sin_empresa.png"})
    
    if request.method == 'POST':
        # formulario enviado
        form = UserForm(request.POST,request.FILES, instance=usuario)

        if form.is_valid():
            # formulario validado correctamente
            form.save()
            c = RequestContext(request, {
                'user': user,
                'usuario': usuario,
                'form': form
            })
            messages.success(request, 'El usuario ha sido actualizado correctamente.')
            return render_to_response('proyeccion/usuario.html',c)
        else:
            messages.error(request, 'Error al intentar editar el usuario, Favor contacte con un administrador.')
    else:
        # formulario inicial
        form = UserForm(instance=usuario)
    
    c = RequestContext(request, {
        'user': user,
        'usuario': usuario,
        'form': form,
        'empresa': empresa
    })
    return render_to_response('proyeccion/usuario.html',c)
          