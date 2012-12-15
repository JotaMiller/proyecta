# -*- encoding: utf-8 -*-
# Se realizan los calculos y se envian los datos a los templates(vistas)
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# requerido para la generacion de PDFs
import ho.pisa as pisa
import cStringIO as StringIO
import cgi
from django.template.loader import render_to_string


from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response 
from django.http import HttpResponse
from django.contrib import messages

from django.conf import settings
from django.contrib.auth.decorators import login_required
from forms import UserForm
from forms import EmpresaForm

from datetime import datetime
import calendar

from rpy2 import robjects
from rpy2.robjects.packages import importr
#from rpy2.robjects.lib import forecast

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

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
    path_grafico = ""
    cant_venta = []
    periodos_fechas = ""
    periodo_inicio = ""
    periodo_fin = ""
    periodos = {}
    venta_maxima = 0
    venta_minima = 1
    informacion_ventas = ""
    periodo_proyeccion = ""
    query = request.POST.get('id_sucursal', '')
    id_sucursal     =   ""
    id_producto     =   ""
    
    t_ventas= 1,
    
    if request.method == 'POST':
        #Se obtienen los datos para realizar los calculos 
        id_producto     =   request.POST['producto']
        id_sucursal     =   request.POST['sucursal']
        periodo_proyeccion = int(request.POST['periodo_proyeccion'])

        # Se calculara la proyeccion con dos periodos antes a la fecha seleccionada
        inicio          =   periodo_proyeccion - 2
        termino         =   periodo_proyeccion - 1

        fecha_inicio    =   datetime.strptime(str(inicio) + '-01-01', "%Y-%m-%d")
        fecha_termino   =   datetime.strptime(str(termino) + '-12-31', "%Y-%m-%d")
        
        # anterior
        #fecha_inicio    =   request.POST['fecha_inicio']
        #fecha_termino   =   request.POST['fecha_termino']
        
        #Fecha utilizada para ser transformada y sepatara por año, mes y dia
        #fecha           =   datetime.strptime(fecha_inicio,"%d-%m-%Y").strftime("%Y-%m-%d") 
        #fecha           =   datetime.strptime(fecha,"%Y-%m-%d")
        
        #Fecha utilizada para ser transformada y sepatara por año, mes y dia
        #f_termino       =   datetime.strptime(fecha_termino,"%d-%m-%Y").strftime("%Y-%m-%d") 
        #f_termino       =   datetime.strptime(f_termino,"%Y-%m-%d")
        
        # se envia el nombre a la plantilla para ser mostrada
        # se utiliza el nombre de usuario y la fecha actual en formato unix
        grafico = user.username+'_' + str(time.time()) + '.png'
        
        # Se genera la ruta en la cual se guardara el grafico
        path_grafico = settings.PROJECT_PATH + '/media/graficos/' + grafico
    
        detalle_ventas = total_ventas(id_producto, fecha_inicio, fecha_termino)
        
        ventas = detalle_ventas[0]
        periodos_fechas = detalle_ventas[2]
        informacion_ventas = []
        
        ventas_ts = convert_ts(ventas, inicio, 01,12)
        
        # print ventas_ts

        r('''
        calcular <- function(ventas_ts,path_grafico,inicio_periodo,fecha_inicio, fecha_termino, verbose=FALSE){
            
            yfit <- window(ventas_ts, start=fecha_inicio, end=c(fecha_termino,12))
        
            m2 <- HoltWinters(yfit)
            
            # Prediccion de las ventas, Se establece a 12 meses
            p2 <- predict(m2, n.ahead = 12)
            
            path <- paste(path_grafico)
            
            png(path, width=600, height=600)
            
            plot(c(ventas_ts,p2), col="black", ylim = range(c(ventas_ts, p2)), lwd =1, pch = 20, type ="o", xlab="Periodo", ylab="Cantidad de productos", main="Proyección de ventas")
            
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
        respuesta       = calcular_ventas(ventas_ts,path_grafico, 01, inicio, termino)
        
        # se prepara la lista con las ventas anteriores y las proyectadas
        periodo = 0
        venta_maxima = 0
        inicio_ano = inicio
        inicio_mes = 1
        periodo_inicio = ""
        periodo_fin = ""

        for t_venta_1 in ventas:
            fecha_time = datetime.strptime(str(inicio_ano)+ '-'+ str(inicio_mes) +'-01',"%Y-%m-%d") 
            fecha_time = calendar.timegm(fecha_time.timetuple()) * 1000
            
            # Se establece el inicio del periodo para el eje x
            if periodo_inicio == "":
                periodo_inicio = fecha_time
            
            # print 'periodo inicio: ' + str(periodo_inicio)

            cant_venta.append([fecha_time,t_venta_1])
            informacion_ventas.append({'cantidad': t_venta_1, 'fecha': str(inicio_ano) + '-' + str(inicio_mes) })

            inicio_mes = inicio_mes +1
            if inicio_mes > 12:
                inicio_mes = 1
                inicio_ano = inicio_ano +1
                # print 'un año mas'
                # print inicio_ano 

            periodo = periodo + 1
            if venta_maxima < t_venta_1:
                venta_maxima = t_venta_1

            if venta_minima > t_venta_1:
                venta_minima = t_venta_1
            
        for t_venta_2 in respuesta:
            fecha_time = datetime.strptime(str(inicio_ano)+ '-'+ str(inicio_mes) +'-01',"%Y-%m-%d") 
            fecha_time = calendar.timegm(fecha_time.timetuple()) * 1000

            cant_venta.append([fecha_time,t_venta_2])
            informacion_ventas.append({'cantidad': t_venta_2, 'fecha': str(inicio_ano) + '-' + str(inicio_mes) })

            inicio_mes = inicio_mes +1
            if inicio_mes > 12:
                inicio_mes = 1
                inicio_ano = inicio_ano +1
                # print 'un año mas'
                # print inicio_ano 

            # se establece el ultimo periodo para el eje x
            periodo_fin = fecha_time
            
            if venta_maxima < t_venta_2:
                venta_maxima = t_venta_2
        
        # print cant_venta


        venta_maxima = int(venta_maxima)
        # Se envian los periodos de proyeccion para la gerenacion del grafico
        periodos = { 'inicio': 1, 'termino': periodo }
        messages.success(request, 'La proyección se realizó correctamente, la puede ver en la parte inferior de la página.')
    
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
        'grafico': path_grafico,
        'periodos_fechas': periodos_fechas,
        'periodo_inicio': periodo_inicio,
        'periodo_fin': periodo_fin,
        'informacion_ventas': informacion_ventas,
        'periodo_proyeccion': periodo_proyeccion,
        'id_sucursal': id_sucursal,
        'id_producto': id_producto,
    })
    return render_to_response('proyeccion/index.html',c)
    
def total_ventas(id_producto, fecha_inicio, fecha_termino):
    """
    Funcion que devuelve las ventas realizadas de un determinado
    producto en un periodo de tiempo, solo devuelve el monto de las ventas
    
    las ventas son devueltas en periodos de meses
    """
    # fecha_inicio = datetime.strptime(fecha_inicio,"%d-%m-%Y").strftime("%Y-%m-%d") 
    # fecha_termino = datetime.strptime(fecha_termino,"%d-%m-%Y").strftime("%Y-%m-%d") 
    # fecha_inicio = datetime.strptime(fecha_inicio,"%Y-%m-%d") 
    # fecha_termino = datetime.strptime(fecha_termino,"%Y-%m-%d") 
    
    id_producto = int(id_producto)
    tiempo = Tiempo.objects.filter( fecha__range = (fecha_inicio, fecha_termino)).order_by('fecha')
    ventas_ts = []
    ventas_detalle = []
    detalle_venta = ""
    venta_time = []
    
    cont_ano    =   fecha_inicio.year
    cont_mes    =   fecha_inicio.month
    final_mes   =   12
    
    while ( cont_ano <= fecha_termino.year ):
        print 'añooooo' + str(fecha_inicio)
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
                    if producto.id == id_producto:
                    #venta_total_mes = venta_total_mes + fecha_venta.venta.total_venta
                        venta_total_mes = venta_total_mes + producto.stock 
                
            ventas_detalle.append({'cantidad': venta_total_mes, 'mes': cont_mes, 'ano': cont_ano, 'fecha':  str(cont_ano) +'-'+str(cont_mes) })
            
            fecha_time = datetime.strptime(str(cont_ano)+'-'+str(cont_mes)+'-01',"%Y-%m-%d") 
            venta_time.append([calendar.timegm(fecha_time.timetuple()) * 1000, venta_total_mes])
            
            ventas_ts.append(venta_total_mes)
            cont_mes = cont_mes + 1
            
        cont_ano = cont_ano + 1
        cont_mes = 1
    
    return ventas_ts, ventas_detalle, venta_time

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
        'empresa': empresa,
        'usuario': request.user,
    })
    return render_to_response('proyeccion/usuarios.html',c)

@login_required
def empresas(request):
    """
    Lista de las empresas actualmente registradas en el sistema
    """
    user        =   request.user
    empresas    =   Empresa.objects.all()
    empresa     =   Empresa.objects.get( id = user.empresa.id )
    
    c = RequestContext(request, {
        'user': user,
        'empresas': empresas,
        'empresa': empresa,
        'usuario': request.user,
    })
    return render_to_response('proyeccion/empresas.html',c)

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
                'form': form,
                'empresa': empresa
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

@login_required
def empresa(request, id_empresa):
    user    =   request.user

    if user.empresa:
        empresa = Empresa.objects.get(id=user.empresa.id)
    else:
        empresa = {"logo":"logos/sin_empresa.png"}
    
    dato_empresa = Empresa.objects.get( id=id_empresa )

    if request.method == 'POST':
        # formulario enviado
        form = EmpresaForm(request.POST,request.FILES, instance=dato_empresa)

        if form.is_valid():
            # formulario validado correctamente
            form.save()
            c = RequestContext(request, {
                'user': user,
                'form': form,
                'usuario': request.user,
                'empresa': empresa,
                'dato_empresa': dato_empresa
            })
            messages.success(request, 'La Empresa ha sido actualizada correctamente.')
            return render_to_response('proyeccion/empresa.html',c)
        else:
            messages.error(request, 'Error al intentar editar la Empresa, Favor contacte con un administrador.')
    else:
        # formulario inicial
        form = EmpresaForm(instance=dato_empresa)
    
    c = RequestContext(request, {
        'user': user,
        'form': form,
        'empresa': empresa,
        'dato_empresa': dato_empresa
    })
    return render_to_response('proyeccion/empresa.html',c)
          

def generar_pdf(html):
    # Función para generar el archivo PDF y devolverlo mediante HttpResponse
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), mimetype='application/pdf')
    return HttpResponse('Error al generar el PDF: %s' % cgi.escape(html))

def reporte_pdf(request):
    # Vista que muestra el reporte generado
    fecha_inicio = ""
    id_sucursal     =   ""
    id_producto     =   ""
    if request.method == 'POST':
        #Se obtienen los datos para realizar los calculos 
        cant_ventas     =   request.POST.getlist('cant_ventas')
        fecha_inicio    =   request.POST['fecha_inicio']
        grafico         =   request.POST['grafico']
        id_producto     =   request.POST['id_producto']
        id_sucursal     =   request.POST['id_sucursal']
        periodo         =   fecha_inicio

        sucursal        =   Sucursal.objects.get( id = id_sucursal )
        producto        =   Producto.objects.get( id = id_producto )

        fecha_inicio = int(fecha_inicio) -2

        detalle_ventas = []
        mes = 1
        ano = fecha_inicio

        for venta in cant_ventas:
            detalle_ventas.append({'fecha': str(ano) + '-' + str(mes), 'cantidad': venta })
            mes = mes + 1

            if mes > 12:
                ano = ano + 1
                mes = 1
        
        libro = { 'titulo': 'prueba', 'descripcion': 'Descriocion jahf as' }
        usuario =   request.user
        fecha = datetime.today()
        empresa     =   Empresa.objects.get( id = usuario.empresa.id )
        path_logo = settings.PROJECT_PATH + '/media/' + str(empresa.logo)
        
        
            
        html = render_to_string('reporte_pdf.html', 
                                {
                                 'pagesize':'A4', 
                                 'libro':libro, 
                                 'usuario': usuario,
                                 'fecha': fecha,
                                 'empresa': empresa,
                                 'sucursal': sucursal,
                                 'producto': producto,
                                 'logo': path_logo,
                                 'cant_ventas': cant_ventas,
                                 'grafico': grafico,
                                 'detalle_ventas': detalle_ventas,
                                 'periodo': periodo,
                                 }, context_instance=RequestContext(request))
        return generar_pdf(html)

def get_all_logged_in_users():
    """
    Retorna la lista de usuarios conectados actualmente en el sitio
    """
    # Query all non-expired sessions
    sessions = Session.objects.filter(expire_date__gte=datetime.now())
    uid_list = []

    # Build a list of user ids from that query
    for session in sessions:
        data = session.get_decoded()
        uid_list.append(data.get('_auth_user_id', None))

    # Query all logged in users based on id list
    return User.objects.filter(id__in=uid_list)

def get_productos(request, id_sucursal):
    """
    Devuelte los productos de una respectiva sucursal
    """
    items = ""

    if request.method == 'GET':
        pass
        ventas = Venta.objects.filter( sucursal = id_sucursal )
        for venta in ventas:
            productos = Producto.objects.filter( venta = venta.id )

            for producto in productos:
                items += """
{
    "id": " """ + str(producto.id) + """ ",
    "nombre": " """ + producto.nombre + """ "
},"""
        if items != '':
            items = items[:-1]

        items = '{ "productos":['+ items +'] }'

    return HttpResponse(items, mimetype="application/json")

def estadistica(request):
    """
    Realiza la estadistica del sitio comparando una proyeccion con
    datos de ventas reales para el año seleccionadp
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
    path_grafico = ""
    cant_venta = []
    cant_venta_real = []
    periodos_fechas = ""
    periodo_inicio = ""
    periodo_fin = ""
    periodos = {}
    venta_maxima = 0
    venta_minima = 1
    informacion_ventas = ""
    periodo_proyeccion = ""
    query = request.POST.get('id_sucursal', '')
    id_sucursal     =   ""
    id_producto     =   ""
    
    t_ventas= 1,
    
    if request.method == 'POST':
        #Se obtienen los datos para realizar los calculos 
        id_producto     =   request.POST['producto']
        id_sucursal     =   request.POST['sucursal']
        periodo_proyeccion = int(request.POST['periodo_proyeccion'])

        # Se calculara la proyeccion con dos periodos antes a la fecha seleccionada
        inicio          =   periodo_proyeccion - 2
        termino         =   periodo_proyeccion - 1
        fecha_estadistica = periodo_proyeccion;

        fecha_inicio    =   datetime.strptime(str(inicio) + '-01-01', "%Y-%m-%d")
        fecha_termino   =   datetime.strptime(str(termino) + '-12-31', "%Y-%m-%d")

        fecha_inicio_estadistica    =   datetime.strptime(str(fecha_estadistica) + '-01-01', "%Y-%m-%d")
        fecha_termino_estadistica   =   datetime.strptime(str(fecha_estadistica) + '-12-31', "%Y-%m-%d")
        
        # anterior
        #fecha_inicio    =   request.POST['fecha_inicio']
        #fecha_termino   =   request.POST['fecha_termino']
        
        #Fecha utilizada para ser transformada y sepatara por año, mes y dia
        #fecha           =   datetime.strptime(fecha_inicio,"%d-%m-%Y").strftime("%Y-%m-%d") 
        #fecha           =   datetime.strptime(fecha,"%Y-%m-%d")
        
        #Fecha utilizada para ser transformada y sepatara por año, mes y dia
        #f_termino       =   datetime.strptime(fecha_termino,"%d-%m-%Y").strftime("%Y-%m-%d") 
        #f_termino       =   datetime.strptime(f_termino,"%Y-%m-%d")
        
        # se envia el nombre a la plantilla para ser mostrada
        # se utiliza el nombre de usuario y la fecha actual en formato unix
        grafico = user.username+'_' + str(time.time()) + '.png'
        
        # Se genera la ruta en la cual se guardara el grafico
        path_grafico = settings.PROJECT_PATH + '/media/graficos/' + grafico
    
        detalle_ventas = total_ventas(id_producto, fecha_inicio, fecha_termino)
        ventas = detalle_ventas[0]
        periodos_fechas = detalle_ventas[2]
       
        ventas_reales_periodo = total_ventas(id_producto, fecha_inicio_estadistica, fecha_termino_estadistica)
        ventas_reales = ventas_reales_periodo[0]


        informacion_ventas = []
        
        ventas_ts = convert_ts(ventas, inicio, 01,12)
        
        # print ventas_ts

        r('''
        calcular <- function(ventas_ts,path_grafico,inicio_periodo,fecha_inicio, fecha_termino, verbose=FALSE){
            
            yfit <- window(ventas_ts, start=fecha_inicio, end=c(fecha_termino,12))
        
            m2 <- HoltWinters(yfit)
            
            # Prediccion de las ventas, Se establece a 12 meses
            p2 <- predict(m2, n.ahead = 12)
            
            path <- paste(path_grafico)
            
            png(path, width=600, height=600)
            
            plot(c(ventas_ts,p2), col="black", ylim = range(c(ventas_ts, p2)), lwd =1, pch = 20, type ="o", xlab="Periodo", ylab="Cantidad de productos", main="Proyección de ventas")
            
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
        respuesta       = calcular_ventas(ventas_ts,path_grafico, 01, inicio, termino)
        
        # se prepara la lista con las ventas anteriores y las proyectadas
        periodo = 0
        venta_maxima = 0
        venta_minima = 1
        inicio_ano = inicio
        inicio_mes = 1
        inicio_mes2 = 1
        periodo_inicio = ""
        periodo_fin = ""

        # for t_venta_1 in ventas:
        #     fecha_time = datetime.strptime(str(inicio_ano)+ '-'+ str(inicio_mes) +'-01',"%Y-%m-%d") 
        #     fecha_time = calendar.timegm(fecha_time.timetuple()) * 1000
            
        #     # Se establece el inicio del periodo para el eje x
        #     if periodo_inicio == "":
        #         periodo_inicio = fecha_time
            
        #     # print 'periodo inicio: ' + str(periodo_inicio)

        #     cant_venta.append([fecha_time,t_venta_1])
        #     informacion_ventas.append({'cantidad': t_venta_1, 'fecha': str(inicio_ano) + '-' + str(inicio_mes) })

        #     inicio_mes = inicio_mes +1
        #     if inicio_mes > 12:
        #         inicio_mes = 1
        #         inicio_ano = inicio_ano +1
        #         print 'un año mas'
        #         print inicio_ano 

        #     periodo = periodo + 1
        #     if venta_maxima < t_venta_1:
        #         venta_maxima = t_venta_1
          

        for t_ventas_reales in ventas_reales:
            fecha_time = datetime.strptime(str(fecha_estadistica)+ '-'+ str(inicio_mes2) +'-01',"%Y-%m-%d") 
            fecha_time = calendar.timegm(fecha_time.timetuple()) * 1000

            print fecha_termino
            cant_venta_real.append([fecha_time,t_ventas_reales])

            inicio_mes2 = inicio_mes2 +1
            if inicio_mes2 > 12:
                inicio_mes2 = 1

            if venta_maxima < t_ventas_reales:
                venta_maxima = t_ventas_reales

            if venta_minima > t_ventas_reales:
                venta_minima = t_ventas_reales
        # 
        # Datos de venta proyectados
        # 
        for t_venta_2 in respuesta:
            fecha_time = datetime.strptime(str(fecha_estadistica)+ '-'+ str(inicio_mes) +'-01',"%Y-%m-%d") 
            fecha_time = calendar.timegm(fecha_time.timetuple()) * 1000
            if periodo_inicio == "":
                periodo_inicio = fecha_time

            cant_venta.append([fecha_time,t_venta_2])
            informacion_ventas.append({'cantidad': t_venta_2, 'fecha': str(inicio_ano) + '-' + str(inicio_mes) })

            inicio_mes = inicio_mes +1
            if inicio_mes > 12:
                inicio_mes = 1
                inicio_ano = inicio_ano +1
                # print 'un año mas'
                # print inicio_ano 

            # se establece el ultimo periodo para el eje x
            periodo_fin = fecha_time
            
            if venta_maxima < t_venta_2:
                venta_maxima = t_venta_2

            if venta_minima > t_venta_2:
                venta_minima = t_venta_2
        
        # print cant_venta


        venta_maxima = int(venta_maxima)
        # Se envian los periodos de proyeccion para la gerenacion del grafico
        periodos = { 'inicio': 1, 'termino': periodo }
        messages.success(request, 'La proyección se realizó correctamente, la puede ver en la parte inferior de la página.')
    
    c = RequestContext(request, {
        'ventas': ventas,
        'ventas_reales': cant_venta_real,
        'cant_venta': cant_venta,
        'periodos': periodos,
        'venta_maxima': venta_maxima,
        'venta_minima': venta_minima,
        'productos': productos,
        'sucursales': sucursales,
        'grafico': grafico,
        't_ventas': t_ventas,
        'empresa': empresa,
        'usuario': request.user,
        'id_ventas': id_venta,
        'ids_sucursales': ids_sucursales,
        'grafico': path_grafico,
        'periodos_fechas': periodos_fechas,
        'periodo_inicio': periodo_inicio,
        'periodo_fin': periodo_fin,
        'informacion_ventas': informacion_ventas,
        'periodo_proyeccion': periodo_proyeccion,
        'id_sucursal': id_sucursal,
        'id_producto': id_producto,
    })
    return render_to_response('proyeccion/estadistica.html',c)

