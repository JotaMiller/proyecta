#===============================================================================
# minichat
# Mini Aplicacion que crea chats 1 a 1,
# 
# @author: JotaMiller
# @contact: hola@jotamiller.cl 
#===============================================================================
from django.db import models

class Chat(models.Model):
    """
    Clase que guarda las conversaciones de los usuarios
    """
    message_from    =   models.CharField( max_length = 100 )
    to              =   models.CharField( max_length = 100 )
    message         =   models.TextField()
    sent            =   models.DateTimeField()
    recd            =   models.IntegerField()
    
