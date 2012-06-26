# Se realizan los calculos y se envian los datos a los templates(vistas)
 
from django.http import HttpResponse
from rpy2 import robjects
from rpy2.robjects.packages import importr
import random

def index(request):
    """ Index - Portada de la aplicacion """
    
    ran = random.random()
    
    # Lib traficos
    grdevices = importr('grDevices')

    # Generar grafico aca
    r = robjects.r
    
    x = [1,2,3,5,4,7,2,1]
    y = [2,4,2,6,6,6,4,2]
    
    nombre = 'graficos/%fgrafico.png' % (ran)
    r.png(nombre,width=500,height=400)
    r.plot(x,y)

    grdevices.dev_off()

    return HttpResponse()

# @param poll_id: Id de la proyeccion realizada 
def results(request, proyeccion_id):
    """ Resultado de la proyeccion """ 
    
    return HttpResponse("El resultado de la proyeccion Numero:%s es" % proyeccion_id)