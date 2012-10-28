# Se realizan los calculos y se envian los datos a los templates(vistas)
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response 
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required
from forms import ConsultaForm

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

@login_required
def index(request):
    """
    Index - Portada de la aplicacion
    """
    usuario = request.user
    perfil = ""
    empresa = Empresa.objects.all()
    ventas = Venta.objects.all()
    productos = Producto.objects.all()
    sucursales = Sucursal.objects.all()
    
    grdevices = importr('grDevices')
    forecast = importr('forecast')
    r = robjects.r
    span = time.time()
    form = ConsultaForm(initial={'fecha_inicio': '14-11-1986',
                                 'fecha_termino': '20-02-2012'})
    
    query = request.POST.get('id_sucursal', '')
    
    t_ventas= 1,
    
    if request.method == 'POST':
        id_producto =   request.POST['producto']
        #t_ventas = total_ventas(id_producto)
        
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
            
            path <- paste('/home/henux/Trabajos/proyecta/assets/graficos/',span,'.png')
            
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
        res = calcular_ventas(salida,span)
#        dato = request.POST['sucursal']
#        
#        id_producto = request.POST['producto']
#        fecha_inicio = request.POST['fecha_inicio']
#        fecha_termino = request.POST['fecha_termino']
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
        'form': form,
        'reportes': REPORTES,
        'ventas': ventas,
        'productos': productos,
        'sucursales': sucursales,
        'grafico': span,
        't_ventas': t_ventas,
        'empresa': empresa,
        'usuario': request.user,
        'perfil': perfil
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
    usuario     =   request.user
    usuarios    =   User.objects.all()
    
    c = RequestContext(request, {
        'usuario': usuario,
        'usuarios': usuarios
    })
    return render_to_response('proyeccion/usuarios.html',c)

@login_required
def usuario(request, id_usuario):
    usuario     =   request.user
    usuarios    =   User.objects.get( id=id_usuario )
    
    c = RequestContext(request, {
        'usuario': usuario,
        'usuarios': usuarios
    })
    return render_to_response('proyeccion/usuario.html',c)
          