# -*- encoding: utf-8 -*-
# Se realizan los calculos y se envian los datos a los templates(vistas)
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
 

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
from proyeccion.models import Tiempo
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
        sucursales = Sucursal.objects.filter( empresa_id = empresa.id )
    else:
        empresa = {"logo":"logos/sin_empresa.png", "id": "0"}
        sucursales = Sucursal.objects.filter( empresa_id = empresa['id'] )

    
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
    ventas2 = False
    respuesta = ""
    cant_venta = []
    periodos = {}
    venta_maxima = 0
    query = request.POST.get('id_sucursal', '')
    
    t_ventas= 1,
    
    if request.method == 'POST':
        #Se obtienen los datos para realizar los calculos 
        id_producto     =   request.POST['producto']
        id_sucursal     =   request.POST['sucursal']
        fecha_inicio    =   request.POST['fecha_inicio']
        fecha_termino   =   request.POST['fecha_termino']
        
        #Fecha utilizada para ser transformada y sepatara por año, mes y dia
        fecha           =   datetime.strptime(fecha_inicio,"%d-%m-%Y").strftime("%Y-%m-%d") 
        fecha           =   datetime.strptime(fecha,"%Y-%m-%d")
        
        #Fecha utilizada para ser transformada y sepatara por año, mes y dia
        f_termino       =   datetime.strptime(fecha_termino,"%d-%m-%Y").strftime("%Y-%m-%d") 
        f_termino       =   datetime.strptime(f_termino,"%Y-%m-%d")
        
        # se envia el nombre a la plantilla para ser mostrada
        # se utiliza el nombre de usuario y la fecha actual en formato unix
        grafico = user.username+'_' + str(time.time()) + '.png'
        
        # Se genera la ruta en la cual se guardara el grafico
        path_grafico = settings.PROJECT_PATH + '/media/graficos/' + grafico
    
        detalle_ventas = total_ventas(id_producto, fecha_inicio, fecha_termino)
        
        ventas = detalle_ventas[0]
        
        ventas_ts = convert_ts(ventas, fecha.year, fecha.month,12)
        
        print ventas_ts
        r('''
        calcular <- function(ventas_ts,path_grafico,inicio_periodo,fecha_inicio, fecha_termino, verbose=FALSE){
            
            yfit <- window(ventas_ts, start=fecha_inicio, end=c(fecha_termino,12))
        
            m2 <- HoltWinters(yfit)
            
            # Prediccion de las ventas, Se establece a 12 meses
            p2 <- predict(m2, n.ahead = 48)
            
            path <- paste(path_grafico)
            
            png(path, width=600, height=600)
            
            plot(ventas_ts, col="black", ylim = range(c(ventas_ts, p2)), lwd =1, pch = 20, type ="o", xlab="Periodo", ylab="Cantidad de productos", main="Proyección de ventas")
            
             lines(fitted(m2)[,1], col = "blue", lwd =2)
            lines(p2, col="red", lwd=2)
            
            # Muestra la grilla para el grafico
            grid()
            
            # Linea divisora para mostrar la diferencia entre la proyeccion y lo real
            abline(v=(fecha_termino+11/12), col="red")
            dev.off()
            
            return(p2)
        }
        
        ''')
        # Funcion directamente de R quien se encarga de realizar los calculos
        calcular_ventas = r['calcular']
        
        # Se ejecuta la funcion de calculos de ventas
        # el grafico se guarda en formato png en el directorio graficos
        respuesta       = calcular_ventas(ventas_ts,path_grafico, fecha.month, fecha.year, f_termino.year)
        
        # se prepara la lista con las ventas anteriores y las proyectadas
        periodo = 0
        venta_maxima = 0
        for t_venta_1 in ventas:
            cant_venta.append( t_venta_1)
            
            periodo = periodo + 1
            if venta_maxima < t_venta_1:
                venta_maxima = t_venta_1
            
        for t_venta_2 in respuesta:
            cant_venta.append(t_venta_2)
            periodo = periodo + 1
            
            if venta_maxima < t_venta_2:
                venta_maxima = t_venta_2
        
        venta_maxima = int(venta_maxima)
        # Se envian los periodos de proyeccion para la gerenacion del grafico
        periodos = { 'inicio': 1, 'termino': periodo }
    
    t = loader.get_template('proyeccion/index.html')
    c = RequestContext(request, {
        'ventas': ventas,
        'cant_venta': cant_venta,
        'periodos': periodos,
        'venta_maxima': venta_maxima,
        'productos': productos,
        'sucursales': sucursales,
        'grafico': grafico,
        't_ventas': t_ventas,
        'empresa': empresa,
        'usuario': request.user,
        'id_ventas': id_venta,
        'ids_sucursales': ids_sucursales,
    })
    return render_to_response('proyeccion/index.html',c)
    
