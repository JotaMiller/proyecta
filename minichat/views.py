# -*- encoding: utf-8 -*-
# Create your views here.

from django.http import HttpResponse
import json
import cgi

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
	action = request.GET.get('action', '')
	
	if  action == 'chatheartbeat':
		return chatHeartbeat(request)
	
	if  action == 'sendchat':
		return sendChat()
		
	if  action == 'closechat':
		return closeChat()
		
	if  action == 'startchatsession':
		return startChatSession()

	# Verificacion si la la session se encuentra definda o no
 	try:
 		request.session['chatHistory']
 	except Exception, e:
 		request.session['chatHistory'] = None

	if request.session['chatHistory'] is None:
		request.session['chatHistory'] = []

 	try:
 		request.session['openChatBoxes']
 	except Exception, e:
 		request.session['openChatBoxes'] = None

	if request.session['openChatBoxes'] is None:
		request.session['openChatBoxes'] = []

	return HttpResponse("Mini chat for Django :)")

def chatHeartbeat(request):
	"""
	"""

	chats 	=	Chat.objects.filter( to=request.user, recd = 1 ).order_by('id')

	items = ""

	chatBoxes = []

	print request
	for chat in chats:
		items = request.session['openChatBoxes']
		# try:
		# 	request.session['openChatBoxes'][chat.message_from]
		# except Exception, e:
		# 	raise e
	print items


	items = { 'items': ['lala','lala']}
	return HttpResponse(json.dumps(items), mimetype="application/json")

def chatBoxSession():
	pass

def startChatSession():
	pass

def sendChat():
	pass

def closeChat():
	pass

def sanitize(text):
	text = cgi.escape(text, True)
	# text = htmlspecialchars(text, ENT_QUOTES);
	text = text.replace("\n\r","\n",text);
	text = text.replace("\r\n","\n",text);
	text = text.replace("\n","<br>",text);

	return text