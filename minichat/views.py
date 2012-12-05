# -*- encoding: utf-8 -*-
# Create your views here.

from django.http import HttpResponse
import json
import cgi

import time
from datetime import datetime
# Modelo
from minichat.models import Chat

DBPATH = 'localhost'
DBUSER = 'root'
DBPASS = 'password'
DBNAME = 'chat'

def index(request):
	"""
	Inicio de la aplicación quien controla el minichat
	"""
	# Verificacion si la la session se encuentra definda o no
 	try:
 		request.session['chatHistory']
 	except Exception, e:
 		request.session['chatHistory'] = None

	if request.session['chatHistory'] is None:
		request.session['chatHistory'] = {}

 	try:
 		request.session['openChatBoxes']
 	except Exception, e:
 		request.session['openChatBoxes'] = None

	if request.session['openChatBoxes'] is None:
		request.session['openChatBoxes'] = {}

	# Inicio Proceso	
	action = request.GET.get('action', '')
	
	if  action == 'chatheartbeat':
		return chatHeartbeat(request)
	
	if  action == 'sendchat':
		return sendChat()
		
	if  action == 'closechat':
		return closeChat()
		
	if  action == 'startchatsession':
		return startChatSession()


	return HttpResponse("Mini chat for Django :)")

def chatHeartbeat(request):
	"""
	"""

	chats 	=	Chat.objects.filter( to=request.user, recd = 1 ).order_by('id')

	items = ""

	chatBoxes = []
	for chat in chats:

		# Se verifica Se se encuentra inicializada la sesion
		try:
			request.session['openChatBoxes'][chat.message_from]
		except Exception, e:
			request.session['openChatBoxes'][chat.message_from] = None

		try:
			request.session['chatHistory'][chat.message_from]
		except Exception, e:
			request.session['chatHistory'][chat.message_from] = None


		if request.session['openChatBoxes'][chat.message_from] is None and request.session['chatHistory'][chat.message_from] != None:
			items = request.session['chatHistory'][chat.message_from]
		
		# chat.message = sanitize(chat.message)

		items = items + """
{ 
	's': '0'
	'f': '""" + chat.message_from + """'
	'm': '""" + chat.message + """'
},
""" 

		if request.session['chatHistory'][chat.message_from] is None:
			request.session['chatHistory'][chat.message_from] = ''
		
		request.session['chatHistory'][chat.message_from] = """
{
	's': '0'
	'f': '""" + chat.message_from + """'
	'm': '""" + chat.message + """'
},
"""
	
		try:
			del request.session['tsChatBoxes'][chat.message_from]
		except Exception, e:
			pass

		request.session['openChatBoxes'][chat.message_from] = chat.sent

	if not request.session['openChatBoxes']:
		for (chatbox, time) in request.session['openChatBoxes']:
			try:
				request.session['tsChatBoxes'][chatbox]
			except Exception, e:
				request.session['tsChatBoxes'][chatbox] = None

			if request.session['tsChatBoxes'][chatbox] == None:
				now =  datetime.today()
				time = now

				message = "Enviado el " + now

				if now > 180:
					items = items + """
{
	's': '2',
	'f': '""" + chatbox +"""',
	'm': '{""" + message +"""}'
},
"""
				try:
					request.session['chatHistory'][chatbox]
				except Exception, e:
					request.session['chatHistory'][chatbox] = ''
				
				request.session['chatHistory'][chatbox] = """
{
	's': '2',
	'f': '""" + chatbox +"""',
	'm': '{""" + message +"""}'
},
"""

			pass
		pass

	# Actualizar
	Chat.objects.filter( to = request.user, recd = 0 ).update( recd=1 )
	if items != '':
		items = items[0:-1]
		pass
	print items
	print request.session['openChatBoxes']


	return HttpResponse(json.dumps(items), mimetype="application/json")

def chatBoxSession(request, chatbox):
	items = ""
	try:
		request.session['chatHistory'][chatbox]
	except Exception, e:
		request.session['chatHistory'][chatbox] = None
	
	if request.session['chatHistory'][chatbox] != None:
		items = request.session['chatHistory'][chatbox]

	return items

def startChatSession(request):
	items = ""
	if not request.session['openChatBoxes']:
		for (chatbox, void) in request.session['openChatBoxes']:
			items = items + chatBoxSession(request, chatbox)
			pass
		pass

	if items != "":
		items = items[0:-1]
		pass

	valores = """
{
	'username': '""" + request.user + """',
	'items': [
		""" + items + """
	]
}
"""
	return HttpResponse(json.dumps(valores), mimetype="application/json")

def sendChat(request):
	message_from 	=	request.user
	to 				= 	request.POST['to']
	message 		=	request.POST['message']

	request.session['openChatBoxes'][to] = datetime.now

	# messagesan = sanitize(message)
	try:
		request.session['chatHistory'][to]
	except Exception, e:
		request.session['chatHistory'][to] = ''
	
	request.session['chatHistory'][to] += """
{
	's': '1',
	'f': '{""" + to + """}',
	'm': '{""" + messagesan + """}'
},
"""
	del request.session['tsChatBoxes'][to]

	chat = Chat(message_from=message_from, to=to, message=message, sent= datetime.now)
	chat.save(force_insert=True)

	return HttpResponse('1')

def closeChat():

	del request.session['openChatBoxes'][request.POST['chatbox']]

	return HttpResponse('1')

	pass

def sanitize(text):
	text = cgi.escape(text, True)
	# text = htmlspecialchars(text, ENT_QUOTES);
	text = text.replace("\n\r","\n",text);
	text = text.replace("\r\n","\n",text);
	text = text.replace("\n","<br>",text);

	return text