def total_ventas(id_producto, fecha_inicio, fecha_termino):
    """
    Funcion que devuelve las ventas realizadas de un determinado
    producto en un periodo de tiempo, solo devuelve el monto de las ventas
    
    las ventas son devueltas en periodos de meses
    """
    fecha_inicio = datetime.strptime(fecha_inicio,"%d-%m-%Y").strftime("%Y-%m-%d") 
    fecha_termino = datetime.strptime(fecha_termino,"%d-%m-%Y").strftime("%Y-%m-%d") 
    fecha_inicio = datetime.strptime(fecha_inicio,"%Y-%m-%d") 
    fecha_termino = datetime.strptime(fecha_termino,"%Y-%m-%d") 
    
    id_producto = int(id_producto)
    tiempo = Tiempo.objects.filter( fecha__range = (fecha_inicio, fecha_termino)).order_by('fecha')
    ventas_ts = []
    ventas_detalle = []
    detalle_venta = ""
    
    cont_ano    =   fecha_inicio.year
    cont_mes    =   fecha_inicio.month
    final_mes   =   12
    
    while ( cont_ano <= fecha_termino.year ):
        if cont_ano == fecha_termino.year:
            final_mes = fecha_termino.month
        while ( cont_mes <= final_mes ):
        #TODO: falta iteracion para recorrer meses
            fecha_ventas = Tiempo.objects.filter( fecha__month = cont_mes ).filter( fecha__year = cont_ano )
            
            venta_total_mes = 0
            for fecha_venta in fecha_ventas:
                productos = Producto.objects.filter( venta = fecha_venta.venta )
                
                #TODO: se filtra por productos ventidos en determinado tiempo
                # Borrar comentario...
                
                for producto in productos:
                #    if producto.id == id_producto:
                    #venta_total_mes = venta_total_mes + fecha_venta.venta.total_venta
                    venta_total_mes = venta_total_mes + producto.stock 
                
            ventas_detalle.append({'cantidad': venta_total_mes, 'mes': cont_mes, 'ano': cont_ano})
            ventas_ts.append(venta_total_mes)
            cont_mes = cont_mes + 1
            
        cont_ano = cont_ano + 1
        cont_mes = 1
    
    return ventas_ts, ventas_detalle

def convert_ts(time_series, start_year=2000, start_pd=1, freq=12):
     """
     Convierte una serie de datos dentro de un objeto rpy2
     los transforma a un objeto de tipo 'ts'
     """
     r_ts = robjects.r.ts(robjects.FloatVector(time_series),start=robjects.r.c(start_year,start_pd), frequency=freq)
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
        empresa = {"logo":"logos/sin_empresa.png"}
    
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
          
def exportar_PDF(request):
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'
    
    grafico = "/home/jotamiller/Trabajos/proyecta/proyecta/media/graficos/admin_1352685801.59.png"

    c = canvas.Canvas(response)
    c.setLineWidth(.3)
    c.setFont('Helvetica', 12)
    
    # Cabecera
    c.drawString(10,703,'EMPRESA:')
    c.line(120,700,580,700)
    c.drawString(120,703,"NOMBRE EMPRESA")
    
    # Grafico
    c.drawImage(grafico, 10, 200, 400, 400, None, True)
    
    c.showPage()
    c.save()
    return response