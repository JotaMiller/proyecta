# -*- encoding: utf-8 -*-
# Create your views here.

from django.http import HttpResponse
import json
import cgi

import time
from time import mktime
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
 		request.session['chatHistory'] = {}

 	try:
 		request.session['openChatBoxes']
 	except Exception, e:
 		request.session['openChatBoxes'] = {}

	try:
		request.session['tsChatBoxes']
	except Exception, e:
		request.session['tsChatBoxes'] = {}

	# Inicio Proceso	
	action = request.GET.get('action', '')
	
	if  action == 'chatheartbeat':
		return chatHeartbeat(request)
	
	if  action == 'sendchat':
		return sendChat(request)
		
	if  action == 'closechat':
		return closeChat(request)
		
	if  action == 'startchatsession':
		return startChatSession(request)



	return HttpResponse("Mini chat for Django :)")

def chatHeartbeat(request):
	"""
	"""

	chats 	=	Chat.objects.filter( to=request.user, recd = 0 ).order_by('id')
	items = ""

	chatBoxes = []
	for chat in chats:

		# Se verifica Se se encuentra inicializada la sesion
		try:
			request.session['openChatBoxes'][chat.message_from]
		except Exception, e:
			request.session['openChatBoxes'][chat.message_from] = ''

		try:
			request.session['chatHistory'][chat.message_from]
		except Exception, e:
			request.session['chatHistory'][chat.message_from] = ''


		if request.session['openChatBoxes'][chat.message_from] == '' and request.session['chatHistory'][chat.message_from] != '':
			items = request.session['chatHistory'][chat.message_from]
		
		# print chat.message_from
		# chat.message = sanitize(chat.message)

		items = items + """
{ 
	"s": "0",
	"f": " """ + chat.message_from + """ ",
	"m": " """ + chat.message + """ "
},""" 

		# if request.session['chatHistory'][chat.message_from] == '':
		# 	request.session['chatHistory'][chat.message_from] = ''
		
		request.session['chatHistory'][chat.message_from] += """
{
	"s": "0",
	"f": " """ + chat.message_from + """ ",
	"m": " """ + chat.message + """ "
},"""
	
		try:
			del request.session['tsChatBoxes'][chat.message_from]
			# print 'borro tsChatBoxes'
		except Exception, e:
			pass

		request.session['openChatBoxes'][chat.message_from] = chat.sent

	# print request.session['openChatBoxes']

	if  request.session['openChatBoxes'] :

		for chatbox  in request.session['openChatBoxes']:

			date_time = request.session['openChatBoxes'][chatbox]
			try:
				request.session['tsChatBoxes'][chatbox]
			except Exception, e:
				request.session['tsChatBoxes'][chatbox] = ''
				pass

			if request.session['tsChatBoxes'][chatbox] == '':
				now =  time.time() - mktime(date_time.timetuple())+1e-6*date_time.microsecond

				fecha = date_time.strftime("%d %b - %H:%M")

				message = "Enviado el " + str(fecha)

				if now > 180:
					items += """
{
	"s": "2",
	"f": " """ + chatbox +""" ",
	"m": "{""" + message +"""} "
},"""
				try:
					request.session['chatHistory'][chatbox]
				except Exception, e:
					request.session['chatHistory'][chatbox] = ''
				
				request.session['chatHistory'][chatbox] += """
{
	"s": "2",
	"f": " """ + chatbox +""" ",
	"m": "{""" + message +"""} "
},"""
				request.session['tsChatBoxes'][chatbox] = 1

			pass
		pass

	# Actualizar
	Chat.objects.filter( to = request.user, recd = 0 ).update( recd=1 )
	if items != '':
		items = items[:-1]
		pass
	# print items
	# print request.session['openChatBoxes']

	item_wrapper = '{ "items":['+ items +'] }'
	return HttpResponse(item_wrapper, mimetype="application/json")

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
	# print request.session['openChatBoxes']
	# print 'fuera '
	try:
		request.session['openChatBoxes']
	except Exception, e:
		request.session['openChatBoxes'] = {}
	
	if request.session['openChatBoxes']:
		for chatbox  in request.session['openChatBoxes']:
				
			try:
				item += request.session['chatHistory'][chatbox]
			except Exception, e:
				raise e
				# items +=  chatBoxSession(request, chatbox)

	if items != '':
		items = items[0:-1]
		pass

	valores = '{ "username": "'+ str(request.user) +'","items": [' + items + ']}'

	return HttpResponse(valores, mimetype="application/json")

def sendChat(request):
	message_from 	=	str(request.user)
	to 				= 	request.POST['to']
	message 		=	request.POST['message']


	request.session['openChatBoxes'][to] = datetime.now()

	# messagesan = sanitize(message)
	try:
		request.session['chatHistory'][to]
	except Exception, e:
		request.session['chatHistory'][to] = ''
	
	request.session['chatHistory'][to] += """
{
	"s": "1",
	"f": "{""" + to + """}",
	"m": "{""" + message + """}"
},"""
	try:
		del request.session['tsChatBoxes'][to]
	except Exception, e:
		pass


	chat = Chat(message_from=message_from, to=to, message=message, sent= datetime.now(), recd=0)
	chat.save(force_insert=True)

	return HttpResponse('1')

def closeChat(request):

	chatbox = request.POST['chatbox']
	print request.POST['chatbox']
	print chatbox
	
	del request.session['openChatBoxes'][chatbox]
	
	return HttpResponse('1')

def sanitize(text):
	text = cgi.escape(text, True)
	# text = htmlspecialchars(text, ENT_QUOTES);
	text = text.replace("\n\r","\n",text);
	text = text.replace("\r\n","\n",text);
	text = text.replace("\n","<br>",text);

	return text