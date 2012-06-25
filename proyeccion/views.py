# Se realizan los calculos y se envian los datos a los templates(vistas)
 
from django.http import HttpResponse

def index(request):
    """ Index - Portada de la aplicacion """
    return HttpResponse("Hello, world. You're at the poll index.")

# @param poll_id: Id de la proyeccion realizada 
def results(request, proyeccion_id):
    """ Resultado de la proyeccion """ 
    return HttpResponse("El resultado de la proyeccion Numero:%s es" % proyeccion_id)