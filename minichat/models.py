#===============================================================================
# minichat
# Mini Aplicacion que crea chats 1 a 1,
# 
# @author: JotaMiller
# @contact: hola@jotamiller.cl 
#===============================================================================
from django.db import models

class Mensaje(models.Model):
    """
    Clase que guarda las conversaciones de los usuarios
    """
    msg_from    =   models.CharField( max_length = 100 )
    msg_to      =   models.CharField( max_length = 100 )
    msg_text    =   models.CharField( max_length = 250 )
    fecha       =   models.DateField()
    
    def __str__(self):
        """
        devuelve el texto del mensaje
        """
        return self.msg_text
